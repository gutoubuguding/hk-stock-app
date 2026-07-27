import httpx, json, psycopg2

conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()
cur.execute("SELECT config_value FROM stock_config WHERE config_key = 'ai_api_key'")
key = cur.fetchone()[0]
conn.close()

headers = {
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

# Try different MiniMax formats
tests = [
    {
        'name': 'Format 1: OpenAI-compatible with MiniMax-M2.5',
        'url': 'https://api.minimax.chat/v1/text/chatcompletion_v2',
        'payload': {
            'model': 'MiniMax-M2.5',
            'messages': [{'role': 'user', 'content': '你好'}],
            'max_tokens': 50
        }
    },
    {
        'name': 'Format 2: MiniMax M2.7 standard',
        'url': 'https://api.minimax.chat/v1/text/chatcompletion_v2',
        'payload': {
            'model': 'MiniMax-M2.7',
            'messages': [{'role': 'user', 'content': '你好'}],
            'max_tokens': 50,
            'stream': False
        }
    },
    {
        'name': 'Format 3: abab6.5s-chat',
        'url': 'https://api.minimax.chat/v1/text/chatcompletion_v2',
        'payload': {
            'model': 'abab6.5s-chat',
            'messages': [{'role': 'user', 'content': '你好'}],
            'max_tokens': 50
        }
    },
    {
        'name': 'Format 4: OpenAI-compatible endpoint',
        'url': 'https://api.minimax.chat/v1/chat/completions',
        'payload': {
            'model': 'MiniMax-M2.7',
            'messages': [{'role': 'user', 'content': '你好'}],
            'max_tokens': 50
        }
    },
]

for test in tests:
    print(f'\n=== {test["name"]} ===')
    try:
        with httpx.Client(timeout=20) as client:
            resp = client.post(test['url'], headers=headers, json=test['payload'])
            print(f'Status: {resp.status_code}')
            data = resp.json()
            if 'choices' in data and data['choices']:
                content = data['choices'][0].get('message', {}).get('content', '')
                print(f'OK! Content: {content[:200]}')
            else:
                print(f'Response: {json.dumps(data, ensure_ascii=False)[:300]}')
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')
