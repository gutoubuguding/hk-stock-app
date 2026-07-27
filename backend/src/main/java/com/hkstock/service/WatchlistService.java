package com.hkstock.service;

import com.hkstock.domain.Watchlist;
import java.util.List;

/** 自选股服务接口 */
public interface WatchlistService {

    /** 获取自选股列表 */
    List<Watchlist> getWatchlist(Long userId);

    /** 添加自选股 */
    void addToWatchlist(Long userId, String stockCode, String stockName);

    /** 删除自选股 */
    void removeFromWatchlist(Long userId, String stockCode);
}
