#!/usr/bin/env python3
"""
富途OpenD港股K线同步脚本
- 使用 Futu OpenD 获取历史K线
- 批量多线程同步
- 增量更新（只拉取数据库中最新日期之后的数据）
"""
import sys
sys.path.insert(0, r'C:\Users\34596\AppData\Local\Programs\Python\Python313\Lib\site-packages')
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

import psycopg2
import time
import threading
from queue import Queue
from futu import *

DB_CONFIG = {
    "host": "localhost", "port": 5432, "dbname": "hk_stock",
    "user": "postgres", "password": "pc20050218"
}

# 富途连接参数
FUTU_HOST = '127.0.0.1'
FUTU_PORT = 11111

# 并行线程数
NUM_THREADS = 5
BATCH_SIZE = 50  # 每批处理多少只股票

def get_all_stock_codes(conn):
    """获取所有股票代码"""
    cur = conn.cursor()
    cur.execute("SELECT stock_code FROM stock_info ORDER BY stock_code")
    codes = [f"HK.{r[0]}" for r in cur.fetchall()]
    cur.close()
    return codes

def get_latest_date(conn, stock_code):
    """获取某股票最新K线日期"""
    cur = conn.cursor()
    cur.execute("""
        SELECT trade_date FROM stock_kline 
        WHERE stock_code = %s AND period_type = 'D'
        ORDER BY trade_date DESC LIMIT 1
    """, (stock_code,))
    result = cur.fetchone()
    cur.close()
    return result[0] if result else None

def sync_stock_kline(quote_ctx, conn, stock_code_hk, stock_code_raw):
    """同步单只股票的K线数据"""
    cur = conn.cursor()
    
    try:
        # 获取数据库中最新日期
        latest = get_latest_date(conn, stock_code_raw)
        
        # 计算起始日期（最新日期后一天，或默认6个月前）
        if latest:
            from datetime import datetime, timedelta
            start_date = (datetime.strptime(str(latest), '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            start_date = "2025-01-01"
        
        end_date = "2026-04-21"
        
        # 如果起始日期在结束日期之后，跳过
        if start_date >= end_date:
            cur.close()
            return 0, 0
        
        ret, data, page_key = quote_ctx.request_history_kline(
            code=stock_code_hk,
            start=start_date,
            end=end_date,
            ktype=KLType.K_DAY,
            autype=AuType.QFQ
        )
        
        if ret != RET_OK:
            return 0, 1
        
        if data is None or data.empty:
            cur.close()
            return 0, 0
        
        # 写入数据库
        count = 0
        for _, row in data.iterrows():
            td = row['time_key'][:10]
            op = float(row['open'])
            cp = float(row['close'])
            hp = float(row['high'])
            lp = float(row['low'])
            vol = int(row['volume'])
            tov = float(row['turnover'])
            chg = float(row['change_rate'])
            
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
            """, (stock_code_raw, td, op, cp, hp, lp, vol, tov, chg))
            
            if cur.rowcount > 0:
                count += 1
        
        conn.commit()
        cur.close()
        return count, 0
        
    except Exception as e:
        conn.rollback()
        cur.close()
        return 0, 1

def worker(task_queue, result_queue, thread_id):
    """工作线程从队列取任务执行"""
    quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)
    
    while True:
        task = task_queue.get()
        if task is None:
            break
        
        batch = task
        batch_results = []
        
        for stock_code_hk in batch:
            stock_code_raw = stock_code_hk.replace("HK.", "")
            count, err = sync_stock_kline(quote_ctx, psycopg2.connect(**DB_CONFIG), stock_code_hk, stock_code_raw)
            batch_results.append((stock_code_raw, count, err))
        
        result_queue.put(batch_results)
        time.sleep(0.5)  # 避免频率过高
    
    quote_ctx.close()

def main():
    print("=" * 50)
    print("富途OpenD K线同步工具")
    print("=" * 50)
    
    conn = psycopg2.connect(**DB_CONFIG)
    
    # 获取所有股票
    all_codes = get_all_stock_codes(conn)
    print(f"待同步股票数量: {len(all_codes)}")
    
    # 分批
    batches = [all_codes[i:i+BATCH_SIZE] for i in range(0, len(all_codes), BATCH_SIZE)]
    print(f"分成 {len(batches)} 批，每批 {BATCH_SIZE} 只")
    
    conn.close()
    
    task_queue = Queue()
    result_queue = Queue()
    
    # 放入所有批次
    for batch in batches:
        task_queue.put(batch)
    
    # 启动工作线程
    threads = []
    for i in range(NUM_THREADS):
        t = threading.Thread(target=worker, args=(task_queue, result_queue, i))
        t.start()
        threads.append(t)
        task_queue.put(None)  # 发送终止信号
    
    # 收集结果
    total_done = 0
    total_new = 0
    total_fail = 0
    
    for _ in range(len(batches)):
        batch_results = result_queue.get()
        for code, count, err in batch_results:
            total_done += 1
            if err == 0:
                total_new += count
                if total_new % 500 == 0:
                    print(f"  进度: {total_done}/{len(all_codes)} (新增:{total_new})")
            else:
                total_fail += 1
                if total_fail <= 5:
                    print(f"  失败: {code}")
    
    for t in threads:
        t.join()
    
    print(f"\n完成! 成功: {total_done}, 失败: {total_fail}, 新增记录: {total_new}")

if __name__ == '__main__':
    main()