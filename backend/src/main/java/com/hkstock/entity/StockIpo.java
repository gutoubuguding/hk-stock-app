package com.hkstock.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/** 新股IPO信息 */
@TableName("stock_ipo")
public class StockIpo {

  @TableId(type = IdType.AUTO)
  private Long id;

  private String stockCode;
  private String stockName;

  /** 行业/板块 */
  private String sector;

  /** 招股期开始 */
  private LocalDate subscriptionStart;

  /** 招股期结束 */
  private LocalDate subscriptionEnd;

  /** 定价日 */
  private LocalDate pricingDate;

  /** 公布中签日 */
  private LocalDate allotmentDate;

  /** 上市日 */
  private LocalDate listingDate;

  /** 发行价 */
  private BigDecimal issuePrice;

  /** 每手入场费 */
  private BigDecimal entryFee;

  /** 募资金额 */
  private BigDecimal fundraisingAmount;

  /** 认购中签率 (%) */
  private BigDecimal allotmentRate;

  /** 公开发售倍数（超购倍数） */
  private BigDecimal oversubscriptionRatio;

  /** 公开发售比例 (%) */
  private BigDecimal publicOfferingRatio;

  /** 国际配售比例 (%) */
  private BigDecimal internationalPlacementRatio;

  /** 保荐人 */
  private String sponsor;

  /** 基石投资者 */
  private String cornerstoneInvestor;

  /** 基石投资金额 */
  private BigDecimal cornerstoneAmount;

  /** 发行市盈率 */
  @TableField("issue_pe")
  private BigDecimal issuePE;

  /** 同行业平均市盈率 */
  @TableField("industry_avg_pe")
  private BigDecimal industryAvgPE;

  /** 是否纳入港股通 */
  private Boolean isHkStockConnect;

  /** 上市首日涨跌幅 (%) */
  private BigDecimal firstDayChange;

  /** 上市后7天涨跌幅 (%) */
  private BigDecimal sevenDayChange;

  /** 上市后30天涨跌幅 (%) */
  private BigDecimal thirtyDayChange;

  /** 发行价 vs 现价涨跌幅 (%) */
  private BigDecimal currentChange;

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

  public LocalDate getSubscriptionStart() {
    return subscriptionStart;
  }

  public void setSubscriptionStart(LocalDate subscriptionStart) {
    this.subscriptionStart = subscriptionStart;
  }

  public LocalDate getSubscriptionEnd() {
    return subscriptionEnd;
  }

  public void setSubscriptionEnd(LocalDate subscriptionEnd) {
    this.subscriptionEnd = subscriptionEnd;
  }

  public LocalDate getPricingDate() {
    return pricingDate;
  }

  public void setPricingDate(LocalDate pricingDate) {
    this.pricingDate = pricingDate;
  }

  public LocalDate getAllotmentDate() {
    return allotmentDate;
  }

  public void setAllotmentDate(LocalDate allotmentDate) {
    this.allotmentDate = allotmentDate;
  }

  public LocalDate getListingDate() {
    return listingDate;
  }

  public void setListingDate(LocalDate listingDate) {
    this.listingDate = listingDate;
  }

  public BigDecimal getIssuePrice() {
    return issuePrice;
  }

  public void setIssuePrice(BigDecimal issuePrice) {
    this.issuePrice = issuePrice;
  }

  public BigDecimal getEntryFee() {
    return entryFee;
  }

  public void setEntryFee(BigDecimal entryFee) {
    this.entryFee = entryFee;
  }

  public BigDecimal getFundraisingAmount() {
    return fundraisingAmount;
  }

  public void setFundraisingAmount(BigDecimal fundraisingAmount) {
    this.fundraisingAmount = fundraisingAmount;
  }

  public BigDecimal getAllotmentRate() {
    return allotmentRate;
  }

  public void setAllotmentRate(BigDecimal allotmentRate) {
    this.allotmentRate = allotmentRate;
  }

  public BigDecimal getOversubscriptionRatio() {
    return oversubscriptionRatio;
  }

  public void setOversubscriptionRatio(BigDecimal oversubscriptionRatio) {
    this.oversubscriptionRatio = oversubscriptionRatio;
  }

  public BigDecimal getPublicOfferingRatio() {
    return publicOfferingRatio;
  }

  public void setPublicOfferingRatio(BigDecimal publicOfferingRatio) {
    this.publicOfferingRatio = publicOfferingRatio;
  }

  public BigDecimal getInternationalPlacementRatio() {
    return internationalPlacementRatio;
  }

  public void setInternationalPlacementRatio(BigDecimal internationalPlacementRatio) {
    this.internationalPlacementRatio = internationalPlacementRatio;
  }

  public String getSponsor() {
    return sponsor;
  }

  public void setSponsor(String sponsor) {
    this.sponsor = sponsor;
  }

  public String getCornerstoneInvestor() {
    return cornerstoneInvestor;
  }

  public void setCornerstoneInvestor(String cornerstoneInvestor) {
    this.cornerstoneInvestor = cornerstoneInvestor;
  }

  public BigDecimal getCornerstoneAmount() {
    return cornerstoneAmount;
  }

  public void setCornerstoneAmount(BigDecimal cornerstoneAmount) {
    this.cornerstoneAmount = cornerstoneAmount;
  }

  public BigDecimal getIssuePE() {
    return issuePE;
  }

  public void setIssuePE(BigDecimal issuePE) {
    this.issuePE = issuePE;
  }

  public BigDecimal getIndustryAvgPE() {
    return industryAvgPE;
  }

  public void setIndustryAvgPE(BigDecimal industryAvgPE) {
    this.industryAvgPE = industryAvgPE;
  }

  public Boolean getIsHkStockConnect() {
    return isHkStockConnect;
  }

  public void setIsHkStockConnect(Boolean isHkStockConnect) {
    this.isHkStockConnect = isHkStockConnect;
  }

  public BigDecimal getFirstDayChange() {
    return firstDayChange;
  }

  public void setFirstDayChange(BigDecimal firstDayChange) {
    this.firstDayChange = firstDayChange;
  }

  public BigDecimal getSevenDayChange() {
    return sevenDayChange;
  }

  public void setSevenDayChange(BigDecimal sevenDayChange) {
    this.sevenDayChange = sevenDayChange;
  }

  public BigDecimal getThirtyDayChange() {
    return thirtyDayChange;
  }

  public void setThirtyDayChange(BigDecimal thirtyDayChange) {
    this.thirtyDayChange = thirtyDayChange;
  }

  public BigDecimal getCurrentChange() {
    return currentChange;
  }

  public void setCurrentChange(BigDecimal currentChange) {
    this.currentChange = currentChange;
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
