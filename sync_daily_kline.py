"""
港股日K线数据同步脚本
- 同步 stock_info 和 stock_ipo 表中所有股票的日K数据
- 带重试机制和速率限制保护
"""
import os
os.environ['NO_PROXY'] = '*'

import psycopg2
import akshare as ak
import requests
import json
import time
import sys
import subprocess
from datetime import datetime, date

sys.stdout.reconfigure(encoding='utf-8')

# 数据库连接从环境变量读取，避免把本机密码提交到 GitHub。
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "hk_stock"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "")
}

QQ_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.qq.com/'
}

MAX_RETRIES = 3
RETRY_DELAY = 10  # 秒


def sync_via_qqfinance(code, conn, backfill=False):
    """通过腾讯财经API获取K线（akshare备用源）"""
    cur = conn.cursor()
    
    # 获取已有数据的最新日期
    cur.execute("""
        SELECT MAX(trade_date) FROM stock_kline 
        WHERE stock_code = %s AND period_type = 'D'
    """, (code,))
    result = cur.fetchone()
    last_date = result[0] if result and result[0] else None
    
    # 获取最多100条
    try:
        url = f'https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get?_var=kline_dayhfq&param=hk{code},day,,,{100},qfq'
        resp = requests.get(url, headers=QQ_HEADERS, timeout=10)
        
        if resp.status_code != 200:
            cur.close()
            return False, f"HTTP {resp.status_code}"
        
        text = resp.text
        if not text.startswith('kline_dayhfq='):
            cur.close()
            return False, "Invalid response"
        
        json_str = text[len('kline_dayhfq='):]
        data = json.loads(json_str)
        
        if data.get('code') != 0:
            cur.close()
            return False, f"API error {data.get('code')}"
        
        stock_data = data.get('data', {}).get(f'hk{code}', {})
        day_data = stock_data.get('qfqday') or stock_data.get('day', [])
        
        if not day_data:
            cur.close()
            return True, 0  # 无数据不算失败
        
        count = 0
        for item in day_data:
            if len(item) < 9:
                continue
            try:
                trade_date = datetime.strptime(item[0][:10], '%Y-%m-%d').date()
                
                # 增量模式：跳过已有日期
                if not backfill and last_date and trade_date <= last_date:
                    continue
                
                open_p = float(item[1])
                close_p = float(item[2])
                high_p = float(item[3])
                low_p = float(item[4])
                volume = int(float(item[5]))
                turnover = float(item[8]) if item[8] else 0
                change_pct = float(item[7]) if item[7] else 0
                
                cur.execute("""
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
                """, (code, trade_date, open_p, close_p, high_p, low_p, volume, turnover, change_pct))
                count += 1
                
            except Exception:
                continue
        
        conn.commit()
        cur.close()
        return True, count
        
    except Exception as e:
        cur.close()
        return False, str(e)


def sync_via_akshare(code, conn, backfill=False):
    """通过akshare获取K线（主数据源）"""
    for attempt in range(MAX_RETRIES):
        cur = conn.cursor()
        
        if backfill:
            start_date = '20240101'
        else:
            cur.execute("""
                SELECT MAX(trade_date) FROM stock_kline 
                WHERE stock_code = %s AND period_type = 'D'
            """, (code,))
            result = cur.fetchone()
            last_date = result[0] if result and result[0] else None
            start_date = last_date.strftime('%Y%m%d') if last_date else '20250101'
        
        end_date = datetime.now().strftime('%Y%m%d')
        
        try:
            df = ak.stock_hk_hist(
                symbol=code, 
                period="daily", 
                start_date=start_date, 
                end_date=end_date, 
                adjust=""
            )
            
            if df is None or df.empty:
                cur.close()
                return True, 0
            
            count = 0
            for _, row in df.iterrows():
                try:
                    td = row.iloc[0]
                    if isinstance(td, str):
                        td = datetime.strptime(td[:10], '%Y-%m-%d').date()
                    
                    if not backfill:
                        cur.execute("""
                            SELECT 1 FROM stock_kline 
                            WHERE stock_code = %s AND period_type = 'D' AND trade_date = %s
                        """, (code, td))
                        if cur.fetchone():
                            continue
                    
                    op = float(row.iloc[1])
                    cp = float(row.iloc[2])
                    hp = float(row.iloc[3])
                    lp = float(row.iloc[4])
                    vol = int(row.iloc[5])
                    tov = float(row.iloc[6])
                    chg = float(row.iloc[8]) if len(row) > 8 else 0
                    
                    cur.execute("""
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
                    """, (code, td, op, cp, hp, lp, vol, tov, chg))
                    count += 1
                    
                except Exception:
                    pass
            
            conn.commit()
            cur.close()
            return True, count
            
        except Exception as e:
            conn.rollback()
            cur.close()
            err_msg = str(e)
            
            if 'aborted' in err_msg.lower() or 'timeout' in err_msg.lower() or 'reset' in err_msg.lower():
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
            return False, err_msg
    
    return False, '重试次数用尽'


