package com.hkstock.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.LocalDateTime;
import lombok.Data;

/** 新闻信息 */
@Data
@TableName("news")
public class News {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 相关股票代码 */
    private String stockCode;

    /** 新闻标题 */
    private String title;

    /** 新闻来源 */
    private String source;

    /** 新闻链接 */
    private String url;

    /** 发布时间 */
    private LocalDateTime publishTime;

    /** AI分析结果：利好/利空/中性 */
    private String aiSentiment;

    /** AI分析摘要 */
    private String aiSummary;

    private LocalDateTime createdAt;
}
