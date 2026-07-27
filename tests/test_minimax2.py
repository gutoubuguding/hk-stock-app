import httpx, json, psycopg2

# Get the actual key from database
conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()
cur.execute("SELECT config_value FROM stock_config WHERE config_key = 'ai_api_key'")
key = cur.fetchone()[0]
cur.execute("SELECT config_value FROM stock_config WHERE config_key = 'ai_base_url'")
base_url = cur.fetchone()[0]
cur.execute("SELECT config_value FROM stock_config WHERE config_key = 'ai_model'")
model = cur.fetchone()[0]
conn.close()

print(f'Key: {key[:20]}...{key[-10:]} (len={len(key)})')
print(f'URL: {base_url}')
print(f'Model: {model}')

# Test MiniMax API with the correct key
url = base_url + '/text/chatcompletion_v2'
headers = {
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}
payload = {
    'model': model,
    'messages': [
        {'role': 'user', 'content': '你好，请用一句话介绍自己'}
    ],
    'temperature': 0.7,
    'max_tokens': 100
}

print(f'\nCalling {url}...')
try:
    with httpx.Client(timeout=30) as client:
        resp = client.post(url, headers=headers, json=payload)
        print(f'Status: {resp.status_code}')
        data = resp.json()
        print(f'Response keys: {list(data.keys())}')
        if 'choices' in data and data['choices']:
            content = data['choices'][0].get('message', {}).get('content', '')
            print(f'Content: {content[:300]}')
        elif 'reply' in data:
            print(f'Reply: {data["reply"][:300]}')
        else:
            print(f'Full: {json.dumps(data, ensure_ascii=False)[:500]}')
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
