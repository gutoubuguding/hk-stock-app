package com.hkstock.vo;

import java.math.BigDecimal;
import java.time.LocalDate;
import lombok.Data;

/** 估值指标视图对象 */
@Data
public class StockValuationVO {
    private String stockCode;
    private BigDecimal pe;
    private BigDecimal pb;
    private BigDecimal dividendYield;
    private BigDecimal marketCap;
    private LocalDate dataDate;
}
