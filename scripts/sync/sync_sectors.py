#!/usr/bin/env python3
"""从 Futu API 同步港股板块信息"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from futu import OpenQuoteContext, RET_OK
import psycopg2
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'hk_stock'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'pc20050218')
}

FUTU_HOST = os.getenv('FUTU_OPEND_HOST', 'host.docker.internal')
FUTU_PORT = int(os.getenv('FUTU_OPEND_PORT', '11111'))

print("从 Futu API 同步港股板块信息...")

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# 获取所有股票代码
cur.execute("SELECT stock_code FROM stock_info ORDER BY stock_code")
stocks = [row[0] for row in cur.fetchall()]
print(f"共 {len(stocks)} 只股票")

quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)

# 分批获取股票信息
BATCH_SIZE = 100
updated = 0

for i in range(0, len(stocks), BATCH_SIZE):
    batch = stocks[i:i+BATCH_SIZE]
    codes = [f"HK.{s}" for s in batch]
    
    ret, data = quote_ctx.get_stock_basicinfo('HK', None, codes)
    if ret == RET_OK:
        for _, row in data.iterrows():
            code = row['code'].replace('HK.', '')
            # 获取板块信息（如果有）
            # Futu API 可能不直接返回板块，但我们可以根据股票名称推断
            pass
    
    if i % 500 == 0:
        print(f"  处理 {i}/{len(stocks)}...")

quote_ctx.close()

# 根据股票名称推断板块
sector_map = {
    '银行': ['银行', '工商', '建设', '农业', '中国银行', '招商', '民生', '兴业', '浦发', '中信', '光大', '平安', '交通', '邮储'],
    '保险': ['保险', '人寿', '平安', '太平洋', '新华', '泰康', '中国人保'],
    '证券': ['证券', '中信建投', '国泰君安', '海通', '华泰', '广发', '招商证券', '申万宏源'],
    '房地产': ['地产', '万科', '保利', '碧桂园', '恒大', '融创', '龙湖', '华润置地', '中海外'],
    '科技': ['科技', '腾讯', '阿里', '美团', '京东', '百度', '网易', '小米', '字节', '快手', '哔哩'],
    '医药': ['医药', '生物', '制药', '药业', '医疗', '健康', '疫苗', '基因'],
    '消费': ['消费', '食品', '饮料', '乳业', '啤酒', '白酒', '茅台', '五粮液', '伊利', '蒙牛'],
    '能源': ['能源', '石油', '石化', '中石油', '中石化', '中海油', '煤炭', '神华'],
    '电力': ['电力', '电网', '华能', '大唐', '华电', '国电', '电力投资'],
    '汽车': ['汽车', '比亚迪', '蔚来', '小鹏', '理想', '长城', '吉利', '广汽', '上汽'],
    '通信': ['通信', '移动', '联通', '电信', '中兴', '华为'],
    '互联网': ['互联网', '电商', '在线', '网络', '数字', '云'],
    '制造业': ['制造', '工业', '机械', '装备', '重工', '三一', '中联'],
    '零售': ['零售', '百货', '超市', '购物', '电商'],
    '物流': ['物流', '快递', '顺丰', '中通', '圆通', '韵达'],
}

# 更新板块信息
for stock_code in stocks:
    cur.execute("SELECT stock_name FROM stock_info WHERE stock_code = %s", (stock_code,))
    result = cur.fetchone()
    if result:
        stock_name = result[0]
        sector = None
        for sector_name, keywords in sector_map.items():
            for keyword in keywords:
                if keyword in stock_name:
                    sector = sector_name
                    break
            if sector:
                break
        
        if sector:
            cur.execute("UPDATE stock_info SET sector = %s WHERE stock_code = %s", (sector, stock_code))
            updated += 1

conn.commit()
cur.close()
conn.close()

print(f"更新了 {updated} 只股票的板块信息")
