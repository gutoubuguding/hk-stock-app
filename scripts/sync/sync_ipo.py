#!/usr/bin/env python3
"""
从东方财富同步港股IPO数据到数据库
定时任务调用此脚本刷新新股数据
"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False

import psycopg2
import json
import time
from datetime import datetime

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "hk_stock",
    "user": "postgres",
    "password": "pc20050218"
}

def sync_ipo_data():
    """从东方财富获取并更新IPO数据"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://data.eastmoney.com/"
    }
    
    # 获取近一年的新股数据
    url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    params = {
        "sortColumns": "LISTING_DATE",
        "sortTypes": "-1",
        "pageSize": 500,
        "pageNumber": 1,
        "reportName": "RPT_IPO_HKAPPLY",
        "columns": "ALL",
        "quoteColumns": "",
        "filter": '(LISTING_DATE>="2025-01-01")'
    }
    
    print("从东方财富获取港股IPO数据...")
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    data = resp.json()
    
    if not data.get("result") or not data["result"].get("data"):
        print(f"获取失败: {data}")
        conn.close()
        return
    
    items = data["result"]["data"]
    print(f"获取到 {len(items)} 条IPO记录")
    
    updated = 0
    inserted = 0
    
    for item in items:
        try:
            stock_code = str(item.get("SECURITY_CODE", "")).strip()
            if not stock_code or len(stock_code) < 3:
                continue
            
            stock_name = item.get("SECURITY_NAME_ABBR", "") or item.get("COMPANY_NAME", "")
            listing_date = item.get("LISTING_DATE", "")
            if listing_date and "T" in str(listing_date):
                listing_date = str(listing_date)[:10]
            
            issue_price = item.get("ISSUE_PRICE")
            if issue_price:
                issue_price = float(issue_price)
            
            # 入场费
            entry_fee = item.get("APPLICATION_FEE") or item.get("ENTRY_FEE")
            if entry_fee:
                entry_fee = float(entry_fee)
            
            # 募资额
            fund_amount = item.get("RAISE_MONEY") or item.get("FUND_RAISING_AMOUNT")
            if fund_amount:
                fund_amount = float(fund_amount)
            
            # 超购倍数
            oversub_ratio = item.get("OVER_SUB_RATIO") or item.get("OVERALLOTMENT_RATIO")
            if oversub_ratio:
                oversub_ratio = float(oversub_ratio)
            
            # 公开发售/国际配售比例
            public_ratio = item.get("PUBLIC_OFFERING_RATIO")
            international_ratio = item.get("INTERNATIONAL_PLACEMENT_RATIO")
            
            # 中签率
            allotment_rate = item.get("ALLOTMENT_RATE")
            if allotment_rate:
                allotment_rate = float(allotment_rate)
            
            # 板块
            sector = item.get("INDUSTRY") or item.get("SECTOR", "")
            
            # 保荐人
            sponsor = item.get("SPONSOR") or item.get("ADVISOR", "")
            
            # 基石投资者
            cornerstone = item.get("CORNERSTONE_INVESTOR") or item.get("CORNERSTONE", "")
            
            # 发行PE
            issue_pe = item.get("ISSUE_PE")
            if issue_pe:
                issue_pe = float(issue_pe)
            
            # 行业PE
            industry_pe = item.get("INDUSTRY_PE")
            if industry_pe:
                industry_pe = float(industry_pe)
            
            # 招股开始/结束日期
            sub_start = item.get("APPLICATION_START_DATE", "")
            sub_end = item.get("APPLICATION_END_DATE", "")
            if sub_start and "T" in str(sub_start):
                sub_start = str(sub_start)[:10]
            if sub_end and "T" in str(sub_end):
                sub_end = str(sub_end)[:10]
            
            # 检查是否已存在
            cur.execute("SELECT id FROM stock_ipo WHERE stock_code = %s", (stock_code,))
            exists = cur.fetchone()
            
            if exists:
                # 更新
                cur.execute("""
                    UPDATE stock_ipo SET
                        stock_name = %s,
                        listing_date = %s,
                        issue_price = %s,
                        entry_fee = %s,
                        fundraising_amount = %s,
                        oversubscription_ratio = %s,
                        public_offering_ratio = %s,
                        international_placement_ratio = %s,
                        allotment_rate = %s,
                        sector = %s,
                        sponsor = %s,
                        cornerstone_investor = %s,
                        issue_pe = %s,
                        industry_avg_pe = %s,
                        subscription_start = %s,
                        subscription_end = %s
                    WHERE stock_code = %s
                """, (
                    stock_name, listing_date, issue_price, entry_fee,
                    fund_amount, oversub_ratio, public_ratio, international_ratio,
                    allotment_rate, sector, sponsor, cornerstone, issue_pe,
                    industry_pe, sub_start, sub_end, stock_code
                ))
                updated += 1
            else:
                # 新增
                cur.execute("""
                    INSERT INTO stock_ipo
                    (stock_code, stock_name, listing_date, issue_price, entry_fee,
                     fundraising_amount, oversubscription_ratio, public_offering_ratio,
                     international_placement_ratio, allotment_rate, sector, sponsor,
                     cornerstone_investor, issue_pe, industry_avg_pe,
                     subscription_start, subscription_end)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    stock_code, stock_name, listing_date, issue_price, entry_fee,
                    fund_amount, oversub_ratio, public_ratio, international_ratio,
                    allotment_rate, sector, sponsor, cornerstone, issue_pe,
                    industry_pe, sub_start, sub_end
                ))
                inserted += 1
            
            time.sleep(0.05)  # 避免请求过快
            
        except Exception as e:
            print(f"  处理记录失败: {e}")
            continue
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"IPO同步完成！新增: {inserted}, 更新: {updated}")


if __name__ == '__main__':
    sync_ipo_data()
