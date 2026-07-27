#!/usr/bin/env python3
"""将AASTOCKS原始板块映射到新的统一分类"""
import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# 新板块分类映射表
# key: AASTOCKS原始板块名称（部分匹配）
# value: 新的统一板块名称

SECTOR_MAP = {
    # === 半导体 ===
    '半导体': '半导体',
    '集成电路': '半导体',
    '芯片': '半导体',
    '半导体设备': '半导体',
    '半导体材料': '半导体',

    # === 创新药/生物医药 ===
    '生物医药': '创新药/生物医药',
    '生物科技': '创新药/生物医药',
    '创新药': '创新药/生物医药',
    '医药': '创新药/生物医药',
    '制药': '创新药/生物医药',
    '新药': '创新药/生物医药',
    '药物': '创新药/生物医药',
    '疫苗': '创新药/生物医药',
    '中药': '创新药/生物医药',

    # === AI/软件 ===
    '人工智能': 'AI/软件',
    'AI': 'AI/软件',
    'ChatGPT': 'AI/软件',
    '机器人': 'AI/软件',
    '软件': 'AI/软件',
    '信息技术': 'AI/软件',
    '信息科技': 'AI/软件',
    '互联网': 'AI/软件',
    '云计算': 'AI/软件',
    '大数据': 'AI/软件',
    '元宇宙': 'AI/软件',

    # === 新能源汽车 ===
    '新能源汽车': '新能源汽车',
    '新能源': '新能源汽车',
    '电动车': '新能源汽车',
    '电动汽车': '新能源汽车',
    '锂电池': '新能源汽车',
    '锂电': '新能源汽车',
    '电池': '新能源汽车',
    '汽车': '新能源汽车',
    '自动驾驶': '新能源汽车',
    '汽车电子': '新能源汽车',
    '汽车零部件': '新能源汽车',

    # === 消费电子 ===
    '消费电子': '消费电子',
    '电子': '消费电子',
    '电子设备': '消费电子',
    '电子元器件': '消费电子',
    '电子元件': '消费电子',
    '电子材料': '消费电子',
    '光学': '消费电子',
    '摄像头': '消费电子',
    '显示': '消费电子',
    '面板': '消费电子',

    # === 食品饮料 ===
    '食品': '食品饮料',
    '饮料': '食品饮料',
    '酒': '食品饮料',
    '酒类': '食品饮料',
    '乳业': '食品饮料',
    '餐饮': '食品饮料',
    '茶': '食品饮料',
    '调味品': '食品饮料',

    # === 工业制造 ===
    '工业': '工业制造',
    '机械': '工业制造',
    '装备': '工业制造',
    '制造': '工业制造',
    '设备': '工业制造',
    '装备制造': '工业制造',
    '高端装备': '工业制造',
    '军工': '工业制造',
    '航空航天': '工业制造',
    '航天': '工业制造',
    '航空': '工业制造',
    '轨道交通': '工业制造',
    '基建': '工业制造',
    '建筑': '工业制造',
    '建材': '工业制造',
    '工程机械': '工业制造',
    '电力': '工业制造',

    # === 新材料 ===
    '材料': '新材料',
    '化工': '新材料',
    '化学': '新材料',
    '新材料': '新材料',
    '稀土': '新材料',
    '碳纤维': '新材料',
    '石墨': '新材料',

    # === 医疗健康服务 ===
    '医疗': '医疗健康服务',
    '医疗设备': '医疗健康服务',
    '医疗服务': '医疗健康服务',
    '医疗器械': '医疗健康服务',
    '体外诊断': '医疗健康服务',
    '辅助生殖': '医疗健康服务',
    '齿科': '医疗健康服务',
    '眼科': '医疗健康服务',
    '医美': '医疗健康服务',

    # === 其他 ===
    'N/A': '其他',
    '其他': '其他',
    '综合': '其他',
    '集团': '其他',
}

def normalize_sector(raw_sector):
    """将原始板块名称映射为新分类"""
    if not raw_sector:
        return '其他'
    
    raw = raw_sector.strip()
    
    # 先精确匹配
    for key, value in SECTOR_MAP.items():
        if key in raw or raw in key:
            return value
    
    # 再模糊匹配关键词
    keywords_sectors = [
        (('半导体', '集成电路', '芯片'), '半导体'),
        (('医药', '制药', '生物', '新药', '疫苗', '中药'), '创新药/生物医药'),
        (('人工智能', 'AI', 'ChatGPT', '机器人', '软件', '信息', '互联网', '云计算', '大数据', '元宇宙'), 'AI/软件'),
        (('汽车', '电池', '新能源', '锂', '电动'), '新能源汽车'),
        (('电子', '光学', '显示', '面板'), '消费电子'),
        (('食品', '饮料', '酒', '餐饮'), '食品饮料'),
        (('工业', '机械', '装备', '设备', '制造', '电力'), '工业制造'),
        (('材料', '化工', '化学'), '新材料'),
        (('医疗', '医'), '医疗健康服务'),
    ]
    
    for keywords, sector in keywords_sectors:
        for kw in keywords:
            if kw in raw:
                return sector
    
    return '其他'

def main():
    # 获取所有唯一板块
    cur.execute("SELECT DISTINCT sector FROM stock_ipo WHERE sector IS NOT NULL")
    original_sectors = [row[0] for row in cur.fetchall()]
    
    print(f"发现 {len(original_sectors)} 个原始板块\n")
    
    # 显示映射关系
    mappings = {}
    for raw in original_sectors:
        new = normalize_sector(raw)
        if new not in mappings:
            mappings[new] = []
        mappings[new].append(raw)
    
    print("=== 板块映射关系 ===")
    for new_sector, originals in sorted(mappings.items()):
        print(f"\n【{new_sector}】")
        for o in originals:
            print(f"  {o}")
    
    # 更新数据库
    print("\n\n=== 更新数据库 ===")
    updated = 0
    for raw in original_sectors:
        new = normalize_sector(raw)
        cur.execute("""
            UPDATE stock_ipo 
            SET sector = %s, updated_at = NOW()
            WHERE sector = %s
        """, (new, raw))
        count = cur.rowcount
        updated += count
        print(f"  {raw} -> {new}: {count}条")
    
    conn.commit()
    print(f"\n更新完成，共 {updated} 条记录")

    # 验证
    cur.execute("""
        SELECT sector, COUNT(*) as cnt 
        FROM stock_ipo 
        WHERE listing_date >= '2025-01-01'
        GROUP BY sector 
        ORDER BY cnt DESC
    """)
    print("\n=== 更新后板块统计 ===")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}只")

if __name__ == '__main__':
    main()