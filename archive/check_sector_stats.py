import httpx
with httpx.Client(timeout=10) as client:
    r = client.get('http://localhost:8080/api/ipo/sector-stats')
    data = r.json()
    print('total:', data.get('total'))
    print('totalSectors:', data.get('totalSectors'))
    print()
    print('前3个板块:')
    for s in data['stats'][:3]:
        print(f"  {s['sector']}: count={s['count']}, avg7d={s.get('avgSevenDayChange')}, avg30d={s.get('avgThirtyDayChange')}")