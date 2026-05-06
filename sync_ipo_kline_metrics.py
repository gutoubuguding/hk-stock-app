#!/usr/bin/env python3
"""只针对 IPO 指标需要的数据同步K线，并回填首日/7日/30日涨跌幅。"""
import os
os.environ['NO_PROXY'] = '*'
import sys
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import time
import psycopg2
import subprocess
from sync_daily_kline import DB_CONFIG, sync_daily_kline_with_retry


def sync_ipo_detail_before_metrics():
    """先补 IPO 详情，尤其是发行价；否则后面的涨跌幅计算会跳过这些股票。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    detail_script = os.path.join(script_dir, 'sync_ipo_detail_aastocks.py')
    if not os.path.exists(detail_script):
        print('未找到 sync_ipo_detail_aastocks.py，跳过 IPO 详情补全')
        return

    print('开始补全 IPO 发行价/详情...')
    result = subprocess.run(
        [sys.executable, detail_script],
        cwd=script_dir,
        text=True,
        capture_output=True,
        encoding='utf-8',
        errors='replace',
        timeout=900,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        print(f'IPO详情补全脚本退出码: {result.returncode}，继续尝试已有数据的K线/指标同步')


def main():
    sync_ipo_detail_before_metrics()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT i.stock_code
        FROM stock_ipo i
        LEFT JOIN (
            SELECT stock_code, COUNT(*) AS k_count, MAX(trade_date) AS last_date
            FROM stock_kline
            WHERE period_type = 'D'
            GROUP BY stock_code
        ) sk ON sk.stock_code = i.stock_code
        WHERE i.listing_date IS NOT NULL
          AND i.listing_date <= CURRENT_DATE
          AND i.issue_price IS NOT NULL
          AND i.issue_price > 0
          AND (
              sk.stock_code IS NULL
              OR sk.k_count < 30
              OR sk.last_date < CURRENT_DATE - INTERVAL '3 days'
              OR i.first_day_change IS NULL
              OR (i.listing_date <= CURRENT_DATE - INTERVAL '7 days' AND i.seven_day_change IS NULL)
              OR (i.listing_date <= CURRENT_DATE - INTERVAL '30 days' AND i.thirty_day_change IS NULL)
          )
        ORDER BY i.stock_code
    """)
    codes = [r[0] for r in cur.fetchall()]
    cur.close()

    print(f"需要同步 IPO K线/指标的股票: {len(codes)} 只")
    ok = fail = new_rows = 0
    for i, code in enumerate(codes, 1):
        success, result = sync_daily_kline_with_retry(code, conn, backfill=True)
        if success:
            ok += 1
            new_rows += int(result or 0)
            print(f"[{i}/{len(codes)}] {code}: K线新增/更新 {result} 条")
        else:
            fail += 1
            print(f"[{i}/{len(codes)}] {code}: 失败 {result}")
        time.sleep(0.5)

    conn.close()
    print(f"IPO K线同步完成：成功 {ok}，失败 {fail}，新增/更新 {new_rows} 条")

    print("开始回填 IPO 指标...")
    result = subprocess.run([sys.executable, 'update_ipo_metrics.py'], cwd=os.path.dirname(os.path.abspath(__file__)), text=True, capture_output=True, encoding='utf-8', errors='replace', timeout=600)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
