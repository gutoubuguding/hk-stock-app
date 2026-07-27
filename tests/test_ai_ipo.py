#!/usr/bin/env python3
"""Test AI service IPO analysis"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import httpx

url = 'http://localhost:8082/api/analyze/ipo'
params = {
    'stock_code': '03308',
    'stock_name': '中际旭创',
    'api_key': 'tp-cfabuhnfj62vmarb5ezr9nn2a6pd1owbux39236brle5x6xc',
    'base_url': 'https://token-plan-cn.xiaomimimo.com/v1',
    'model': 'mimo-v2.5-pro'
}

print('Testing AI service...')
with httpx.Client(timeout=300) as client:
    resp = client.get(url, params=params)
    data = resp.json()
    print(f'Status: {resp.status_code}')
    analysis = data.get('analysis', {})
    print(f'Analysis type: {type(analysis).__name__}')
    if isinstance(analysis, dict):
        print(f'Analysis keys: {list(analysis.keys())}')
        print(f'Summary: {analysis.get("summary", "EMPTY")[:100]}...')
        print(f'Suggestion: {analysis.get("suggestion", "EMPTY")}')
    else:
        print(f'Analysis is not a dict: {analysis}')
