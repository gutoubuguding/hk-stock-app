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

/** 新股 IPO 数据与近一年新股对比指标同步任务。 */
@Component
public class IpoSyncTask {

  private static final Logger log = LoggerFactory.getLogger(IpoSyncTask.class);
  private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
  private static final String IPO_SCRIPT = "sync_ipo_futu.py";
  private static final String IPO_METRICS_SCRIPT = "sync_ipo_kline_metrics.py";

  private @Autowired ScriptRunner scriptRunner;
  private @Autowired CacheManager cacheManager;

  @Scheduled(cron = "0 0 8 * * ?")
  public void updateIpoDataMorning() {
    log.info("【IPO同步】早市同步开始 (时间: {})", LocalDateTime.now().format(DF));
    scriptRunner.run(IPO_SCRIPT, "IPO早市同步");
    clearIpoCaches();
  }

  @Scheduled(cron = "0 0 20 * * ?")
  public void updateIpoDataEvening() {
    log.info("【IPO同步】晚市同步开始 (时间: {})", LocalDateTime.now().format(DF));
    scriptRunner.run(IPO_SCRIPT, "IPO晚市同步");
    clearIpoCaches();
  }

  @Scheduled(cron = "0 5 17 * * MON-FRI")
  public void syncIpoComparisonMetricsAfterClose() {
    log.info("【IPO指标同步】收盘后同步开始 (时间: {})", LocalDateTime.now().format(DF));
    scriptRunner.run(IPO_METRICS_SCRIPT, "IPO近一年对比指标-收盘");
    clearIpoCaches();
  }

  @Scheduled(cron = "0 20 20 * * ?")
  public void syncIpoComparisonMetricsEvening() {
    log.info("【IPO指标同步】晚间补偿同步开始 (时间: {})", LocalDateTime.now().format(DF));
    scriptRunner.run(IPO_METRICS_SCRIPT, "IPO近一年对比指标-晚间");
    clearIpoCaches();
  }

  private void clearIpoCaches() {
    clear(CacheConfig.IPO_UPCOMING);
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
