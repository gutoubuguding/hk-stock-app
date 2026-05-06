"""
港股分析应用 - AI微服务
基于 FastAPI + LLM API + akshare数据同步
"""
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analyze, scraper, config
import subprocess
import threading
from datetime import datetime

app = FastAPI(
    title="港股AI分析微服务",
    description="提供新股AI分析、新闻分析、K线同步等功能",
    version="1.1.0"
)

# 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(analyze.router, prefix="/api/analyze", tags=["AI分析"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["数据爬取"])
app.include_router(config.router, prefix="/api/config", tags=["配置管理"])

# K线同步状态
_kline_sync_status = {"running": False, "progress": "", "last_run": None}
_ipo_sync_status = {"running": False, "progress": "", "last_run": None}


def _run_kline_sync_script():
    """在后台线程中运行K线同步脚本"""
    global _kline_sync_status
    try:
        _kline_sync_status["running"] = True
        _kline_sync_status["progress"] = "开始同步..."
        result = subprocess.run(
            ["python", "sync_daily_kline.py"],
            cwd="/tmp/hk-stock" if False else "C:/Users/34596/.openclaw/workspace/hk-stock-app",
            capture_output=True,
            text=True,
            timeout=3600  # 最多跑1小时
        )
        if result.returncode == 0:
            _kline_sync_status["progress"] = "同步完成"
        else:
            _kline_sync_status["progress"] = f"同步失败: {result.stderr[-200:]}"
    except subprocess.TimeoutExpired:
        _kline_sync_status["progress"] = "同步超时（>1小时）"
    except Exception as e:
        _kline_sync_status["progress"] = f"同步异常: {str(e)[:100]}"
    finally:
        _kline_sync_status["running"] = False
        _kline_sync_status["last_run"] = str(datetime.now())


def _run_ipo_sync_script():
    """在后台线程中运行IPO同步脚本（Futu API）"""
    global _ipo_sync_status
    try:
        _ipo_sync_status["running"] = True
        _ipo_sync_status["progress"] = "开始同步..."
        result = subprocess.run(
            ["python", "sync_ipo_futu.py"],
            cwd="C:/Users/34596/.openclaw/workspace/hk-stock-app",
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            _ipo_sync_status["progress"] = "同步完成"
            if result.stdout:
                _ipo_sync_status["progress"] = result.stdout.strip().split('\n')[-1]
        else:
            _ipo_sync_status["progress"] = f"同步失败: {result.stderr[-200:]}"
    except subprocess.TimeoutExpired:
        _ipo_sync_status["progress"] = "同步超时（>60秒）"
    except Exception as e:
        _ipo_sync_status["progress"] = f"同步异常: {str(e)[:100]}"
    finally:
        _ipo_sync_status["running"] = False
        _ipo_sync_status["last_run"] = str(datetime.now())


@app.get("/api/sync/kline")
def sync_kline_background(background_tasks: BackgroundTasks):
    """触发全量K线同步（后台异步执行）"""
    global _kline_sync_status
    if _kline_sync_status["running"]:
        return {"status": "running", "progress": _kline_sync_status["progress"]}
    background_tasks.add_task(_run_kline_sync_script)
    return {"status": "started", "message": "K线同步已在后台启动"}


@app.get("/api/sync/kline/status")
def sync_kline_status():
    """查询K线同步状态"""
    return _kline_sync_status


@app.get("/api/sync/ipo")
def sync_ipo_background(background_tasks: BackgroundTasks):
    """触发IPO同步（后台异步执行，使用Futu API）"""
    global _ipo_sync_status
    if _ipo_sync_status["running"]:
        return {"status": "running", "progress": _ipo_sync_status["progress"]}
    background_tasks.add_task(_run_ipo_sync_script)
    return {"status": "started", "message": "IPO同步已在后台启动"}


@app.get("/api/sync/ipo/status")
def sync_ipo_status():
    """查询IPO同步状态"""
    return _ipo_sync_status


@app.get("/")
def root():
    return {"message": "港股AI分析微服务运行中", "version": "1.1.0"}


@app.get("/health")
def health():
    return {"status": "ok"}
