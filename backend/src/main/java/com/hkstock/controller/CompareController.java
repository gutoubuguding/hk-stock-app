package com.hkstock.controller;

import com.hkstock.common.ApiResponse;
import com.hkstock.service.StockService;
import jakarta.annotation.Resource;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.*;

/** 股票对比控制器 */
@RestController
@RequestMapping("/api/compare")
public class CompareController {

    @Resource
    private StockService stockService;

    /** 对比多只股票 */
    @GetMapping
    public ApiResponse<Map<String, Object>> compareStocks(
        @RequestParam String stockCodes,
        @RequestParam(defaultValue = "pe,pb,change,volume,marketCap") String metrics) {
        List<String> codes = List.of(stockCodes.split(","));
        return ApiResponse.success(stockService.compareStocks(codes, metrics));
    }
}
