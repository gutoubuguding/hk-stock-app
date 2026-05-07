package com.hkstock.task;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * 新股 IPO 数据与近一年新股对比指标同步任务。
 */
@Component
public class IpoSyncTask {

    private static final Logger log = LoggerFactory.getLogger(IpoSyncTask.class);
    private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    private static final String IPO_SCRIPT = "sync_ipo_futu.py";
    private static final String IPO_METRICS_SCRIPT = "sync_ipo_kline_metrics.py";

    private @Autowired ScriptRunner scriptRunner;

    @Scheduled(cron = "0 0 8 * * ?")
    public void updateIpoDataMorning() {
        log.info("【IPO同步】早市同步开始 (时间: {})", LocalDateTime.now().format(DF));
        scriptRunner.run(IPO_SCRIPT, "IPO早市同步");
    }

    @Scheduled(cron = "0 0 20 * * ?")
    public void updateIpoDataEvening() {
        log.info("【IPO同步】晚市同步开始 (时间: {})", LocalDateTime.now().format(DF));
        scriptRunner.run(IPO_SCRIPT, "IPO晚市同步");
    }

    @Scheduled(cron = "0 5 17 * * MON-FRI")
    public void syncIpoComparisonMetricsAfterClose() {
        log.info("【IPO指标同步】收盘后同步开始 (时间: {})", LocalDateTime.now().format(DF));
        scriptRunner.run(IPO_METRICS_SCRIPT, "IPO近一年对比指标-收盘");
    }

    @Scheduled(cron = "0 20 20 * * ?")
    public void syncIpoComparisonMetricsEvening() {
        log.info("【IPO指标同步】晚间补偿同步开始 (时间: {})", LocalDateTime.now().format(DF));
        scriptRunner.run(IPO_METRICS_SCRIPT, "IPO近一年对比指标-晚间");
    }
}
