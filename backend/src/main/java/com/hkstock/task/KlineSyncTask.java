package com.hkstock.task;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * K 线批量同步任务。
 */
@Component
public class KlineSyncTask {

    private static final Logger log = LoggerFactory.getLogger(KlineSyncTask.class);
    private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    private static final String KLINE_SCRIPT = "sync_daily_kline.py";

    private @Autowired ScriptRunner scriptRunner;

    @Scheduled(cron = "0 0 9 * * ?")
    public void syncAllKlineMorning() {
        log.info("【K线同步】早市预热开始 (时间: {})", LocalDateTime.now().format(DF));
        scriptRunner.run(KLINE_SCRIPT, "K线同步-早市预热");
    }

    @Scheduled(cron = "0 0 12 * * ?")
    public void syncAllKlineNoon() {
        log.info("【K线同步】午间同步开始 (时间: {})", LocalDateTime.now().format(DF));
        scriptRunner.run(KLINE_SCRIPT, "K线同步-午间");
    }

    @Scheduled(cron = "0 30 16 * * ?")
    public void syncAllKlineClose() {
        log.info("【K线同步】收盘同步开始 (时间: {})", LocalDateTime.now().format(DF));
        scriptRunner.run(KLINE_SCRIPT, "K线同步-收盘");
    }
}
