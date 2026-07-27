#!/usr/bin/env python3
"""
用腾讯财经API补全新股K线数据
API: https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get
"""
import os
os.environ['NO_PROXY'] = '*'

import requests
import psycopg2
import json
import time
import sys
from datetime import datetime, date

sys.stdout.reconfigure(encoding='utf-8')

DB_CONFIG = {
    "host": "localhost", "port": 5432, "dbname": "hk_stock",
    "user": "postgres", "password": "pc20050218"
}

QQFinance_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.qq.com/'
}

MAX_RETRIES = 3
REQUEST_DELAY = 2  # 每次请求休息2秒，避免触发限速


def get_kline_from_qq(code, count=100):
    """从腾讯财经获取港股日K线"""
    for attempt in range(MAX_RETRIES):
        try:
            url = f'https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get?_var=kline_dayhfq&param=hk{code},day,,,{count},qfq'
            resp = requests.get(url, headers=QQFinance_HEADERS, timeout=10)
            
            if resp.status_code != 200:
                return None, f"HTTP {resp.status_code}"
            
            text = resp.text
            if not text.startswith('kline_dayhfq='):
                return None, "Invalid response format"
            
            json_str = text[len('kline_dayhfq='):]
            data = json.loads(json_str)
            
            if data.get('code') != 0:
                return None, f"API error code: {data.get('code')}"
            
            stock_data = data.get('data', {}).get(f'hk{code}', {})
            day_data = stock_data.get('day', [])
            
            if not day_data:
                return None, "No day data"
            
            # 解析数据
            # 格式: [日期, 开, 收, 高, 低, 成交量, {}, 涨跌幅, 成交额, ?, ?]
            klines = []
            for item in day_data:
                if len(item) < 9:
                    continue
                try:
                    trade_date = datetime.strptime(item[0][:10], '%Y-%m-%d').date()
                    open_p = float(item[1])
                    close_p = float(item[2])
                    high_p = float(item[3])
                    low_p = float(item[4])
                    volume = int(float(item[5]))
                    turnover = float(item[8]) if item[8] else 0
                    change_pct = float(item[7]) if item[7] else 0
                    
                    klines.append({
                        'date': trade_date,
                        'open': open_p,
                        'close': close_p,
                        'high': high_p,
                        'low': low_p,
                        'volume': volume,
                        'turnover': turnover,
                        'change_pct': change_pct
                    })
                except Exception:
                    continue
            
            return klines, None
            
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(3)
                continue
            return None, str(e)
    
    return None, 'Max retries exceeded'


def sync_ipo_klines():
    """补全新股K线数据"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    # 获取所有缺失K线或K线不足5条的股票（包括IPO表里的新股）
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT COALESCE(si.stock_code, i.stock_code) as code, 
               COALESCE(si.stock_name, i.stock_name) as name,
               i.listing_date
        FROM stock_ipo i
        LEFT JOIN stock_info si ON i.stock_code = si.stock_code
        LEFT JOIN stock_kline sk ON i.stock_code = sk.stock_code AND sk.period_type = 'D'
        WHERE sk.stock_code IS NULL OR 
              (SELECT COUNT(*) FROM stock_kline WHERE stock_code = i.stock_code AND period_type = 'D') < 5
        ORDER BY i.listing_date DESC NULLS LAST
    """)
    stocks = cur.fetchall()
    cur.close()
    
    if not stocks:
        print("没有需要补全的新股K线")
        conn.close()
        return
    
    print(f"需要补全 {len(stocks)} 只股票的K线")
    
    success = 0
    failed = 0
    
    for code, name, listing_date in stocks:
        print(f"\n处理: {code} {name} (上市日: {listing_date})")
        
        klines, err = get_kline_from_qq(code, count=100)
        
        if err:
            print(f"  获取失败: {err}")
            failed += 1
            continue
        
        if not klines:
            print(f"  无K线数据")
            failed += 1
            continue
        
        print(f"  获取到 {len(klines)} 条K线")
        
        cur2 = conn.cursor()
        inserted = 0
        
        for kline in klines:
            try:
                cur2.execute("""
                    INSERT INTO stock_kline 
                    (stock_code, period_type, trade_date, open_price, close_price,
                     high_price, low_price, volume, turnover, change_percent, turnover_rate)
                    VALUES (%s, 'D', %s, %s, %s, %s, %s, %s, %s, %s, 0)
                    ON CONFLICT (stock_code, period_type, trade_date) DO UPDATE SET
                        open_price = EXCLUDED.open_price,
                        close_price = EXCLUDED.close_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        volume = EXCLUDED.volume,
                        turnover = EXCLUDED.turnover,
                        change_percent = EXCLUDED.change_percent
                """, (
                    code, kline['date'], kline['open'], kline['close'],
                    kline['high'], kline['low'], kline['volume'],
                    kline['turnover'], kline['change_pct']
                ))
                inserted += 1
            except Exception as e:
                pass
        
        conn.commit()
        cur2.close()
        
        print(f"  插入/更新 {inserted} 条K线")
        success += 1
        
        # 每次请求休息2秒
        time.sleep(REQUEST_DELAY)
    
    conn.close()
    print(f"\n=== 完成: 成功 {success}, 失败 {failed} ===")


if __name__ == '__main__':
    sync_ipo_klines()
