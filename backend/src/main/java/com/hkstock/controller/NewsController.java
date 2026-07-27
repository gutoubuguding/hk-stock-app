package com.hkstock.controller;

import com.hkstock.common.ApiResponse;
import com.hkstock.domain.News;
import com.hkstock.service.AiAnalysisService;
import jakarta.annotation.Resource;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.*;

/** 新闻AI分析控制器 */
@RestController
@RequestMapping("/api/news")
public class NewsController {

    @Resource
    private AiAnalysisService aiAnalysisService;

    /** 获取股票相关新闻及AI分析 */
    @GetMapping("/analyze")
    public ApiResponse<Map<String, Object>> analyzeStockNews(
        @RequestParam String stockCode,
        @RequestParam(required = false) String stockName,
        @RequestParam(defaultValue = "7") Integer days,
        @RequestParam(required = false) String apiKey,
        @RequestParam(required = false) String baseUrl,
        @RequestParam(required = false) String model) {
        return ApiResponse.success(aiAnalysisService.analyzeStockNews(stockCode, stockName, days, apiKey, baseUrl, model));
    }

    /** 获取新闻列表 */
    @GetMapping("/list")
    public ApiResponse<List<News>> getNewsList(
        @RequestParam String stockCode,
        @RequestParam(defaultValue = "7") Integer days) {
        return ApiResponse.success(aiAnalysisService.getNewsList(stockCode, days));
    }
}
