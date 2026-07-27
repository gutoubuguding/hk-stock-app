package com.hkstock.service;

import com.hkstock.domain.StockCalendar;
import java.util.List;
import java.util.Map;

/** 财报/分红日历服务接口 */
public interface CalendarService {

    /** 获取即将发布财报的股票 */
    List<StockCalendar> getUpcomingFinancialReports(Integer days);

    /** 获取即将派息的股票 */
    List<StockCalendar> getUpcomingDividends(Integer days);

    /** 获取大盘概览 */
    Map<String, Object> getMarketOverview();
}
