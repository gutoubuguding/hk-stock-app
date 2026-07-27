package com.hkstock.vo;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 自选股视图对象 */
@Data
public class WatchlistVO {
    private Long id;
    private String stockCode;
    private String stockName;
    private Integer sortOrder;
    private LocalDateTime createdAt;
}
