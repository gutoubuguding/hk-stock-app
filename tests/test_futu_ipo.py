#!/usr/bin/env python3
"""Quick test of Futu OpenD IPO connection"""
import sys
sys.path.insert(0, 'C:/Users/34596/.openclaw/workspace/hk-stock-app/backend/src/main/java')
# Actually can't import Java - let's use socket directly
import socket
import json
import struct

HOST = '127.0.0.1'
PORT = 11111

def send_futu_request(command_id, body_dict):
    """Send a request to Futu OpenD and get response"""
    # Protocol format: use JSON over simple socket
    # First let's try the simple approach
    req = {
        "protocol": 1,
        "cmd": command_id,
        "seq": 1,
        "body": body_dict
    }
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((HOST, PORT))
        
        # Send JSON request
        msg = json.dumps(req).encode('utf-8')
        # Prepend 4-byte length
        header = struct.pack('<I', len(msg))
        s.sendall(header + msg)
        
        # Read response length
        resp_len_bytes = s.recv(4)
        if len(resp_len_bytes) < 4:
            print(f"Failed to read response length")
            s.close()
            return None
        resp_len = struct.unpack('<I', resp_len_bytes)[0]
        
        # Read response
        resp_data = b''
        while len(resp_data) < resp_len:
            chunk = s.recv(resp_len - len(resp_data))
            if not chunk:
                break
            resp_data += chunk
        
        s.close()
        
        resp = json.loads(resp_data.decode('utf-8'))
        return resp
        
    except Exception as e:
        print(f"Socket error: {e}")
        return None

# Try command 3200 - GetIPOList
print("Testing Futu OpenD connection (IPO List - cmd 3200)...")
resp = send_futu_request(3200, {"market": 1})
if resp:
    print(f"Response: {json.dumps(resp, ensure_ascii=False)[:500]}")
else:
    print("No response from Futu OpenD")

# Also check if port is actually open
print("\nChecking port 11111...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
result = s.connect_ex((HOST, PORT))
if result == 0:
    print("Port 11111 is OPEN and accepting connections")
else:
    print(f"Port 11111 connection failed with code: {result}")
s.close()
