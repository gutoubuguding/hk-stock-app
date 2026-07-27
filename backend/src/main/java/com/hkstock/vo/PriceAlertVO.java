package com.hkstock.vo;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import lombok.Data;

/** 价格预警视图对象 */
@Data
public class PriceAlertVO {
    private Long id;
    private String stockCode;
    private String stockName;
    private String alertType;
    private BigDecimal targetPrice;
    private Boolean triggered;
    private LocalDateTime triggeredAt;
    private LocalDateTime createdAt;
}
