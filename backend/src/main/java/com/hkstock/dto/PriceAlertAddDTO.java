package com.hkstock.dto;

import java.math.BigDecimal;
import lombok.Data;

/** 添加价格预警请求 */
@Data
public class PriceAlertAddDTO {
    private String stockCode;
    private String stockName;
    private String alertType;  // ABOVE / BELOW
    private BigDecimal targetPrice;
}
