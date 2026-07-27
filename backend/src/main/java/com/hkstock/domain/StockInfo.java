package com.hkstock.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import lombok.Data;

/** 股票基本信息 */
@Data
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
}
