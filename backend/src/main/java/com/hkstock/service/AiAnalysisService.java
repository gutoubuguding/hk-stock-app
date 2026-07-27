package com.hkstock.service;

import com.hkstock.domain.News;
import java.util.List;
import java.util.Map;

/** AI分析服务接口 */
public interface AiAnalysisService {

    /** 分析股票新闻 */
    Map<String, Object> analyzeStockNews(String stockCode, String stockName, Integer days, 
                                         String apiKey, String baseUrl, String model);

    /** 获取新闻列表 */
    List<News> getNewsList(String stockCode, Integer days);
}
