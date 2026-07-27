#!/usr/bin/env python3
"""测试没有K线的股票"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from futu import OpenQuoteContext, RET_OK, KLType
import os

FUTU_HOST = os.getenv('FUTU_OPEND_HOST', 'host.docker.internal')
FUTU_PORT = int(os.getenv('FUTU_OPEND_PORT', '11111'))

quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)

# 测试没有K线的股票
test_stocks = ['00200', '00201', '00202', '00204']
for code in test_stocks:
    futu_code = f'HK.{code}'
    ret, data, err = quote_ctx.request_history_kline(futu_code, ktype=KLType.K_DAY, max_count=5)
    data_len = len(data) if data is not None else 0
    print(f'{code}: ret={ret}, data={data_len}, err={err}')

quote_ctx.close()
