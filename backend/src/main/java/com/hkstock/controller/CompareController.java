package com.hkstock.controller;

import com.hkstock.service.StockService;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/** 股票对比控制器 */
@RestController
@RequestMapping("/api/compare")
public class CompareController {

  private @Autowired StockService stockService;

  /**
   * 对比多只股票
   *
   * @param stockCodes 股票代码列表，逗号分隔，如 "00700,09988,03690"
   */
  @GetMapping
  public Map<String, Object> compareStocks(
      @RequestParam String stockCodes,
      @RequestParam(defaultValue = "pe,pb,change,volume,marketCap") String metrics) {
    List<String> codes = List.of(stockCodes.split(","));
    return stockService.compareStocks(codes, metrics);
  }
}
