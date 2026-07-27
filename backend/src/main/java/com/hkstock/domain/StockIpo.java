package com.hkstock.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 新股IPO信息 */
@Data
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

    /** 各申购手数对应的真实中签/获配比例 JSON */
    private String allotmentRateTiers;

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

    /** HKEX 配发结果 PDF 链接 */
    private String hkexPdfUrl;

    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
