package com.hkstock.task;

import com.hkstock.service.PriceAlertService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/**
 * 价格预警检查任务。
 */
@Component
public class PriceAlertTask {

    private static final Logger log = LoggerFactory.getLogger(PriceAlertTask.class);

    private @Autowired PriceAlertService priceAlertService;

    @Scheduled(cron = "0 */5 9-16 * * MON-FRI")
    public void checkPriceAlertsIntraday() {
        int count = priceAlertService.checkAlerts().size();
        if (count > 0) {
            log.info("【价格预警】本次触发 {} 条", count);
        }
    }
}
