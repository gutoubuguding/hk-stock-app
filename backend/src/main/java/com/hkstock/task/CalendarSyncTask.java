package com.hkstock.task;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/** Earnings and dividend calendar sync task. */
@Component
public class CalendarSyncTask {

  private static final Logger log = LoggerFactory.getLogger(CalendarSyncTask.class);
  private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
  private static final String CALENDAR_SCRIPT = "sync_calendar_aastocks.py";

  private @Autowired PythonScriptRunner pythonScriptRunner;

  @Scheduled(cron = "0 30 7 * * ?")
  public void syncCalendarMorning() {
    log.info("[Calendar sync] Morning sync started at {}", LocalDateTime.now().format(DF));
    pythonScriptRunner.run(CALENDAR_SCRIPT, "Calendar morning sync");
  }

  @Scheduled(cron = "0 30 18 * * ?")
  public void syncCalendarEvening() {
    log.info("[Calendar sync] Evening sync started at {}", LocalDateTime.now().format(DF));
    pythonScriptRunner.run(CALENDAR_SCRIPT, "Calendar evening sync");
  }
}
