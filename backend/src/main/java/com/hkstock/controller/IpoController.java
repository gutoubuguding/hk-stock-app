package com.hkstock.controller;

import com.hkstock.common.ApiResponse;
import com.hkstock.domain.StockIpo;
import com.hkstock.service.IpoService;
import jakarta.annotation.Resource;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.*;

/** 新股相关 HTTP 接口 */
@RestController
@RequestMapping("/api/ipo")
public class IpoController {

    @Resource
    private IpoService ipoService;

    /** 获取即将上市新股列表 */
    @GetMapping("/upcoming")
    public ApiResponse<List<StockIpo>> getUpcomingIpo() {
        return ApiResponse.success(ipoService.getUpcomingIpo());
    }

    /** 获取近一年上市新股横向对比表格 */
    @GetMapping("/comparison")
    public ApiResponse<Map<String, Object>> getIpoComparison(
        @RequestParam(required = false) String sortBy,
        @RequestParam(defaultValue = "desc") String sortOrder) {
        return ApiResponse.success(ipoService.getIpoComparison(sortBy, sortOrder));
    }

    /** 获取新股板块统计 */
    @GetMapping("/sector-stats")
    public ApiResponse<Map<String, Object>> getSectorStats() {
        return ApiResponse.success(ipoService.getSectorStats());
    }

    /** 获取破发率统计 */
    @GetMapping("/break-rate")
    public ApiResponse<Map<String, Object>> getBreakRate() {
        return ApiResponse.success(ipoService.getBreakRate());
    }

    /** AI 分析新股走势 */
    @GetMapping("/ai-analysis/{stockCode}")
    public ApiResponse<Map<String, Object>> getIpoAiAnalysis(@PathVariable String stockCode) {
        return ApiResponse.success(ipoService.getAiAnalysis(stockCode));
    }

    /** 手动触发新股数据更新 */
    @PostMapping("/refresh")
    public ApiResponse<Map<String, String>> refreshIpoData() {
        ipoService.refreshIpoData();
        return ApiResponse.success(Map.of("status", "success", "message", "新股数据更新已触发"));
    }

    /** 获取指定板块的所有新股列表 */
    @GetMapping("/sector")
    public ApiResponse<Map<String, Object>> getIposBySector(@RequestParam String sector) {
        return ApiResponse.success(ipoService.getIposBySector(sector));
    }
}
