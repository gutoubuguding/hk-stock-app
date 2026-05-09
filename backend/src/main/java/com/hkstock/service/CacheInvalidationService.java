package com.hkstock.service;

import com.hkstock.config.CacheConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.Cache;
import org.springframework.cache.CacheManager;
import org.springframework.stereotype.Service;

/** Clears read caches after data sync jobs write fresh market data. */
@Service
public class CacheInvalidationService {

  private static final Logger log = LoggerFactory.getLogger(CacheInvalidationService.class);

  private @Autowired CacheManager cacheManager;

  /** IPO base data changed: upcoming IPOs and derived IPO dashboards may be stale. */
  public void evictIpoDataCaches() {
    clear(
        CacheConfig.IPO_UPCOMING,
        CacheConfig.IPO_COMPARISON,
        CacheConfig.IPO_SECTOR_STATS,
        CacheConfig.IPO_BREAK_RATE,
        CacheConfig.IPO_SECTOR_LIST);
  }

  /** IPO metrics changed: comparison, sector stats and break-rate dashboards may be stale. */
  public void evictIpoMetricsCaches() {
    clear(
        CacheConfig.IPO_COMPARISON,
        CacheConfig.IPO_SECTOR_STATS,
        CacheConfig.IPO_BREAK_RATE,
        CacheConfig.IPO_SECTOR_LIST);
  }

  /** K-line or valuation data changed: stock detail and comparison caches may be stale. */
  public void evictStockMarketCaches() {
    clear(
        CacheConfig.STOCK_KLINE,
        CacheConfig.STOCK_DAILY_INFO,
        CacheConfig.STOCK_VALUATION,
        CacheConfig.STOCK_COMPARISON);
  }

  /** Stock master data changed: search and comparison caches may be stale. */
  public void evictStockListCaches() {
    clear(CacheConfig.STOCK_SEARCH, CacheConfig.STOCK_COMPARISON);
  }

  /** Market overview data changed. */
  public void evictMarketOverviewCaches() {
    clear(CacheConfig.MARKET_OVERVIEW);
  }

  private void clear(String... cacheNames) {
    for (String cacheName : cacheNames) {
      Cache cache = cacheManager.getCache(cacheName);
      if (cache == null) {
        log.warn("Cache not found, skip clear: {}", cacheName);
        continue;
      }
      cache.clear();
      log.info("Cleared cache: {}", cacheName);
    }
  }
}
