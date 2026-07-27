package com.hkstock.vo;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 日历事件视图对象 */
@Data
public class StockCalendarVO {
    private Long id;
    private String stockCode;
    private String stockName;
    private String eventType;
    private LocalDate eventDate;
    private BigDecimal dividendPerShare;
    private LocalDate exDividendDate;
    private LocalDate paymentDate;
    private String financialReportType;
}
