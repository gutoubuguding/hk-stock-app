package com.hkstock.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.LocalDateTime;
import lombok.Data;

/** 自选股 */
@Data
@TableName("watchlist")
public class Watchlist {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 用户ID */
    private Long userId;

    private String stockCode;
    private String stockName;

    /** 排序权重 */
    private Integer sortOrder;

    private LocalDateTime createdAt;
}
