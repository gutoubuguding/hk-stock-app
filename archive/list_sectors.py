import httpx
r = httpx.get('http://localhost:8080/api/ipo/sector-stats', timeout=10)
data = r.json()
print(f"共 {data['totalSectors']} 个板块:\n")
for s in sorted(data['stats'], key=lambda x: -x['count']):
    print(f"{s['sector']:30s} {s['count']:3d}只")