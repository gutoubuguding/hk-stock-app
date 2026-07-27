package com.hkstock.controller;

import com.hkstock.common.ApiResponse;
import com.hkstock.domain.PriceAlert;
import com.hkstock.service.PriceAlertService;
import com.hkstock.utils.JWTUtil;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

/** 价格预警控制器 */
@RestController
@RequestMapping("/api/alert")
public class PriceAlertController {

    @Resource
    private PriceAlertService priceAlertService;

    @Value("${secret:}")
    private String secret;

    /** 获取当前用户ID */
    private Long getCurrentUserId(HttpServletRequest request) {
        String token = request.getHeader("token");
        if (token == null || token.isEmpty()) {
            throw new RuntimeException("未登录");
        }
        Map<String, String> claims = JWTUtil.verifyToken(token, secret, "id");
        return Long.parseLong(claims.get("id"));
    }

    /** 获取用户的价格预警 */
    @GetMapping
    public ApiResponse<List<PriceAlert>> getAlerts(HttpServletRequest request) {
        Long userId = getCurrentUserId(request);
        return ApiResponse.success(priceAlertService.getAlerts(userId));
    }

    /** 添加价格预警 */
    @PostMapping
    public ApiResponse<Void> addAlert(HttpServletRequest request, @RequestBody Map<String, Object> body) {
        Long userId = getCurrentUserId(request);
        String stockCode = (String) body.get("stockCode");
        String stockName = (String) body.get("stockName");
        String alertType = (String) body.get("alertType");
        BigDecimal targetPrice = new BigDecimal(body.get("targetPrice").toString());
        priceAlertService.addAlert(userId, stockCode, stockName, alertType, targetPrice);
        return ApiResponse.success();
    }

    /** 手动检查并返回本次触发的价格预警 */
    @PostMapping("/check")
    public ApiResponse<List<PriceAlert>> checkAlerts(HttpServletRequest request) {
        Long userId = getCurrentUserId(request);
        return ApiResponse.success(priceAlertService.checkAlerts(userId));
    }

    /** 删除价格预警 */
    @DeleteMapping("/{id}")
    public ApiResponse<Void> deleteAlert(HttpServletRequest request, @PathVariable Long id) {
        Long userId = getCurrentUserId(request);
        priceAlertService.deleteAlert(userId, id);
        return ApiResponse.success();
    }
}
