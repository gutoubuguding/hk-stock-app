package com.hkstock.task;

import com.hkstock.service.CacheInvalidationService;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/** IPO performance, sector and break-rate metrics sync task. */
@Component
public class IpoMetricsSyncTask {

  private static final Logger log = LoggerFactory.getLogger(IpoMetricsSyncTask.class);
  private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
  private static final String IPO_METRICS_SCRIPT = "sync_ipo_kline_metrics.py";

  private @Autowired PythonScriptRunner pythonScriptRunner;
  private @Autowired CacheInvalidationService cacheInvalidationService;

  @Scheduled(cron = "0 5 17 * * MON-FRI")
  public void syncIpoComparisonMetricsAfterClose() {
    log.info("[IPO metrics sync] After-close sync started at {}", LocalDateTime.now().format(DF));
    pythonScriptRunner.run(IPO_METRICS_SCRIPT, "IPO metrics after-close sync");
    cacheInvalidationService.evictIpoMetricsCaches();
  }

  @Scheduled(cron = "0 20 20 * * ?")
  public void syncIpoComparisonMetricsEvening() {
    log.info("[IPO metrics sync] Evening compensation sync started at {}", LocalDateTime.now().format(DF));
    pythonScriptRunner.run(IPO_METRICS_SCRIPT, "IPO metrics evening sync");
    cacheInvalidationService.evictIpoMetricsCaches();
  }
}
