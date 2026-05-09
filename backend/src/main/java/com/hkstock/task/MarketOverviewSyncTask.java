package com.hkstock.task;

import com.hkstock.service.CacheInvalidationService;
import com.hkstock.service.StockService;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/** Market overview and stock master data sync tasks. */
@Component
public class MarketOverviewSyncTask {

  private static final Logger log = LoggerFactory.getLogger(MarketOverviewSyncTask.class);
  private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
  private static final String MARKET_OVERVIEW_SCRIPT = "sync_market_overview.py";

  private @Autowired PythonScriptRunner pythonScriptRunner;
  private @Autowired StockService stockService;
  private @Autowired CacheInvalidationService cacheInvalidationService;

  @Scheduled(cron = "0 0 9 * * ?")
  public void updateStockList() {
    log.info("[Stock list] Refresh started");
    stockService.refreshStockList();
    cacheInvalidationService.evictStockListCaches();
    log.info("[Stock list] Refresh completed");
  }

  @Scheduled(cron = "0 */30 9-16 * * MON-FRI")
  public void syncMarketOverviewIntraday() {
    log.info("[Market overview] Intraday sync started at {}", LocalDateTime.now().format(DF));
    pythonScriptRunner.run(MARKET_OVERVIEW_SCRIPT, "Market overview intraday sync");
    cacheInvalidationService.evictMarketOverviewCaches();
  }

  @Scheduled(cron = "0 10 17 * * MON-FRI")
  public void syncMarketOverviewClose() {
    log.info("[Market overview] Close sync started at {}", LocalDateTime.now().format(DF));
    pythonScriptRunner.run(MARKET_OVERVIEW_SCRIPT, "Market overview close sync");
    cacheInvalidationService.evictMarketOverviewCaches();
  }
}
