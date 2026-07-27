#!/usr/bin/env python3
"""Test call_llm directly"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from app.routers.analyze import call_llm

api_key = 'tp-cfabuhnfj62vmarb5ezr9nn2a6pd1owbux39236brle5x6xc'
base_url = 'https://token-plan-cn.xiaomimimo.com/v1'
model = 'mimo-v2.5-pro'

print(f'api_key: {api_key}')
print(f'api_key 长度: {len(api_key)}')
print(f'api_key 是否为空: {not api_key or api_key.strip() == ""}')

result = call_llm('你好', api_key, base_url, model)
print(f'结果长度: {len(result)}')
print(f'结果: {result[:200]}')
