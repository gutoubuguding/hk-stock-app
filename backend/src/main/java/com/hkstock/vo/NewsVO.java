package com.hkstock.vo;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import lombok.Data;

/** 新闻视图对象 */
@Data
public class NewsVO {
    private Long id;
    private String stockCode;
    private String title;
    private String source;
    private String url;
    private LocalDateTime publishTime;
    private String aiSentiment;
    private String aiSummary;
}
