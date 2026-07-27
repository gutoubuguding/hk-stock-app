package com.hkstock.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 财报/分红日历 */
@Data
@TableName("stock_calendar")
public class StockCalendar {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String stockCode;
    private String stockName;
    private String eventType;
    private LocalDate eventDate;
    private BigDecimal dividendPerShare;
    private LocalDate exDividendDate;
    private LocalDate paymentDate;
    private String financialReportType;
    private LocalDateTime createdAt;
}
