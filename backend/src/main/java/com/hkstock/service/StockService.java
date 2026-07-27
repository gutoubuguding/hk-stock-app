package com.hkstock.service;

import com.hkstock.domain.StockInfo;
import com.hkstock.domain.StockKline;
import com.hkstock.domain.StockValuation;
import java.util.List;
import java.util.Map;

/** 股票服务接口 */
public interface StockService {

    /** 搜索股票 */
    List<StockInfo> searchStocks(String keyword);

    /** 获取K线数据 */
    List<StockKline> getKlineData(String stockCode, String periodType, Integer days);

    /** 获取最新日K数据（当日关键信息） */
    StockKline getLatestDailyInfo(String stockCode);

    /** 获取估值指标 */
    StockValuation getValuation(String stockCode);

    /** 对比多只股票 */
    Map<String, Object> compareStocks(List<String> stockCodes, String metrics);

    /** 从Futu OpenAPI刷新K线数据 */
    void refreshKlineData(String stockCode, String periodType, int days);

    /** 刷新股票列表 */
    void refreshStockList();
}
