package com.hkstock.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.hkstock.domain.PriceAlert;
import com.hkstock.domain.StockKline;
import com.hkstock.mapper.PriceAlertMapper;
import com.hkstock.service.PriceAlertService;
import com.hkstock.service.StockService;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import jakarta.annotation.Resource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

/** 价格预警服务实现 */
@Service
public class PriceAlertServiceImpl implements PriceAlertService {

    private static final Logger log = LoggerFactory.getLogger(PriceAlertServiceImpl.class);

    @Resource
    private PriceAlertMapper priceAlertMapper;
    @Resource
    private StockService stockService;

    @Override
    public List<PriceAlert> getAlerts(Long userId) {
        return priceAlertMapper.selectList(
            new LambdaQueryWrapper<PriceAlert>()
                .eq(PriceAlert::getUserId, userId)
                .eq(PriceAlert::getTriggered, false)
                .orderByDesc(PriceAlert::getCreatedAt));
    }

    @Override
    public void addAlert(Long userId, String stockCode, String stockName, String alertType, BigDecimal targetPrice) {
        PriceAlert alert = new PriceAlert();
        alert.setUserId(userId);
        alert.setStockCode(stockCode);
        alert.setStockName(stockName);
        alert.setAlertType(alertType);
        alert.setTargetPrice(targetPrice);
        alert.setTriggered(false);
        alert.setCreatedAt(LocalDateTime.now());
        priceAlertMapper.insert(alert);
    }

    @Override
    public void deleteAlert(Long userId, Long id) {
        priceAlertMapper.delete(
            new LambdaQueryWrapper<PriceAlert>()
                .eq(PriceAlert::getId, id)
                .eq(PriceAlert::getUserId, userId));
    }

    @Override
    public List<PriceAlert> checkAlerts(Long userId) {
        List<PriceAlert> activeAlerts = getAlerts(userId);
        List<PriceAlert> triggered = new ArrayList<>();
        for (PriceAlert alert : activeAlerts) {
            try {
                StockKline latest = stockService.getLatestDailyInfo(alert.getStockCode());
                if (latest == null || latest.getClosePrice() == null || alert.getTargetPrice() == null) {
                    continue;
                }
                int cmp = latest.getClosePrice().compareTo(alert.getTargetPrice());
                boolean hit = "ABOVE".equalsIgnoreCase(alert.getAlertType()) ? cmp >= 0 : cmp <= 0;
                if (hit) {
                    alert.setTriggered(true);
                    alert.setTriggeredAt(LocalDateTime.now());
                    priceAlertMapper.updateById(alert);
                    triggered.add(alert);
                    log.info("价格预警触发: {} {} 目标价={} 最新收盘={}",
                        alert.getStockCode(), alert.getAlertType(),
                        alert.getTargetPrice(), latest.getClosePrice());
                }
            } catch (Exception e) {
                log.warn("检查价格预警失败: {} - {}", alert.getStockCode(), e.getMessage());
            }
        }
        return triggered;
    }

    @Override
    public List<PriceAlert> checkAllAlerts() {
        List<PriceAlert> activeAlerts = priceAlertMapper.selectList(
            new LambdaQueryWrapper<PriceAlert>()
                .eq(PriceAlert::getTriggered, false));
        List<PriceAlert> triggered = new ArrayList<>();
        for (PriceAlert alert : activeAlerts) {
            try {
                StockKline latest = stockService.getLatestDailyInfo(alert.getStockCode());
                if (latest == null || latest.getClosePrice() == null || alert.getTargetPrice() == null) {
                    continue;
                }
                int cmp = latest.getClosePrice().compareTo(alert.getTargetPrice());
                boolean hit = "ABOVE".equalsIgnoreCase(alert.getAlertType()) ? cmp >= 0 : cmp <= 0;
                if (hit) {
                    alert.setTriggered(true);
                    alert.setTriggeredAt(LocalDateTime.now());
                    priceAlertMapper.updateById(alert);
                    triggered.add(alert);
                    log.info("价格预警触发: {} {} 目标价={} 最新收盘={}",
                        alert.getStockCode(), alert.getAlertType(),
                        alert.getTargetPrice(), latest.getClosePrice());
                }
            } catch (Exception e) {
                log.warn("检查价格预警失败: {} - {}", alert.getStockCode(), e.getMessage());
            }
        }
        return triggered;
    }
}
