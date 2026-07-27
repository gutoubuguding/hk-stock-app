package com.hkstock.controller;

import com.hkstock.common.ApiResponse;
import com.hkstock.domain.StockInfo;
import com.hkstock.domain.StockKline;
import com.hkstock.domain.StockValuation;
import com.hkstock.service.StockService;
import jakarta.annotation.Resource;
import java.util.List;
import org.springframework.web.bind.annotation.*;

/** 股票查询控制器 */
@RestController
@RequestMapping("/api/stock")
public class StockController {

    @Resource
    private StockService stockService;

    /** 搜索股票（按代码/名称/类别） */
    @GetMapping("/search")
    public ApiResponse<List<StockInfo>> searchStocks(@RequestParam String keyword) {
        return ApiResponse.success(stockService.searchStocks(keyword));
    }

    /** 获取股票K线数据 */
    @GetMapping("/kline")
    public ApiResponse<List<StockKline>> getKline(
        @RequestParam String stockCode,
        @RequestParam(defaultValue = "D") String periodType,
        @RequestParam(defaultValue = "120") Integer days) {
        return ApiResponse.success(stockService.getKlineData(stockCode, periodType, days));
    }

    /** 获取股票当日关键信息 */
    @GetMapping("/daily-info")
    public ApiResponse<StockKline> getDailyInfo(@RequestParam String stockCode) {
        return ApiResponse.success(stockService.getLatestDailyInfo(stockCode));
    }

    /** 获取股票估值指标 */
    @GetMapping("/valuation")
    public ApiResponse<StockValuation> getValuation(@RequestParam String stockCode) {
        return ApiResponse.success(stockService.getValuation(stockCode));
    }

    /** 刷新股票列表（从Futu OpenAPI拉取） */
    @PostMapping("/refresh-list")
    public ApiResponse<String> refreshStockList() {
        stockService.refreshStockList();
        return ApiResponse.success("股票列表刷新完成");
    }

    /** 刷新K线数据 */
    @PostMapping("/refresh-kline")
    public ApiResponse<String> refreshKline(
        @RequestParam String stockCode,
        @RequestParam(defaultValue = "D") String periodType,
        @RequestParam(defaultValue = "120") Integer days) {
        stockService.refreshKlineData(stockCode, periodType, days);
        return ApiResponse.success("K线数据刷新完成: " + stockCode + " - " + periodType);
    }

    /** 一键刷新所有周期K线数据（日K/月K/年K） */
    @PostMapping("/refresh-kline-all")
    public ApiResponse<String> refreshKlineAll(@RequestParam String stockCode) {
        stockService.refreshKlineData(stockCode, "D", 120);
        stockService.refreshKlineData(stockCode, "M", 36);
        stockService.refreshKlineData(stockCode, "Y", 10);
        return ApiResponse.success("全部周期K线数据刷新完成: " + stockCode);
    }
}
