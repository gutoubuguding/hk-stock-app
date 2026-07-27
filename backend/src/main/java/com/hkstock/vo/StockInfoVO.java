package com.hkstock.vo;

import java.math.BigDecimal;
import lombok.Data;

/** 股票信息视图对象 */
@Data
public class StockInfoVO {
    private String stockCode;
    private String stockName;
    private String sector;
    private Boolean isHkStockConnect;
    private BigDecimal marketCap;
}
