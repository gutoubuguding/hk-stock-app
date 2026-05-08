package com.hkstock.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/** 估值指标 */
@TableName("stock_valuation")
public class StockValuation {

  @TableId(type = IdType.AUTO)
  private Long id;

  private String stockCode;

  /** 市盈率 PE */
  private BigDecimal pe;

  /** 市净率 PB */
  private BigDecimal pb;

  /** 股息率 (%) */
  private BigDecimal dividendYield;

  /** 总市值（港元） */
  private BigDecimal marketCap;

  /** 数据日期 */
  private LocalDate dataDate;

  private LocalDateTime updatedAt;

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

  public BigDecimal getPe() {
    return pe;
  }

  public void setPe(BigDecimal pe) {
    this.pe = pe;
  }

  public BigDecimal getPb() {
    return pb;
  }

  public void setPb(BigDecimal pb) {
    this.pb = pb;
  }

  public BigDecimal getDividendYield() {
    return dividendYield;
  }

  public void setDividendYield(BigDecimal dividendYield) {
    this.dividendYield = dividendYield;
  }

  public BigDecimal getMarketCap() {
    return marketCap;
  }

  public void setMarketCap(BigDecimal marketCap) {
    this.marketCap = marketCap;
  }

  public LocalDate getDataDate() {
    return dataDate;
  }

  public void setDataDate(LocalDate dataDate) {
    this.dataDate = dataDate;
  }

  public LocalDateTime getUpdatedAt() {
    return updatedAt;
  }

  public void setUpdatedAt(LocalDateTime updatedAt) {
    this.updatedAt = updatedAt;
  }
}
