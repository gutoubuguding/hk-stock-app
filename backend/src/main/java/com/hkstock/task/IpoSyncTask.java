package com.hkstock.task;

import com.hkstock.service.CacheInvalidationService;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/** IPO base data sync task. */
@Component
public class IpoSyncTask {

  private static final Logger log = LoggerFactory.getLogger(IpoSyncTask.class);
  private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
  private static final String IPO_SCRIPT = "sync_ipo_futu.py";

  private @Autowired PythonScriptRunner pythonScriptRunner;
  private @Autowired CacheInvalidationService cacheInvalidationService;

  @Scheduled(cron = "0 0 8 * * ?")
  public void updateIpoDataMorning() {
    log.info("[IPO sync] Morning sync started at {}", LocalDateTime.now().format(DF));
    pythonScriptRunner.run(IPO_SCRIPT, "IPO morning sync");
    cacheInvalidationService.evictIpoDataCaches();
  }

  @Scheduled(cron = "0 0 20 * * ?")
  public void updateIpoDataEvening() {
    log.info("[IPO sync] Evening sync started at {}", LocalDateTime.now().format(DF));
    pythonScriptRunner.run(IPO_SCRIPT, "IPO evening sync");
    cacheInvalidationService.evictIpoDataCaches();
  }
}
