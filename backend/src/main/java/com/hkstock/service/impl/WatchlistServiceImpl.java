package com.hkstock.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.hkstock.domain.Watchlist;
import com.hkstock.mapper.WatchlistMapper;
import com.hkstock.service.WatchlistService;
import java.time.LocalDateTime;
import java.util.List;
import jakarta.annotation.Resource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

/** 自选股服务实现 */
@Service
public class WatchlistServiceImpl implements WatchlistService {

    private static final Logger log = LoggerFactory.getLogger(WatchlistServiceImpl.class);

    @Resource
    private WatchlistMapper watchlistMapper;

    @Override
    public List<Watchlist> getWatchlist(Long userId) {
        return watchlistMapper.selectList(
            new LambdaQueryWrapper<Watchlist>()
                .eq(Watchlist::getUserId, userId)
                .orderByAsc(Watchlist::getSortOrder));
    }

    @Override
    public void addToWatchlist(Long userId, String stockCode, String stockName) {
        // 检查是否已存在
        Watchlist existing = watchlistMapper.selectOne(
            new LambdaQueryWrapper<Watchlist>()
                .eq(Watchlist::getUserId, userId)
                .eq(Watchlist::getStockCode, stockCode));
        
        if (existing != null) {
            log.info("自选股已存在: {} - {}", stockCode, stockName);
            return;
        }

        Watchlist watchlist = new Watchlist();
        watchlist.setUserId(userId);
        watchlist.setStockCode(stockCode);
        watchlist.setStockName(stockName);
        watchlist.setSortOrder(0);
        watchlist.setCreatedAt(LocalDateTime.now());
        watchlistMapper.insert(watchlist);
    }

    @Override
    public void removeFromWatchlist(Long userId, String stockCode) {
        watchlistMapper.delete(
            new LambdaQueryWrapper<Watchlist>()
                .eq(Watchlist::getUserId, userId)
                .eq(Watchlist::getStockCode, stockCode));
    }
}
