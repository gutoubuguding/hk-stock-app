#!/usr/bin/env python3
"""
港股IPO数据同步脚本
使用 Futu OpenD Python API 获取即将上市的港股新股数据
定时任务调用此脚本刷新新股数据
"""
import sys
import os
os.environ['NO_PROXY'] = '*'

from futu import *
import psycopg2
from datetime import datetime

# 数据库和 Futu OpenD 连接信息从环境变量读取，避免提交本机密码/端口配置。
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "hk_stock"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "")
}

FUTU_HOST = os.getenv("FUTU_OPEND_HOST", "127.0.0.1")
FUTU_PORT = int(os.getenv("FUTU_OPEND_PORT", "11111"))


def sync_ipo_data():
    """从Futu OpenD获取港股IPO数据并写入数据库"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("连接 Futu OpenD...")
    quote_ctx = None
    try:
        quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)
        quote_ctx.set_sync_query_connect_timeout(10)
        
        print("请求港股IPO列表...")
        ret, df = quote_ctx.get_ipo_list(market=Market.HK)
        
        if ret != 0:
            print(f"Futu API返回错误: {ret}")
            return
        
        if df is None or df.empty:
            print("Futu未返回IPO数据")
            return
        
        print(f"获取到 {len(df)} 条IPO记录")
        
        updated = 0
        inserted = 0
        
        for _, row in df.iterrows():
            try:
                stock_code = str(row.get('code', '')).strip()
                if not stock_code or stock_code == 'N/A':
                    continue
                
                # 清理股票代码格式 (Futu返回的是 "HK.XXXXX" 格式)
                if stock_code.startswith('HK.'):
                    stock_code = stock_code[3:]  # 去掉 "HK." 前缀
                
                stock_name = str(row.get('name', '')).strip()
                if stock_name == 'N/A':
                    stock_name = ''
                
                # 招股时间
                apply_time = row.get('apply_time', '')
                if apply_time == 'N/A':
                    apply_time = None
                
                # 上市时间
                list_time = row.get('list_time', '')
                list_date = None
                if list_time and list_time != 'N/A':
                    try:
                        list_date = datetime.strptime(list_time[:10], '%Y-%m-%d').date()
                    except:
                        list_date = None
                
                # 发行价
                ipo_price = row.get('ipo_price', None)
                if ipo_price == 'N/A' or ipo_price is None:
                    ipo_price = None
                else:
                    try:
                        ipo_price = float(ipo_price)
                    except:
                        ipo_price = None
                
                # 募资额
                issue_size = row.get('issue_size', None)
                if issue_size == 'N/A' or issue_size is None:
                    issue_size = None
                else:
                    try:
                        issue_size = float(issue_size) * 1000000  # Futu单位是百万
                    except:
                        issue_size = None
                
                # 入场费
                entrance_price = row.get('entrance_price', None)
                if entrance_price == 'N/A' or entrance_price is None:
                    entrance_price = None
                else:
                    try:
                        entrance_price = float(entrance_price)
                    except:
                        entrance_price = None
                
                # 中签率
                winning_ratio = row.get('winning_ratio', None)
                if winning_ratio == 'N/A' or winning_ratio is None:
                    winning_ratio = None
                else:
                    try:
                        winning_ratio = float(winning_ratio)
                    except:
                        winning_ratio = None
                
                # 超购倍数 (online_issue_size / issue_size ratio)
                online_issue_size = row.get('online_issue_size', None)
                oversub_ratio = None
                if online_issue_size not in (None, 'N/A') and issue_size not in (None, 0):
                    try:
                        oversub_ratio = float(online_issue_size) / issue_size * 100 if issue_size else None
                    except:
                        oversub_ratio = None
                
                # 招股结束时间
                apply_end_time = row.get('apply_end_time', '')
                if apply_end_time == 'N/A':
                    apply_end_time = None
                
                # 保荐人/基石投资者 - Futu没有这些字段，留空
                sponsor = None
                cornerstone = None
                
                # 检查是否已存在
                cur.execute("SELECT id FROM stock_ipo WHERE stock_code = %s", (stock_code,))
                exists = cur.fetchone()
                
                if exists:
                    cur.execute("""
                        UPDATE stock_ipo SET
                            stock_name = %s,
                            listing_date = %s,
                            issue_price = %s,
                            entry_fee = %s,
                            fundraising_amount = %s,
                            oversubscription_ratio = %s,
                            allotment_rate = %s,
                            sponsor = %s,
                            cornerstone_investor = %s,
                            subscription_start = %s,
                            subscription_end = %s
                        WHERE stock_code = %s
                    """, (
                        stock_name, list_date, ipo_price, entrance_price,
                        issue_size, oversub_ratio, winning_ratio,
                        sponsor, cornerstone, apply_time, apply_end_time,
                        stock_code
                    ))
                    updated += 1
                else:
                    cur.execute("""
                        INSERT INTO stock_ipo
                        (stock_code, stock_name, listing_date, issue_price, entry_fee,
                         fundraising_amount, oversubscription_ratio, allotment_rate,
                         sponsor, cornerstone_investor, subscription_start, subscription_end)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        stock_code, stock_name, list_date, ipo_price, entrance_price,
                        issue_size, oversub_ratio, winning_ratio,
                        sponsor, cornerstone, apply_time, apply_end_time
                    ))
                    inserted += 1
                
                print(f"  处理: {stock_code} {stock_name} (上市日: {list_date})")
                
            except Exception as e:
                print(f"  处理记录失败: {e}")
                continue
        
        conn.commit()
        print(f"\nIPO同步完成！新增: {inserted}, 更新: {updated}")
        
    except Exception as e:
        print(f"Futu连接失败: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if quote_ctx:
            quote_ctx.close()
    
    cur.close()
    conn.close()


if __name__ == '__main__':
    sync_ipo_data()
