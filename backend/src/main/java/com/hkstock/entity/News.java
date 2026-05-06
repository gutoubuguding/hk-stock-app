package com.hkstock.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import java.time.LocalDateTime;

/**
 * 新闻信息
 */
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

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getStockCode() {
        return stockCode;
    }

    public void setStockCode(String stockCode) {
        this.stockCode = stockCode;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public LocalDateTime getPublishTime() {
        return publishTime;
    }

    public void setPublishTime(LocalDateTime publishTime) {
        this.publishTime = publishTime;
    }

    public String getAiSentiment() {
        return aiSentiment;
    }

    public void setAiSentiment(String aiSentiment) {
        this.aiSentiment = aiSentiment;
    }

    public String getAiSummary() {
        return aiSummary;
    }

    public void setAiSummary(String aiSummary) {
        this.aiSummary = aiSummary;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
