package com.hkstock.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** 股票基本信息 */
@TableName("stock_info")
public class StockInfo {

  @TableId(type = IdType.AUTO)
  private Long id;

  /** 股票代码，如 "00700" */
  private String stockCode;

  /** 股票名称，如 "腾讯控股" */
  private String stockName;

  /** 板块/行业 */
  private String sector;

  /** 是否纳入港股通 */
  private Boolean isHkStockConnect;

  /** 总市值（港元） */
  private BigDecimal marketCap;

  private LocalDateTime createdAt;
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

  public String getStockName() {
    return stockName;
  }

  public void setStockName(String stockName) {
    this.stockName = stockName;
  }

  public String getSector() {
    return sector;
  }

  public void setSector(String sector) {
    this.sector = sector;
  }

  public Boolean getIsHkStockConnect() {
    return isHkStockConnect;
  }

  public void setIsHkStockConnect(Boolean isHkStockConnect) {
    this.isHkStockConnect = isHkStockConnect;
  }

  public BigDecimal getMarketCap() {
    return marketCap;
  }

  public void setMarketCap(BigDecimal marketCap) {
    this.marketCap = marketCap;
  }

  public LocalDateTime getCreatedAt() {
    return createdAt;
  }

  public void setCreatedAt(LocalDateTime createdAt) {
    this.createdAt = createdAt;
  }

  public LocalDateTime getUpdatedAt() {
    return updatedAt;
  }

  public void setUpdatedAt(LocalDateTime updatedAt) {
    this.updatedAt = updatedAt;
  }
}
