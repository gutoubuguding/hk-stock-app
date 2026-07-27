package com.hkstock.dto;

import lombok.Data;

/** 添加自选股请求 */
@Data
public class WatchlistAddDTO {
    private String stockCode;
    private String stockName;
    private Integer sortOrder = 0;
}
