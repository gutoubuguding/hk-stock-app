import httpx
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False

# Test connection to MiniMax API
headers = {
    "Authorization": "Bearer sk-cp-kvWu_D1285p3QaGD0wEvAzkLj4gJb_J45_9YiQmupBu5LTEd389ackr0lxxR3V_l86KO9euvMbuaRyYf62E113mK0BZl2oHCQlTuOOEQggwGj2vkG1Nm3Nk",
    "Content-Type": "application/json"
}

payload = {
    "model": "MiniMax-M2.7",
    "messages": [
        {"role": "user", "content": "Hello, respond with 'OK' only"}
    ],
    "temperature": 0.7,
    "max_tokens": 50
}

url = "https://api.minimax.chat/v1/chat/completions"

try:
    with httpx.Client(timeout=15, follow_redirects=True) as client:
        resp = client.post(url, headers=headers, json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")