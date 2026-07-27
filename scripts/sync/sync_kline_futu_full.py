#!/usr/bin/env python3
"""
富途OpenD港股K线同步脚本 - 多线程版
增量同步：只拉取数据库中最新日期之后的数据
"""
import sys
sys.path.insert(0, r'C:\Users\34596\AppData\Local\Programs\Python\Python313\Lib\site-packages')
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

import psycopg2
import time
import threading
from queue import Queue
from datetime import datetime, timedelta
from futu import *

DB_CONFIG = {
    "host": "localhost", "port": 5432, "dbname": "hk_stock",
    "user": "postgres", "password": "pc20050218"
}

FUTU_HOST = '127.0.0.1'
FUTU_PORT = 11111
NUM_THREADS = 4

# 全局统计
stats_lock = threading.Lock()
stats = {"done": 0, "new": 0, "fail": 0, "skip": 0}

def get_all_stock_codes():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT stock_code FROM stock_info ORDER BY stock_code")
    codes = [f"HK.{r[0]}" for r in cur.fetchall()]
    cur.close()
    conn.close()
    return codes

def get_latest_date(stock_code_raw):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT trade_date FROM stock_kline 
        WHERE stock_code = %s AND period_type = 'D'
        ORDER BY trade_date DESC LIMIT 1
    """, (stock_code_raw,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else None

def calc_date_range(stock_code_raw):
    latest = get_latest_date(stock_code_raw)
    if latest:
        start_date = (datetime.strptime(str(latest), '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        start_date = "2025-01-01"
    end_date = "2026-04-21"
    return start_date, end_date

def sync_one(quote_ctx, stock_code_hk, stock_code_raw):
    start_date, end_date = calc_date_range(stock_code_raw)
    
    if start_date >= end_date:
        return "skip"
    
    try:
        ret, data, page_key = quote_ctx.request_history_kline(
            code=stock_code_hk,
            start=start_date,
            end=end_date,
            ktype=KLType.K_DAY,
            autype=AuType.QFQ
        )
        
        if ret != RET_OK:
            return "fail"
        
        if data is None or data.empty:
            return "skip"
        
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        count = 0
        
        for _, row in data.iterrows():
            td = row['time_key'][:10]
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
            """, (stock_code_raw, td, float(row['open']), float(row['close']),
                  float(row['high']), float(row['low']), int(row['volume']),
                  float(row['turnover']), float(row['change_rate'])))
            if cur.rowcount > 0:
                count += 1
        
        conn.commit()
        cur.close()
        conn.close()
        return count
        
    except Exception as e:
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return "fail"

def worker(worker_id, task_queue):
    quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)
    
    while True:
        task = task_queue.get()
        if task is None:
            break
        
        code_hk, code_raw = task
        
        result = sync_one(quote_ctx, code_hk, code_raw)
        
        with stats_lock:
            stats["done"] += 1
            if result == "skip":
                stats["skip"] += 1
            elif result == "fail":
                stats["fail"] += 1
            else:
                stats["new"] += result
            
            done = stats["done"]
            if stats["done"] % 200 == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 已处理 {done} 只股票 (新增:{stats['new']} 失败:{stats['fail']} 跳过:{stats['skip']})")
        
        time.sleep(0.3)
    
    quote_ctx.close()

def main():
    print("=" * 60)
    print("富途OpenD 全量K线同步")
    print(f"并行线程: {NUM_THREADS}")
    print("=" * 60)
    
    all_codes = get_all_stock_codes()
    print(f"股票总数: {len(all_codes)}")
    print("开始时间: ", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("-" * 60)
    
    task_queue = Queue()
    for code_hk in all_codes:
        code_raw = code_hk.replace("HK.", "")
        task_queue.put((code_hk, code_raw))
    
    # 启动工作线程
    threads = []
    for i in range(NUM_THREADS):
        t = threading.Thread(target=worker, args=(i, task_queue))
        t.start()
        threads.append(t)
        task_queue.put(None)
    
    # 等待完成
    for t in threads:
        t.join()
    
    print("-" * 60)
    print(f"完成! 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"成功: {stats['done'] - stats['fail']} 只")
    print(f"失败: {stats['fail']} 只")
    print(f"跳过: {stats['skip']} 只 (已有最新数据)")
    print(f"新增记录: {stats['new']} 条")

if __name__ == '__main__':
    main()