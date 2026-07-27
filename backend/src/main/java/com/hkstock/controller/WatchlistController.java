package com.hkstock.controller;

import com.hkstock.common.ApiResponse;
import com.hkstock.domain.Watchlist;
import com.hkstock.service.WatchlistService;
import com.hkstock.utils.JWTUtil;
import jakarta.annotation.Resource;
import jakarta.servlet.http.HttpServletRequest;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

/** 自选股控制器 */
@RestController
@RequestMapping("/api/watchlist")
public class WatchlistController {

    @Resource
    private WatchlistService watchlistService;

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

    /** 获取自选股列表 */
    @GetMapping
    public ApiResponse<List<Watchlist>> getWatchlist(HttpServletRequest request) {
        Long userId = getCurrentUserId(request);
        return ApiResponse.success(watchlistService.getWatchlist(userId));
    }

    /** 添加自选股 */
    @PostMapping
    public ApiResponse<Void> addToWatchlist(HttpServletRequest request, @RequestBody Map<String, String> body) {
        Long userId = getCurrentUserId(request);
        String stockCode = body.get("stockCode");
        String stockName = body.get("stockName");
        watchlistService.addToWatchlist(userId, stockCode, stockName);
        return ApiResponse.success();
    }

    /** 删除自选股 */
    @DeleteMapping("/{stockCode}")
    public ApiResponse<Void> removeFromWatchlist(HttpServletRequest request, @PathVariable String stockCode) {
        Long userId = getCurrentUserId(request);
        watchlistService.removeFromWatchlist(userId, stockCode);
        return ApiResponse.success();
    }
}
