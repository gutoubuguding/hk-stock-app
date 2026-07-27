package com.hkstock.query;

import lombok.Data;

/** K线数据查询参数 */
@Data
public class KlineQuery {
    private String stockCode;
    private String periodType = "D";
    private Integer days = 120;
}
