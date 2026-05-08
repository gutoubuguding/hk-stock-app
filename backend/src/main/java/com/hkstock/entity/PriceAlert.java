package com.hkstock.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** 价格预警 */
@TableName("price_alert")
public class PriceAlert {

  @TableId(type = IdType.AUTO)
  private Long id;

  private String stockCode;
  private String stockName;
  private String alertType;
  private BigDecimal targetPrice;
  private Boolean triggered;
  private LocalDateTime triggeredAt;
  private LocalDateTime createdAt;

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

  public String getAlertType() {
    return alertType;
  }

  public void setAlertType(String alertType) {
    this.alertType = alertType;
  }

  public BigDecimal getTargetPrice() {
    return targetPrice;
  }

  public void setTargetPrice(BigDecimal targetPrice) {
    this.targetPrice = targetPrice;
  }

  public Boolean getTriggered() {
    return triggered;
  }

  public void setTriggered(Boolean triggered) {
    this.triggered = triggered;
  }

  public LocalDateTime getTriggeredAt() {
    return triggeredAt;
  }

  public void setTriggeredAt(LocalDateTime triggeredAt) {
    this.triggeredAt = triggeredAt;
  }

  public LocalDateTime getCreatedAt() {
    return createdAt;
  }

  public void setCreatedAt(LocalDateTime createdAt) {
    this.createdAt = createdAt;
  }
}
