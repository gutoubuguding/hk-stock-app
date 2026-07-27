package com.hkstock.service;

import com.hkstock.domain.PriceAlert;
import java.math.BigDecimal;
import java.util.List;

/** 价格预警服务接口 */
public interface PriceAlertService {

    /** 获取用户的价格预警 */
    List<PriceAlert> getAlerts(Long userId);

    /** 添加价格预警 */
    void addAlert(Long userId, String stockCode, String stockName, String alertType, BigDecimal targetPrice);

    /** 删除价格预警 */
    void deleteAlert(Long userId, Long id);

    /** 检查并返回触发的预警 */
    List<PriceAlert> checkAlerts(Long userId);

    /** 检查所有用户的预警（定时任务用） */
    List<PriceAlert> checkAllAlerts();
}
