package com.hkstock.controller;

import com.hkstock.entity.StockIpo;
import com.hkstock.service.IpoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 新股相关 HTTP 接口。
 *
 * <p>前端 `IPO.vue` 主要调用这里：
 * <ul>
 *   <li>/upcoming：即将上市的新股列表；</li>
 *   <li>/comparison：近一年新股表现对比表；</li>
 *   <li>/sector-stats：按行业/板块聚合统计；</li>
 *   <li>/break-rate：整体破发率；</li>
 *   <li>/ai-analysis/{stockCode}：调用 Python AI 微服务生成单只新股分析报告。</li>
 * </ul>
 */
@RestController
@RequestMapping("/api/ipo")
public class IpoController {

    private @Autowired IpoService ipoService;

    /**
     * 获取即将上市新股列表
     */
    @GetMapping("/upcoming")
    public List<StockIpo> getUpcomingIpo() {
        return ipoService.getUpcomingIpo();
    }

    /**
     * 获取近一年上市新股横向对比表格。
     *
     * @param sortBy 前端选择的排序字段，例如 listingDate / firstDayChange / sevenDayChange
     * @param sortOrder asc 或 desc，默认 desc
     */
    @GetMapping("/comparison")
    public Map<String, Object> getIpoComparison(
            @RequestParam(required = false) String sortBy,
            @RequestParam(defaultValue = "desc") String sortOrder
    ) {
        return ipoService.getIpoComparison(sortBy, sortOrder);
    }

    /**
     * 获取新股板块统计
     */
    @GetMapping("/sector-stats")
    public Map<String, Object> getSectorStats() {
        return ipoService.getSectorStats();
    }

    /**
     * 获取破发率统计
     */
    @GetMapping("/break-rate")
    public Map<String, Object> getBreakRate() {
        return ipoService.getBreakRate();
    }

    /**
     * AI 分析新股走势。
     *
     * <p>这里只做路由转发，真正流程在 IpoService：
     * 数据库查公司名 -> 读取当前 AI 配置 -> 调用 ai-service 的 /api/analyze/ipo。
     */
    @GetMapping("/ai-analysis/{stockCode}")
    public Map<String, Object> getIpoAiAnalysis(@PathVariable String stockCode) {
        return ipoService.getAiAnalysis(stockCode);
    }

    /**
     * 手动触发新股数据更新
     */
    @PostMapping("/refresh")
    public Map<String, String> refreshIpoData() {
        ipoService.refreshIpoData();
        return Map.of("status", "success", "message", "新股数据更新已触发");
    }

    /**
     * 获取指定板块的所有新股列表
     */
    @GetMapping("/sector")
    public Map<String, Object> getIposBySector(@RequestParam String sector) {
        return ipoService.getIposBySector(sector);
    }
}
