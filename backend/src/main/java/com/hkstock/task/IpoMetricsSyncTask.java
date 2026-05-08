package com.hkstock.task;

import com.hkstock.config.CacheConfig;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.Cache;
import org.springframework.cache.CacheManager;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/** 近一年 IPO 对比、板块统计和破发率等衍生指标同步任务。 */
@Component
public class IpoMetricsSyncTask {

  private static final Logger log = LoggerFactory.getLogger(IpoMetricsSyncTask.class);
  private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
  private static final String IPO_METRICS_SCRIPT = "sync_ipo_kline_metrics.py";

  private @Autowired PythonScriptRunner pythonScriptRunner;
  private @Autowired CacheManager cacheManager;

  @Scheduled(cron = "0 5 17 * * MON-FRI")
  public void syncIpoComparisonMetricsAfterClose() {
    log.info("【IPO指标同步】收盘后同步开始 (时间: {})", LocalDateTime.now().format(DF));
    pythonScriptRunner.run(IPO_METRICS_SCRIPT, "IPO近一年对比指标-收盘");
    clearIpoCaches();
  }

  @Scheduled(cron = "0 20 20 * * ?")
  public void syncIpoComparisonMetricsEvening() {
    log.info("【IPO指标同步】晚间补偿同步开始 (时间: {})", LocalDateTime.now().format(DF));
    pythonScriptRunner.run(IPO_METRICS_SCRIPT, "IPO近一年对比指标-晚间");
    clearIpoCaches();
  }

  private void clearIpoCaches() {
    clear(CacheConfig.IPO_COMPARISON);
    clear(CacheConfig.IPO_SECTOR_STATS);
    clear(CacheConfig.IPO_BREAK_RATE);
    clear(CacheConfig.IPO_SECTOR_LIST);
  }

  private void clear(String cacheName) {
    Cache cache = cacheManager.getCache(cacheName);
    if (cache != null) {
      cache.clear();
    }
  }
}
