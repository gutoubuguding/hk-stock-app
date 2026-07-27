package com.hkstock.vo;

import java.math.BigDecimal;
import java.time.LocalDate;
import lombok.Data;

/** K线数据视图对象 */
@Data
public class StockKlineVO {
    private String stockCode;
    private String periodType;
    private LocalDate tradeDate;
    private BigDecimal openPrice;
    private BigDecimal closePrice;
    private BigDecimal highPrice;
    private BigDecimal lowPrice;
    private Long volume;
    private BigDecimal turnover;
    private BigDecimal changePercent;
    private BigDecimal turnoverRate;
}
