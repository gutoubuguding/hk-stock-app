package com.hkstock.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.LocalDate;

/** K线数据 */
@TableName("stock_kline")
public class StockKline {

  @TableId(type = IdType.AUTO)
  private Long id;

  private String stockCode;

  /** 周期类型：D=日K, W=周K, M=月K, Y=年K */
  private String periodType;

  private LocalDate tradeDate;

  private BigDecimal openPrice;
  private BigDecimal closePrice;
  private BigDecimal highPrice;
  private BigDecimal lowPrice;

  /** 成交量 */
  private Long volume;

  /** 成交额 */
  private BigDecimal turnover;

  /** 涨跌幅 (%) */
  private BigDecimal changePercent;

  /** 换手率 (%) */
  private BigDecimal turnoverRate;

  public Long getId() {
    return id;
  }

  public void setId(Long id) {
    this.id = id;
  }

  public String getStockCode() {
    return stockCode;
  }

  public void setStockCode(String stockCode) {
    this.stockCode = stockCode;
  }

  public String getPeriodType() {
    return periodType;
  }

  public void setPeriodType(String periodType) {
    this.periodType = periodType;
  }

  public LocalDate getTradeDate() {
    return tradeDate;
  }

  public void setTradeDate(LocalDate tradeDate) {
    this.tradeDate = tradeDate;
  }

  public BigDecimal getOpenPrice() {
    return openPrice;
  }

  public void setOpenPrice(BigDecimal openPrice) {
    this.openPrice = openPrice;
  }

  public BigDecimal getClosePrice() {
    return closePrice;
  }

  public void setClosePrice(BigDecimal closePrice) {
    this.closePrice = closePrice;
  }

  public BigDecimal getHighPrice() {
    return highPrice;
  }

  public void setHighPrice(BigDecimal highPrice) {
    this.highPrice = highPrice;
  }

  public BigDecimal getLowPrice() {
    return lowPrice;
  }

  public void setLowPrice(BigDecimal lowPrice) {
    this.lowPrice = lowPrice;
  }

  public Long getVolume() {
    return volume;
  }

  public void setVolume(Long volume) {
    this.volume = volume;
  }

  public BigDecimal getTurnover() {
    return turnover;
  }

  public void setTurnover(BigDecimal turnover) {
    this.turnover = turnover;
  }

  public BigDecimal getChangePercent() {
    return changePercent;
  }

  public void setChangePercent(BigDecimal changePercent) {
    this.changePercent = changePercent;
  }

  public BigDecimal getTurnoverRate() {
    return turnoverRate;
  }

  public void setTurnoverRate(BigDecimal turnoverRate) {
    this.turnoverRate = turnoverRate;
  }
}