def sync_daily_kline_with_retry(code, conn, backfill=False):
    """同步单只股票的日K线，优先akshare，失败则用腾讯财经备用"""
    # 先试akshare
    success, result = sync_via_akshare(code, conn, backfill)
    if success:
        return success, result
    
    # akshare失败，用腾讯财经备用
    print(f'  {code} akshare失败({result})，切换腾讯财经备用...')
    return sync_via_qqfinance(code, conn, backfill)


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    
    # 1. 获取 stock_info 中已有K线但过期的股票（增量同步）
    cur = conn.cursor()
    cur.execute("""
        SELECT si.stock_code
        FROM stock_info si
        INNER JOIN (
            SELECT stock_code, MAX(trade_date) as last_date
            FROM stock_kline 
            WHERE period_type = 'D'
            GROUP BY stock_code
            HAVING MAX(trade_date) < CURRENT_DATE - INTERVAL '3 days'
        ) sk ON si.stock_code = sk.stock_code
    """)
    stale_stocks = [r[0] for r in cur.fetchall()]
    
    # 2. 获取 stock_info 中完全没有K线的股票（全量回补）
    cur.execute("""
        SELECT si.stock_code
        FROM stock_info si
        LEFT JOIN stock_kline sk ON si.stock_code = sk.stock_code AND sk.period_type = 'D'
        WHERE sk.stock_code IS NULL
    """)
    no_kline_stocks = [r[0] for r in cur.fetchall()]
    
    # 3. 获取 stock_ipo 里需要补K线或补首日/7日/30日指标的新股
    #    关键修复：即便已经有几条K线，只要7/30日指标到期但为空，也要继续同步并在末尾回填指标。
    cur.execute("""
        SELECT DISTINCT i.stock_code
        FROM stock_ipo i
        LEFT JOIN (
            SELECT stock_code, COUNT(*) AS k_count, MAX(trade_date) AS last_date
            FROM stock_kline
            WHERE period_type = 'D'
            GROUP BY stock_code
        ) sk ON sk.stock_code = i.stock_code
        WHERE i.listing_date IS NOT NULL
          AND i.listing_date <= CURRENT_DATE
          AND (
              sk.stock_code IS NULL
              OR sk.k_count < 30
              OR sk.last_date < CURRENT_DATE - INTERVAL '3 days'
              OR (i.issue_price IS NOT NULL AND i.first_day_change IS NULL)
              OR (i.issue_price IS NOT NULL AND i.listing_date <= CURRENT_DATE - INTERVAL '7 days' AND i.seven_day_change IS NULL)
              OR (i.issue_price IS NOT NULL AND i.listing_date <= CURRENT_DATE - INTERVAL '30 days' AND i.thirty_day_change IS NULL)
          )
    """)
    ipo_need_sync = [r[0] for r in cur.fetchall()]
    cur.close()
    
    # 合并：去重
    all_backfill = list(set(no_kline_stocks + ipo_need_sync))
    
    print(f'增量同步股票: {len(stale_stocks)} 只')
    print(f'全量/指标回补股票: {len(all_backfill)} 只（包括 {len(ipo_need_sync)} 只新股）')
    print(f'开始同步...')
    
    # 先处理全量回补（新股优先）
    print(f'\n=== 阶段1: 全量回补 {len(all_backfill)} 只股票 ===')
    ok_backfill = 0
    fail_backfill = 0
    total_new = 0
    
    for i, code in enumerate(all_backfill):
        success, result = sync_daily_kline_with_retry(code, conn, backfill=True)
        if success:
            ok_backfill += 1
            total_new += result
            if result > 0:
                print(f'  {code}: {result} 条新K线')
        else:
            fail_backfill += 1
            if fail_backfill <= 3:
                print(f'  {code} 失败: {result}')
        
        if (i + 1) % 20 == 0:
            print(f'  进度: {i+1}/{len(all_backfill)} (成功:{ok_backfill} 失败:{fail_backfill})')
            time.sleep(2)
        
        time.sleep(1)
    
    # 再处理增量同步
    print(f'\n=== 阶段2: 增量同步 {len(stale_stocks)} 只股票 ===')
    ok_incr = 0
    fail_incr = 0
    
    for i, code in enumerate(stale_stocks):
        success, result = sync_daily_kline_with_retry(code, conn, backfill=False)
        if success:
            ok_incr += 1
            total_new += result
        else:
            fail_incr += 1
            if fail_incr <= 3:
                print(f'  {code} 失败: {result}')
        
        if (i + 1) % 50 == 0:
            print(f'  进度: {i+1}/{len(stale_stocks)} (成功:{ok_incr} 失败:{fail_incr})')
            time.sleep(1)
        
        time.sleep(0.5)
    
    conn.close()
    print(f'\n=== 完成 ===')
    print(f'全量回补: 成功:{ok_backfill} 失败:{fail_backfill}')
    print(f'增量同步: 成功:{ok_incr} 失败:{fail_incr}')
    print(f'新增K线: {total_new} 条')

    # K线同步完成后，自动回填 IPO 首日/7日/30日涨跌幅，供新股对比表和板块统计使用。
    print('\n=== 阶段3: 回填IPO首日/7日/30日涨跌幅 ===')
    try:
        result = subprocess.run(
            [sys.executable, 'update_ipo_metrics.py'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            timeout=600,
            encoding='utf-8',
            errors='replace'
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        if result.returncode != 0:
            print(f'IPO指标回填失败，退出码: {result.returncode}')
    except Exception as e:
        print(f'IPO指标回填异常: {e}')


if __name__ == '__main__':
    main()
