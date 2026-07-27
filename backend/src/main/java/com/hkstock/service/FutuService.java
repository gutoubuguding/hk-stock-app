package com.hkstock.service;

import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;
import java.util.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

/** Futu OpenAPI 服务 - 通过 AI 微服务代理调用 */
@Service
public class FutuService {

    private static final Logger log = LoggerFactory.getLogger(FutuService.class);

    @Value("${ai-service.url:http://localhost:8082}")
    private String aiServiceUrl;

    private final RestTemplate restTemplate;

    public FutuService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    /** 获取股票K线数据 */
    public List<Map<String, Object>> getKlineData(String stockCode, String periodType, int count) {
        try {
            String period = convertPeriodType(periodType);
            String url = aiServiceUrl + "/api/sync/kline/{stockCode}?period={period}&count={count}";

            JSONObject response = restTemplate.getForObject(url, JSONObject.class, stockCode, period, count);
            if (response == null || !response.getBooleanValue("success")) {
                log.error("获取K线数据失败: {}", response);
                return new ArrayList<>();
            }

            JSONArray klineList = response.getJSONArray("data");
            List<Map<String, Object>> result = new ArrayList<>();

            for (int i = 0; i < klineList.size(); i++) {
                JSONObject kline = klineList.getJSONObject(i);
                Map<String, Object> data = new HashMap<>();
                data.put("date", kline.getString("date"));
                data.put("open", kline.getBigDecimal("open"));
                data.put("close", kline.getBigDecimal("close"));
                data.put("high", kline.getBigDecimal("high"));
                data.put("low", kline.getBigDecimal("low"));
                data.put("volume", kline.getLong("volume"));
                data.put("turnover", kline.getBigDecimal("turnover"));
                data.put("changePercent", kline.getBigDecimal("changePercent"));
                data.put("turnoverRate", kline.getBigDecimal("turnoverRate"));
                result.add(data);
            }

            return result;

        } catch (Exception e) {
            log.error("获取K线数据异常: {}", e.getMessage(), e);
            return new ArrayList<>();
        }
    }

    /** 获取股票列表 */
    public List<Map<String, Object>> getStockList() {
        try {
            String url = aiServiceUrl + "/api/sync/stocks";

            JSONObject response = restTemplate.getForObject(url, JSONObject.class);
            if (response == null || !response.getBooleanValue("success")) {
                log.error("获取股票列表失败: {}", response);
                return new ArrayList<>();
            }

            JSONArray stockList = response.getJSONArray("data");
            List<Map<String, Object>> result = new ArrayList<>();

            for (int i = 0; i < stockList.size(); i++) {
                JSONObject stock = stockList.getJSONObject(i);
                Map<String, Object> data = new HashMap<>();
                data.put("code", stock.getString("code"));
                data.put("name", stock.getString("name"));
                data.put("lotSize", stock.getIntValue("lotSize"));
                data.put("stockType", stock.getIntValue("stockType"));
                result.add(data);
            }

            return result;

        } catch (Exception e) {
            log.error("获取股票列表异常: {}", e.getMessage(), e);
            return new ArrayList<>();
        }
    }

    /** 获取IPO列表 */
    public List<Map<String, Object>> getIpoList() {
        try {
            String url = aiServiceUrl + "/api/sync/ipo";

            JSONObject response = restTemplate.getForObject(url, JSONObject.class);
            if (response == null || !response.getBooleanValue("success")) {
                log.error("获取IPO列表失败: {}", response);
                return new ArrayList<>();
            }

            JSONArray ipoList = response.getJSONArray("data");
            List<Map<String, Object>> result = new ArrayList<>();

            for (int i = 0; i < ipoList.size(); i++) {
                JSONObject ipo = ipoList.getJSONObject(i);
                Map<String, Object> data = new HashMap<>();
                data.put("code", ipo.getString("code"));
                data.put("name", ipo.getString("name"));
                data.put("listTime", ipo.getString("listTime"));
                data.put("ipoPrice", ipo.getBigDecimal("ipoPrice"));
                result.add(data);
            }

            return result;

        } catch (Exception e) {
            log.error("获取IPO列表异常: {}", e.getMessage(), e);
            return new ArrayList<>();
        }
    }

    /** 转换周期类型 */
    private String convertPeriodType(String periodType) {
        return switch (periodType.toUpperCase()) {
            case "D", "5D" -> "K_DAY";
            case "W" -> "K_WEEK";
            case "M" -> "K_MON";
            default -> "K_DAY";
        };
    }
}
