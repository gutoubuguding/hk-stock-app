package com.hkstock.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import lombok.Data;

/** 价格预警 */
@Data
@TableName("price_alert")
public class PriceAlert {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 用户ID */
    private Long userId;

    private String stockCode;
    private String stockName;
    private String alertType;
    private BigDecimal targetPrice;
    private Boolean triggered;
    private LocalDateTime triggeredAt;
    private LocalDateTime createdAt;
}
