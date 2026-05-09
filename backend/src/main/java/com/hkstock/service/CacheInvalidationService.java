package com.hkstock.service;

import com.hkstock.config.CacheConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.Cache;
import org.springframework.cache.CacheManager;
import org.springframework.stereotype.Service;

/** 数据同步完成后的缓存清理服务，避免同步脚本写入新数据后接口仍命中旧缓存。 */
@Service
public class CacheInvalidationService {

  private static final Logger log = LoggerFactory.getLogger(CacheInvalidationService.class);

  private @Autowired CacheManager cacheManager;

  /** IPO 基础数据变更后，清理所有 IPO 相关查询缓存。 */
  public void evictIpoDataCaches() {
    clear(
        CacheConfig.IPO_UPCOMING,
        CacheConfig.IPO_COMPARISON,
        CacheConfig.IPO_SECTOR_STATS,
        CacheConfig.IPO_BREAK_RATE,
        CacheConfig.IPO_SECTOR_LIST);
  }

  /** IPO 衍生指标变更后，清理依赖指标/K 线统计的 IPO 缓存。 */
  public void evictIpoMetricsCaches() {
    clear(
        CacheConfig.IPO_COMPARISON,
        CacheConfig.IPO_SECTOR_STATS,
        CacheConfig.IPO_BREAK_RATE,
        CacheConfig.IPO_SECTOR_LIST);
  }

  /** K 线、估值等行情数据变更后，清理个股行情相关缓存。 */
  public void evictStockMarketCaches() {
    clear(
        CacheConfig.STOCK_KLINE,
        CacheConfig.STOCK_DAILY_INFO,
        CacheConfig.STOCK_VALUATION,
        CacheConfig.STOCK_COMPARISON);
  }

  /** 股票基础列表变更后，清理搜索与股票对比缓存。 */
  public void evictStockListCaches() {
    clear(CacheConfig.STOCK_SEARCH, CacheConfig.STOCK_COMPARISON);
  }

  /** 大盘概览数据变更后，清理大盘概览缓存。 */
  public void evictMarketOverviewCaches() {
    clear(CacheConfig.MARKET_OVERVIEW);
  }

  private void clear(String... cacheNames) {
    for (String cacheName : cacheNames) {
      Cache cache = cacheManager.getCache(cacheName);
      if (cache == null) {
        log.warn("缓存不存在，跳过清理: {}", cacheName);
        continue;
      }
      cache.clear();
      log.info("已清理缓存: {}", cacheName);
    }
  }
}
