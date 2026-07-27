#!/usr/bin/env python3
"""Test analyze_stock_news directly"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from app.routers.analyze import analyze_stock_news

print('测试 analyze_stock_news...')
result = analyze_stock_news(
    stock_code='01810',
    stock_name='小米集团',
    days=7,
    api_key='tp-cfabuhnfj62vmarb5ezr9nn2a6pd1owbux39236brle5x6xc',
    base_url='https://token-plan-cn.xiaomimimo.com/v1',
    model='mimo-v2.5-pro'
)

print(f'result keys: {result.keys()}')
print(f'analysis 长度: {len(result.get("analysis", ""))}')
print(f'news 数量: {len(result.get("news", []))}')
print(f'analysis 前200字符: {result.get("analysis", "")[:200]}')
