package com.hkstock.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 估值指标 */
@Data
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
}
