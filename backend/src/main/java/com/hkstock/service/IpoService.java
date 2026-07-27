package com.hkstock.service;

import com.hkstock.domain.StockIpo;
import java.util.List;
import java.util.Map;

/** 新股服务接口 */
public interface IpoService {

    /** 获取即将上市新股 */
    List<StockIpo> getUpcomingIpo();

    /** 获取近一年新股横向对比 */
    Map<String, Object> getIpoComparison(String sortBy, String sortOrder);

    /** 新股板块统计 */
    Map<String, Object> getSectorStats();

    /** 破发率统计 */
    Map<String, Object> getBreakRate();

    /** AI分析新股走势 */
    Map<String, Object> getAiAnalysis(String stockCode);

    /** 刷新新股数据 */
    void refreshIpoData();

    /** 获取指定板块的所有新股 */
    Map<String, Object> getIposBySector(String sector);
}
