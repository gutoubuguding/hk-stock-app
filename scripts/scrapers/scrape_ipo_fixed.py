#!/usr/bin/env python3
"""Scrape IPO data from AAStocks and save to database"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
from bs4 import BeautifulSoup
import psycopg2
import re

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'dbname': os.getenv('DB_NAME', 'hk_stock'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'pc20050218')
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def scrape_ipo_page(page_num):
    url = f'http://www.aastocks.com/sc/stocks/market/ipo/listedipo.aspx?s=3&o=0&page={page_num}'
    resp = requests.get(url, headers=headers, timeout=15)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    tables = soup.find_all('table')
    
    ipo_table = None
    for idx, table in enumerate(tables):
        rows = table.find_all('tr')
        if len(rows) > 5:
            first_row_text = ''.join([td.get_text(strip=True) for td in rows[0].find_all(['td', 'th'])])
            if 'HK' in first_row_text or '倍' in first_row_text:
                ipo_table = table
                break
    
    if not ipo_table:
        return []
    
    rows = ipo_table.find_all('tr')
    results = []
    
    for row in rows[1:]:
        cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
        if len(cells) < 10:
            continue
        
        code_match = re.search(r'(\d{5})\.HK', cells[1])
        if not code_match:
            continue
        
        stock_code = code_match.group(1)
        
        # Extract stock name (before the code)
        name_text = cells[1]
        name_match = re.search(r'^(.+?)[\d]', name_text)
        stock_name = name_match.group(1).strip() if name_match else ''
        
        # Extract listing date
        listing_date = cells[2].strip() if len(cells) > 2 else None
        
        # Extract allotment rate
        rate_text = cells[9] if len(cells) > 9 else ''
        rate_match = re.search(r'([\d.]+)%', rate_text)
        allotment_rate = float(rate_match.group(1)) if rate_match else None
        
        # Extract oversubscription ratio
        ratio_text = cells[7] if len(cells) > 7 else ''
        ratio_match = re.search(r'([\d.]+)', ratio_text)
        oversubscription_ratio = float(ratio_match.group(1)) if ratio_match else None
        
        # Extract entry fee
        entry_text = cells[8] if len(cells) > 8 else ''
        entry_match = re.search(r'([\d,.]+)', entry_text)
        entry_fee = float(entry_match.group(1).replace(',', '')) if entry_match else None
        
        # Extract issue price
        price_text = cells[5] if len(cells) > 5 else ''
        price_match = re.search(r'([\d.]+)', price_text)
        issue_price = float(price_match.group(1)) if price_match else None
        
        # Extract first day change
        change_text = cells[11] if len(cells) > 11 else ''
        change_match = re.search(r'([+-]?[\d.]+)%', change_text)
        first_day_change = float(change_match.group(1)) if change_match else None
        
        results.append({
            'stock_code': stock_code,
            'stock_name': stock_name,
            'listing_date': listing_date,
            'allotment_rate': allotment_rate,
            'oversubscription_ratio': oversubscription_ratio,
            'entry_fee': entry_fee,
            'issue_price': issue_price,
            'first_day_change': first_day_change,
        })
    
    return results

def update_database(records):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    updated = 0
    for rec in records:
        try:
            cur.execute("""
                INSERT INTO stock_ipo (stock_code, stock_name, listing_date, allotment_rate, oversubscription_ratio, entry_fee, issue_price, first_day_change)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (stock_code) DO UPDATE SET
                    stock_name = COALESCE(EXCLUDED.stock_name, stock_ipo.stock_name),
                    listing_date = COALESCE(EXCLUDED.listing_date, stock_ipo.listing_date),
                    allotment_rate = COALESCE(EXCLUDED.allotment_rate, stock_ipo.allotment_rate),
                    oversubscription_ratio = COALESCE(EXCLUDED.oversubscription_ratio, stock_ipo.oversubscription_ratio),
                    entry_fee = COALESCE(EXCLUDED.entry_fee, stock_ipo.entry_fee),
                    issue_price = COALESCE(EXCLUDED.issue_price, stock_ipo.issue_price),
                    first_day_change = COALESCE(EXCLUDED.first_day_change, stock_ipo.first_day_change)
            """, (
                rec['stock_code'], rec['stock_name'], rec['listing_date'],
                rec['allotment_rate'], rec['oversubscription_ratio'],
                rec['entry_fee'], rec['issue_price'], rec['first_day_change']
            ))
            updated += 1
        except Exception as e:
            print(f"Error updating {rec['stock_code']}: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    return updated

print("Starting HK IPO scrape...")

all_records = []
for page in range(1, 6):  # Scrape 5 pages
    print(f"Page {page}...")
    records = scrape_ipo_page(page)
    print(f"  Found {len(records)} records")
    all_records.extend(records)
    
    if len(records) < 20:
        break

print(f"\nTotal records scraped: {len(all_records)}")

if all_records:
    updated = update_database(all_records)
    print(f"Updated {updated} records in database")
