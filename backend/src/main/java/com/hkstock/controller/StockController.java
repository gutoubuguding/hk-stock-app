package com.hkstock.controller;

import com.hkstock.entity.StockInfo;
import com.hkstock.entity.StockKline;
import com.hkstock.service.StockService;
import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/** 股票查询控制器 */
@RestController
@RequestMapping("/api/stock")
public class StockController {

  private @Autowired StockService stockService;

  /** 搜索股票（按代码/名称/类别） */
  @GetMapping("/search")
  public List<StockInfo> searchStocks(@RequestParam String keyword) {
    return stockService.searchStocks(keyword);
  }

  /** 获取股票K线数据 */
  @GetMapping("/kline")
  public List<StockKline> getKline(
      @RequestParam String stockCode,
      @RequestParam(defaultValue = "D") String periodType,
      @RequestParam(defaultValue = "120") Integer days) {
    return stockService.getKlineData(stockCode, periodType, days);
  }

  /** 获取股票当日关键信息 */
  @GetMapping("/daily-info")
  public StockKline getDailyInfo(@RequestParam String stockCode) {
    return stockService.getLatestDailyInfo(stockCode);
  }

  /** 获取股票估值指标 */
  @GetMapping("/valuation")
  public Object getValuation(@RequestParam String stockCode) {
    return stockService.getValuation(stockCode);
  }

  /** 刷新股票列表（从Futu OpenAPI拉取） */
  @PostMapping("/refresh-list")
  public String refreshStockList() {
    stockService.refreshStockList();
    return "股票列表刷新完成";
  }

  /** 刷新K线数据 */
  @PostMapping("/refresh-kline")
  public String refreshKline(
      @RequestParam String stockCode,
      @RequestParam(defaultValue = "D") String periodType,
      @RequestParam(defaultValue = "120") Integer days) {
    stockService.refreshKlineData(stockCode, periodType, days);
    return "K线数据刷新完成: " + stockCode + " - " + periodType;
  }

  /** 一键刷新所有周期K线数据（日K/月K/年K） */
  @PostMapping("/refresh-kline-all")
  public String refreshKlineAll(@RequestParam String stockCode) {
    stockService.refreshKlineData(stockCode, "D", 120);
    stockService.refreshKlineData(stockCode, "M", 36);
    stockService.refreshKlineData(stockCode, "Y", 10);
    return "全部周期K线数据刷新完成: " + stockCode;
  }
}
