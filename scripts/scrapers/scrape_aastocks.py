#!/usr/bin/env python3
"""从阿斯达克获取港股IPO数据"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False
import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# 阿斯达克IPO列表页面
url = "https://www.aastocks.com/tc/ipo/ipoList.aspx"

try:
    resp = requests.get(url, headers=headers, timeout=15)
    resp.encoding = 'utf-8'
    html = resp.text
    
    print(f"Status: {resp.status_code}")
    print(f"Content length: {len(html)}")
    
    # 查找港股IPO代码 (通常是4-5位数字)
    # 查找表格中的股票信息
    
    # 保存到文件以便分析
    with open("aastocks_ipo.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("Saved to aastocks_ipo.html")
    
    # 尝试提取股票代码和名称
    # 港股代码通常是5位数字，如 09999, 09888
    code_pattern = r'(?:>|")(\d{4,5})(?:<|")'
    codes = re.findall(code_pattern, html)
    unique_codes = list(set(codes))
    print(f"Found {len(unique_codes)} unique codes: {unique_codes[:20]}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
