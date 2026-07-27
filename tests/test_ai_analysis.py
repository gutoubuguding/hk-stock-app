#!/usr/bin/env python3
"""Test AI analysis"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import httpx

url = 'http://localhost:8082/api/analyze/stock-news'
params = {
    'stock_code': '01810',
    'stock_name': '小米集团',
    'days': 7,
    'api_key': 'tp-cfabuhnfj62vmarb5ezr9nn2a6pd1owbux39236brle5x6xc',
    'base_url': 'https://token-plan-cn.xiaomimimo.com/v1',
    'model': 'mimo-v2.5-pro'
}

print('请求 AI 分析...')
with httpx.Client(timeout=300) as client:
    resp = client.get(url, params=params)
    data = resp.json()
    print(f'状态码: {resp.status_code}')
    analysis = data.get('data', {}).get('analysis', '')
    print(f'analysis 长度: {len(analysis)}')
    print(f'analysis 前200字符: {analysis[:200]}')
