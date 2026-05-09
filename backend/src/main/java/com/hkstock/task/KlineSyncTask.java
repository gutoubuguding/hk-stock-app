package com.hkstock.task;

import com.hkstock.service.CacheInvalidationService;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/** Batch K-line sync task. */
@Component
public class KlineSyncTask {

  private static final Logger log = LoggerFactory.getLogger(KlineSyncTask.class);
  private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
  private static final String KLINE_SCRIPT = "sync_daily_kline.py";

  private @Autowired PythonScriptRunner pythonScriptRunner;
  private @Autowired CacheInvalidationService cacheInvalidationService;

  @Scheduled(cron = "0 0 9 * * ?")
  public void syncAllKlineMorning() {
    log.info("[K-line sync] Morning warm-up sync started at {}", LocalDateTime.now().format(DF));
    pythonScriptRunner.run(KLINE_SCRIPT, "K-line morning warm-up sync");
    cacheInvalidationService.evictStockMarketCaches();
  }

  @Scheduled(cron = "0 0 12 * * ?")
  public void syncAllKlineNoon() {
    log.info("[K-line sync] Noon sync started at {}", LocalDateTime.now().format(DF));
    pythonScriptRunner.run(KLINE_SCRIPT, "K-line noon sync");
    cacheInvalidationService.evictStockMarketCaches();
  }

  @Scheduled(cron = "0 30 16 * * ?")
  public void syncAllKlineClose() {
    log.info("[K-line sync] Close sync started at {}", LocalDateTime.now().format(DF));
    pythonScriptRunner.run(KLINE_SCRIPT, "K-line close sync");
    cacheInvalidationService.evictStockMarketCaches();
  }
}
