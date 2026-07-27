package com.hkstock.service.impl;

import com.alibaba.fastjson2.JSONObject;
import com.hkstock.domain.News;
import com.hkstock.mapper.NewsMapper;
import com.hkstock.service.AiAnalysisService;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import jakarta.annotation.Resource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

/** AI分析服务实现 */
@Service
public class AiAnalysisServiceImpl implements AiAnalysisService {

    private static final Logger log = LoggerFactory.getLogger(AiAnalysisServiceImpl.class);

    @Resource
    private RestTemplate restTemplate;
    @Resource
    private NewsMapper newsMapper;

    @Value("${ai-service.url}")
    private String aiServiceUrl;

    @Override
    public Map<String, Object> analyzeStockNews(String stockCode, String stockName, Integer days,
                                                 String apiKey, String baseUrl, String model) {
        try {
            String name = stockName;
            if (name == null || name.isBlank()) {
                name = getStockNameByCode(stockCode);
            }

            // 构建URL，包含API配置参数
            String url = aiServiceUrl + "/api/analyze/stock-news?stock_code={code}&stock_name={name}&days={days}";
            if (apiKey != null && !apiKey.isBlank()) {
                url += "&api_key={apiKey}";
            }
            if (baseUrl != null && !baseUrl.isBlank()) {
                url += "&base_url={baseUrl}";
            }
            if (model != null && !model.isBlank()) {
                url += "&model={model}";
            }

            JSONObject response = restTemplate.getForObject(url, JSONObject.class, 
                stockCode, name, days, apiKey, baseUrl, model);
            return response != null ? response : new HashMap<>();
        } catch (Exception e) {
            log.error("调用AI服务失败: {}", e.getMessage());
            Map<String, Object> fallback = new HashMap<>();
            fallback.put("error", "AI服务暂时不可用: " + e.getMessage());
            return fallback;
        }
    }

    @Override
    public List<News> getNewsList(String stockCode, Integer days) {
        return newsMapper.selectByStockCodeAndDays(stockCode, days);
    }

    private String getStockNameByCode(String stockCode) {
        try {
            String url = aiServiceUrl + "/api/stock/info?stockCode=" + stockCode;
            JSONObject response = restTemplate.getForObject(url, JSONObject.class);
            if (response != null && response.containsKey("stockName")) {
                return response.getString("stockName");
            }
        } catch (Exception e) {
            log.warn("获取股票名称失败: {}", e.getMessage());
        }
        return stockCode;
    }
}
