package com.hkstock.task;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/** 财报/分红日历同步任务。 */
@Component
public class CalendarSyncTask {

  private static final Logger log = LoggerFactory.getLogger(CalendarSyncTask.class);
  private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
  private static final String CALENDAR_SCRIPT = "sync_calendar_aastocks.py";

  private @Autowired ScriptRunner scriptRunner;

  @Scheduled(cron = "0 30 7 * * ?")
  public void syncCalendarMorning() {
    log.info("【日历同步】早市同步开始 (时间: {})", LocalDateTime.now().format(DF));
    scriptRunner.run(CALENDAR_SCRIPT, "日历同步-早市");
  }

  @Scheduled(cron = "0 30 18 * * ?")
  public void syncCalendarEvening() {
    log.info("【日历同步】晚市同步开始 (时间: {})", LocalDateTime.now().format(DF));
    scriptRunner.run(CALENDAR_SCRIPT, "日历同步-晚市");
  }
}
