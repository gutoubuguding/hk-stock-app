package com.hkstock.controller;

import com.hkstock.entity.StockCalendar;
import com.hkstock.service.CalendarService;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/** 财报/分红日历控制器 */
@RestController
@RequestMapping("/api/calendar")
public class CalendarController {

  private @Autowired CalendarService calendarService;

  /** 获取即将发布财报的股票 */
  @GetMapping("/financial")
  public List<StockCalendar> getUpcomingFinancialReports(
      @RequestParam(defaultValue = "30") Integer days) {
    return calendarService.getUpcomingFinancialReports(days);
  }

  /** 获取即将派息的股票 */
  @GetMapping("/dividend")
  public List<StockCalendar> getUpcomingDividends(@RequestParam(defaultValue = "30") Integer days) {
    return calendarService.getUpcomingDividends(days);
  }

  /** 获取大盘概览 */
  @GetMapping("/market-overview")
  public Map<String, Object> getMarketOverview() {
    return calendarService.getMarketOverview();
  }
}
