package com.hkstock.controller;

import com.hkstock.common.ApiResponse;
import com.hkstock.domain.StockCalendar;
import com.hkstock.service.CalendarService;
import jakarta.annotation.Resource;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.*;

/** 财报/分红日历控制器 */
@RestController
@RequestMapping("/api/calendar")
public class CalendarController {

    @Resource
    private CalendarService calendarService;

    /** 获取即将发布财报的股票 */
    @GetMapping("/financial")
    public ApiResponse<List<StockCalendar>> getUpcomingFinancialReports(
        @RequestParam(defaultValue = "30") Integer days) {
        return ApiResponse.success(calendarService.getUpcomingFinancialReports(days));
    }

    /** 获取即将派息的股票 */
    @GetMapping("/dividend")
    public ApiResponse<List<StockCalendar>> getUpcomingDividends(
        @RequestParam(defaultValue = "30") Integer days) {
        return ApiResponse.success(calendarService.getUpcomingDividends(days));
    }

    /** 获取大盘概览 */
    @GetMapping("/market-overview")
    public ApiResponse<Map<String, Object>> getMarketOverview() {
        return ApiResponse.success(calendarService.getMarketOverview());
    }
}
