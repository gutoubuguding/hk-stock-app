package com.hkstock.service;

import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * AI分析服务（调用Python微服务）
 */
@Service
public class AiAnalysisService {
    private static final Logger log = LoggerFactory.getLogger(AiAnalysisService.class);


    private @Autowired RestTemplate restTemplate;
    private @Autowired com.hkstock.mapper.NewsMapper newsMapper;

    @Value("${ai-service.url}")
    private String aiServiceUrl;

    /**
     * 分析股票新闻
     */
    public Map<String, Object> analyzeStockNews(String stockCode, String stockName, Integer days) {
        try {
            // 获取股票名称用于新闻搜索
            String name = stockName;
            if (name == null || name.isBlank()) {
                name = getStockNameByCode(stockCode);
            }
            
            // 调用Python AI微服务
            String url = aiServiceUrl + "/api/analyze/stock-news?stock_code={code}&stock_name={name}&days={days}";
            JSONObject response = restTemplate.getForObject(url, JSONObject.class, stockCode, name, days);
            return response != null ? response : new HashMap<>();
        } catch (Exception e) {
            log.error("调用AI服务失败: {}", e.getMessage());
            Map<String, Object> fallback = new HashMap<>();
            fallback.put("error", "AI服务暂时不可用: " + e.getMessage());
            return fallback;
        }
    }
    
    /**
     * 根据股票代码获取股票名称
     */
    private String getStockNameByCode(String stockCode) {
        try {
            String url = aiServiceUrl.replace("8081", "8080") + "/api/stock/info?stockCode=" + stockCode;
            JSONObject response = restTemplate.getForObject(url, JSONObject.class);
            if (response != null && response.containsKey("stockName")) {
                return response.getString("stockName");
            }
        } catch (Exception e) {
            log.warn("获取股票名称失败: {}", e.getMessage());
        }
        return stockCode;
    }

    /**
     * 获取新闻列表
     */
    public List<com.hkstock.entity.News> getNewsList(String stockCode, Integer days) {
        return newsMapper.selectByStockCodeAndDays(stockCode, days);
    }
}
