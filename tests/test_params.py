#!/usr/bin/env python3
"""测试AI服务参数接收"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/test")
def test_params(
    stock_code: str = Query(...),
    api_key: str = Query(None),
    base_url: str = Query(None),
    model: str = Query(None)
):
    return {
        "received": {
            "stock_code": stock_code,
            "api_key": api_key,
            "base_url": base_url,
            "model": model
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
