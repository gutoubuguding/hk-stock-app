#!/usr/bin/env python3
"""通过Futu OpenD获取港股IPO列表"""
import socket
import json
import struct
import sys
sys.stdout.reconfigure(encoding='utf-8')

PROTOCOL_HEAD_SIZE = 44

def create_packet(proto_id, body_json):
    """创建Futu协议包"""
    body_bytes = body_json.encode('utf-8')
    
    # 协议头
    header = struct.pack('<HHBBiI',
        PROTOCOL_HEAD_SIZE,  # nHeadSize
        proto_id,            # nProtoID  
        2,                   # nProtoFmtType (JSON)
        1,                   # nProtoVer
        1,                   # nSerialNo
        len(body_bytes)      # nBodyLen
    )
    
    # 补齐到44字节
    header += b'\x00' * (PROTOCOL_HEAD_SIZE - len(header))
    
    return header + body_bytes

def send_request(host, port, proto_id, body):
    """发送请求到Futu OpenD"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        packet = create_packet(proto_id, json.dumps(body))
        sock.sendall(packet)
        
        # 读取响应头
        header_data = sock.recv(PROTOCOL_HEAD_SIZE)
        if len(header_data) < PROTOCOL_HEAD_SIZE:
            print("Invalid response header")
            return None
            
        # 解析响应头
        head_size, proto_id, fmt_type, ver, serial_no, body_len = struct.unpack('<HHBBiI', header_data[:16])
        
        # 读取响应体
        body_data = b''
        while len(body_data) < body_len:
            chunk = sock.recv(body_len - len(body_data))
            if not chunk:
                break
            body_data += chunk
            
        sock.close()
        
        return json.loads(body_data.decode('utf-8'))
        
    except Exception as e:
        print(f"Error: {e}")
        return None

# 连接到Futu OpenD
host = "127.0.0.1"
port = 11111

print(f"Connecting to Futu OpenD at {host}:{port}...")

# 测试连接 - 获取市场状态 (ProtoID: 1001)
body = {
    "c2s": {
        "marketList": [1]  # 1=港股
    }
}

print("\n1. Testing connection - GetMarketState...")
result = send_request(host, port, 1001, body)
if result:
    print(f"Response: {json.dumps(result, ensure_ascii=False)[:500]}")
else:
    print("Failed to connect")

# 获取IPO列表 (ProtoID: 3200)
print("\n2. Getting IPO list...")
body = {
    "c2s": {
        "market": 1  # 港股
    }
}
result = send_request(host, port, 3200, body)
if result:
    print(f"Response: {json.dumps(result, ensure_ascii=False)[:1000]}")
else:
    print("Failed to get IPO list")

# 尝试其他可能的ProtoID
print("\n3. Trying alternative ProtoID 3201...")
result = send_request(host, port, 3201, body)
if result:
    print(f"Response: {json.dumps(result, ensure_ascii=False)[:500]}")
else:
    print("Failed")
