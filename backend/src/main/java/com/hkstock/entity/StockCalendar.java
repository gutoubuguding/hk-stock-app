package com.hkstock.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 财报/分红日历
 */
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

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getStockCode() { return stockCode; }
    public void setStockCode(String stockCode) { this.stockCode = stockCode; }
    public String getStockName() { return stockName; }
    public void setStockName(String stockName) { this.stockName = stockName; }
    public String getEventType() { return eventType; }
    public void setEventType(String eventType) { this.eventType = eventType; }
    public LocalDate getEventDate() { return eventDate; }
    public void setEventDate(LocalDate eventDate) { this.eventDate = eventDate; }
    public BigDecimal getDividendPerShare() { return dividendPerShare; }
    public void setDividendPerShare(BigDecimal dividendPerShare) { this.dividendPerShare = dividendPerShare; }
    public LocalDate getExDividendDate() { return exDividendDate; }
    public void setExDividendDate(LocalDate exDividendDate) { this.exDividendDate = exDividendDate; }
    public LocalDate getPaymentDate() { return paymentDate; }
    public void setPaymentDate(LocalDate paymentDate) { this.paymentDate = paymentDate; }
    public String getFinancialReportType() { return financialReportType; }
    public void setFinancialReportType(String financialReportType) { this.financialReportType = financialReportType; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
