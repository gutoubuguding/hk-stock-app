"""数据同步路由 - 提供 Futu OpenD 数据同步接口"""

import os
import logging
import sys
sys.stdout.reconfigure(encoding='utf-8')

from fastapi import APIRouter, HTTPException
from futu import OpenQuoteContext, RET_OK, Market, KLType

router = APIRouter(prefix="/api/sync", tags=["sync"])

logger = logging.getLogger(__name__)

# Futu OpenD 配置
FUTU_HOST = os.getenv("FUTU_OPEND_HOST", "host.docker.internal")
FUTU_PORT = int(os.getenv("FUTU_OPEND_PORT", "11111"))


@router.get("/stocks")
async def sync_stocks():
    """同步港股股票列表"""
    try:
        quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)
        quote_ctx.set_sync_query_connect_timeout(10)

        # 获取港股全部股票列表
        ret, data = quote_ctx.get_stock_basicinfo(Market.HK)
        quote_ctx.close()

        if ret != RET_OK:
            raise HTTPException(status_code=500, detail=f"获取股票列表失败: {data}")

        stocks = []
        for _, row in data.iterrows():
            # 过滤出正股 (stock_type == 2 表示正股)
            stock_type = int(row.get("stock_type", 0))
            if stock_type == 2:
                stocks.append({
                    "code": row["code"],
                    "name": row["name"],
                    "lotSize": int(row.get("lot_size", 0)),
                    "stockType": stock_type
                })

        return {
            "success": True,
            "count": len(stocks),
            "data": stocks
        }

    except Exception as e:
        logger.error(f"同步股票列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ipo")
async def sync_ipo():
    """同步港股 IPO 列表"""
    try:
        quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)
        quote_ctx.set_sync_query_connect_timeout(10)

        # 获取 IPO 列表
        ret, data = quote_ctx.get_ipo_list(market=Market.HK)
        quote_ctx.close()

        if ret != RET_OK:
            raise HTTPException(status_code=500, detail=f"获取IPO列表失败: {data}")

        ipos = []
        for _, row in data.iterrows():
            ipos.append({
                "code": row["code"],
                "name": row["name"],
                "listTime": str(row.get("list_time", "")),
                "ipoPrice": float(row.get("ipo_price", 0)) if row.get("ipo_price") else None,
            })

        return {
            "success": True,
            "count": len(ipos),
            "data": ipos
        }

    except Exception as e:
        logger.error(f"同步IPO列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kline/{stock_code}")
async def sync_kline(stock_code: str, period: str = "K_DAY", count: int = 120):
    """同步单只股票的 K 线数据"""
    try:
        quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)
        quote_ctx.set_sync_query_connect_timeout(10)

        # 映射周期类型
        kl_type_map = {
            "K_DAY": KLType.K_DAY,
            "K_WEEK": KLType.K_WEEK,
            "K_MON": KLType.K_MON,
        }
        kl_type = kl_type_map.get(period, KLType.K_DAY)

        ret, data = quote_ctx.request_history_kline(stock_code, ktype=kl_type, max_count=count)
        quote_ctx.close()

        if ret != RET_OK:
            raise HTTPException(status_code=500, detail=f"获取K线失败: {data}")

        klines = []
        for _, row in data.iterrows():
            klines.append({
                "date": str(row["time_key"]),
                "open": float(row["open"]),
                "close": float(row["close"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "volume": int(row["volume"]),
                "turnover": float(row["turnover"]),
                "changePercent": float(row.get("change_rate", 0)),
                "turnoverRate": float(row.get("turnover_rate", 0)),
            })

        return {
            "success": True,
            "stockCode": stock_code,
            "period": period,
            "count": len(klines),
            "data": klines
        }

    except Exception as e:
        logger.error(f"同步K线失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
