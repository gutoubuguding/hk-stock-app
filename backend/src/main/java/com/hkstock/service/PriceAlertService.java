package com.hkstock.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.hkstock.entity.PriceAlert;
import com.hkstock.entity.StockKline;
import com.hkstock.mapper.PriceAlertMapper;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/** 价格预警服务 */
@Service
public class PriceAlertService {
  private static final Logger log = LoggerFactory.getLogger(PriceAlertService.class);

  private @Autowired PriceAlertMapper priceAlertMapper;
  private @Autowired StockService stockService;

  public List<PriceAlert> getAlerts() {
    return priceAlertMapper.selectList(
        new LambdaQueryWrapper<PriceAlert>()
            .eq(PriceAlert::getTriggered, false)
            .orderByDesc(PriceAlert::getCreatedAt));
  }

  public void addAlert(PriceAlert alert) {
    alert.setTriggered(false);
    priceAlertMapper.insert(alert);
  }

  public void deleteAlert(Long id) {
    priceAlertMapper.deleteById(id);
  }

  /** 检查未触发预警，命中后更新状态并返回本次触发列表。 */
  public List<PriceAlert> checkAlerts() {
    List<PriceAlert> activeAlerts = getAlerts();
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
          log.info(
              "价格预警触发: {} {} 目标价={} 最新收盘={}",
              alert.getStockCode(),
              alert.getAlertType(),
              alert.getTargetPrice(),
              latest.getClosePrice());
        }
      } catch (Exception e) {
        log.warn("检查价格预警失败: {} - {}", alert.getStockCode(), e.getMessage());
      }
    }
    return triggered;
  }
}
