import httpx
from bs4 import BeautifulSoup

keyword = "小米集团"
url = "https://news.google.com/rss/search"
params = {"q": f"{keyword} 港股", "hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans"}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

try:
    with httpx.Client(timeout=15, follow_redirects=True) as client:
        resp = client.get(url, params=params, headers=headers)
        print(f"Status: {resp.status_code}")
        
        soup = BeautifulSoup(resp.text, "lxml-xml")
        items = soup.find_all("item", limit=3)
        print(f"Found {len(items)} items")
        
        for i, item in enumerate(items):
            title = item.find("title").text if item.find("title") else ""
            link = item.find("link").text if item.find("link") else ""
            source = item.find("source").text if item.find("source") else ""
            print(f"  {i+1}. [{source}] {title}")
            print(f"     Link: {link}")
            print()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
