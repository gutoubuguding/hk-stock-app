package com.hkstock.config;

import com.github.benmanes.caffeine.cache.Caffeine;
import java.time.Duration;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.caffeine.CaffeineCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** Local read-through cache configuration for high-frequency query APIs. */
@Configuration
@EnableCaching
public class CacheConfig {

  public static final String IPO_UPCOMING = "ipoUpcoming";
  public static final String IPO_COMPARISON = "ipoComparison";
  public static final String IPO_SECTOR_STATS = "ipoSectorStats";
  public static final String IPO_BREAK_RATE = "ipoBreakRate";
  public static final String IPO_SECTOR_LIST = "ipoSectorList";
  public static final String MARKET_OVERVIEW = "marketOverview";
  public static final String STOCK_SEARCH = "stockSearch";
  public static final String STOCK_KLINE = "stockKline";
  public static final String STOCK_DAILY_INFO = "stockDailyInfo";
  public static final String STOCK_VALUATION = "stockValuation";
  public static final String STOCK_COMPARISON = "stockComparison";

  @Bean
  public CacheManager cacheManager() {
    CaffeineCacheManager cacheManager =
        new CaffeineCacheManager(
            IPO_UPCOMING,
            IPO_COMPARISON,
            IPO_SECTOR_STATS,
            IPO_BREAK_RATE,
            IPO_SECTOR_LIST,
            MARKET_OVERVIEW,
            STOCK_SEARCH,
            STOCK_KLINE,
            STOCK_DAILY_INFO,
            STOCK_VALUATION,
            STOCK_COMPARISON);
    cacheManager.setCaffeine(
        Caffeine.newBuilder()
            .maximumSize(2_000)
            .expireAfterWrite(Duration.ofMinutes(10))
            .recordStats());
    return cacheManager;
  }
}
