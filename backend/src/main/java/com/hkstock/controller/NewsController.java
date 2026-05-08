package com.hkstock.controller;

import com.hkstock.entity.News;
import com.hkstock.service.AiAnalysisService;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/** 新闻AI分析控制器 */
@RestController
@RequestMapping("/api/news")
public class NewsController {

  private @Autowired AiAnalysisService aiAnalysisService;

  /** 获取股票相关新闻及AI分析 */
  @GetMapping("/analyze")
  public Map<String, Object> analyzeStockNews(
      @RequestParam String stockCode,
      @RequestParam(required = false) String stockName,
      @RequestParam(defaultValue = "7") Integer days) {
    return aiAnalysisService.analyzeStockNews(stockCode, stockName, days);
  }

  /** 获取新闻列表 */
  @GetMapping("/list")
  public List<News> getNewsList(
      @RequestParam String stockCode, @RequestParam(defaultValue = "7") Integer days) {
    return aiAnalysisService.getNewsList(stockCode, days);
  }
}
