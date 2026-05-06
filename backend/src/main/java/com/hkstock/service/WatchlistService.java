package com.hkstock.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.hkstock.entity.Watchlist;
import com.hkstock.mapper.WatchlistMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 自选股服务
 */
@Service
public class WatchlistService {
    private static final Logger log = LoggerFactory.getLogger(WatchlistService.class);


    private @Autowired WatchlistMapper watchlistMapper;

    public List<Watchlist> getWatchlist() {
        return watchlistMapper.selectList(
                new LambdaQueryWrapper<Watchlist>().orderByAsc(Watchlist::getSortOrder)
        );
    }

    public void addToWatchlist(Watchlist watchlist) {
        watchlistMapper.insert(watchlist);
    }

    public void removeFromWatchlist(String stockCode) {
        watchlistMapper.delete(
                new LambdaQueryWrapper<Watchlist>().eq(Watchlist::getStockCode, stockCode)
        );
    }
}
