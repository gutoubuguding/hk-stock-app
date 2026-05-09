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

/** 行情概览与股票列表同步任务。 */
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
    log.info("【股票列表】开始更新");
    stockService.refreshStockList();
    cacheInvalidationService.evictStockListCaches();
    log.info("【股票列表】更新完成");
  }

  @Scheduled(cron = "0 */30 9-16 * * MON-FRI")
  public void syncMarketOverviewIntraday() {
    log.info("【大盘概览】盘中同步开始 (时间: {})", LocalDateTime.now().format(DF));
    pythonScriptRunner.run(MARKET_OVERVIEW_SCRIPT, "大盘概览-盘中");
    cacheInvalidationService.evictMarketOverviewCaches();
  }

  @Scheduled(cron = "0 10 17 * * MON-FRI")
  public void syncMarketOverviewClose() {
    log.info("【大盘概览】收盘后同步开始 (时间: {})", LocalDateTime.now().format(DF));
    pythonScriptRunner.run(MARKET_OVERVIEW_SCRIPT, "大盘概览-收盘");
    cacheInvalidationService.evictMarketOverviewCaches();
  }
}
