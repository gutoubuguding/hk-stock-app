#!/usr/bin/env python3
"""Test MiniMax API directly"""
import sys
sys.path.insert(0, r'C:\Users\34596\AppData\Local\Programs\Python\Python313\Lib\site-packages')
import httpx
import os

llm_config = {
    "api_key": os.getenv("AI_API_KEY", "sk-cp-kvWu_D1285p3QaGD0wEvAzkLj4gJb_J45_9YiQmupBu5LTEd389ackr0lxxR3V_l86KO9euvMbuaRyYf62E113mK0BZl2oHCQlTuOOEQggwGj2vkG1Nm3Nk"),
    "base_url": "https://api.minimax.chat/v1",
    "model": "MiniMax-M2.7"
}

print("Testing MiniMax API...")
headers = {
    "Authorization": f"Bearer {llm_config['api_key']}",
    "Content-Type": "application/json"
}

payload = {
    "model": llm_config['model'],
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'OK' in one word"}
    ],
    "temperature": 0.7,
    "max_tokens": 10
}

try:
    with httpx.Client(timeout=15) as client:
        response = client.post(llm_config['base_url'] + "/chat/completions", headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:300]}")
except Exception as e:
    print(f"Failed: {type(e).__name__}: {e}")