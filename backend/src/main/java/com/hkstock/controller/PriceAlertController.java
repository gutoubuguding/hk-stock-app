package com.hkstock.controller;

import com.hkstock.entity.PriceAlert;
import com.hkstock.service.PriceAlertService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 价格预警控制器
 */
@RestController
@RequestMapping("/api/alert")
public class PriceAlertController {

    private @Autowired PriceAlertService priceAlertService;

    /**
     * 获取所有价格预警
     */
    @GetMapping
    public List<PriceAlert> getAlerts() {
        return priceAlertService.getAlerts();
    }

    /**
     * 添加价格预警
     */
    @PostMapping
    public Map<String, String> addAlert(@RequestBody PriceAlert alert) {
        priceAlertService.addAlert(alert);
        return Map.of("status", "success");
    }

    /**
     * 手动检查并返回本次触发的价格预警
     */
    @PostMapping("/check")
    public List<PriceAlert> checkAlerts() {
        return priceAlertService.checkAlerts();
    }

    /**
     * 删除价格预警
     */
    @DeleteMapping("/{id}")
    public Map<String, String> deleteAlert(@PathVariable Long id) {
        priceAlertService.deleteAlert(id);
        return Map.of("status", "success");
    }
}
