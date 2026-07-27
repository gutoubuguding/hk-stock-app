package com.hkstock.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.math.BigDecimal;
import java.time.LocalDate;
import lombok.Data;

/** K线数据 */
@Data
@TableName("stock_kline")
public class StockKline {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String stockCode;

    /** 周期类型：D=日K, W=周K, M=月K, Y=年K */
    private String periodType;

    private LocalDate tradeDate;

    private BigDecimal openPrice;
    private BigDecimal closePrice;
    private BigDecimal highPrice;
    private BigDecimal lowPrice;

    /** 成交量 */
    private Long volume;

    /** 成交额 */
    private BigDecimal turnover;

    /** 涨跌幅 (%) */
    private BigDecimal changePercent;

    /** 换手率 (%) */
    private BigDecimal turnoverRate;
}
