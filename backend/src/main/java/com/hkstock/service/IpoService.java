package com.hkstock.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.toolkit.support.SFunction;
import com.hkstock.config.CacheConfig;
import com.hkstock.entity.StockIpo;
import com.hkstock.exception.AiServiceException;
import com.hkstock.exception.BusinessException;
import com.hkstock.exception.DataSyncException;
import com.hkstock.mapper.StockIpoMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.regex.Pattern;

/**
 * 新股服务
 */
@Service
public class IpoService {

    private static final Logger log = LoggerFactory.getLogger(IpoService.class);
    private static final Pattern HK_STOCK_CODE_PATTERN = Pattern.compile("^(HK\\.)?\\d{5}$");
    /**
     * 板块样本数太少时，均值/破发率容易被单只股票扭曲，前端展示也会非常杂乱。
     * 默认只展示最近一年内至少 3 只新股的板块，少于 3 只的板块仍计入汇总元数据。
     */
    private static final int MIN_SECTOR_SAMPLE_SIZE = 3;

    private @Autowired StockIpoMapper ipoMapper;
    private @Autowired RestTemplate restTemplate;
    private @Autowired FutuService futuService;
    private @Autowired ConfigService configService;

    @Value("${ai-service.url}")
    private String aiServiceUrl;

    /**
     * 获取即将上市新股
     */
    @Cacheable(value = CacheConfig.IPO_UPCOMING, key = "T(java.time.LocalDate).now().toString()")
    public List<StockIpo> getUpcomingIpo() {
        LambdaQueryWrapper<StockIpo> wrapper = new LambdaQueryWrapper<>();
        wrapper.ge(StockIpo::getListingDate, LocalDate.now())
                .orderByAsc(StockIpo::getListingDate);
        return ipoMapper.selectList(wrapper);
    }

    /**
     * 获取近一年新股横向对比
     */
    @Cacheable(value = CacheConfig.IPO_COMPARISON, key = "(#sortBy ?: 'listingDate') + ':' + (#sortOrder ?: 'desc')")
    public Map<String, Object> getIpoComparison(String sortBy, String sortOrder) {
        LocalDate oneYearAgo = LocalDate.now().minusYears(1);
        LambdaQueryWrapper<StockIpo> wrapper = new LambdaQueryWrapper<>();
        wrapper.ge(StockIpo::getListingDate, oneYearAgo);

        if (sortBy != null && !sortBy.isEmpty()) {
            boolean isAsc = "asc".equalsIgnoreCase(sortOrder);
            wrapper.orderBy(true, isAsc, getSortField(sortBy));
        } else {
            wrapper.orderByDesc(StockIpo::getListingDate);
        }

        List<StockIpo> list = ipoMapper.selectList(wrapper);
        Map<String, Object> result = new HashMap<>();
        result.put("data", list);
        result.put("total", list.size());
        return result;
    }

    /**
     * 新股板块统计
     */
    @Cacheable(value = CacheConfig.IPO_SECTOR_STATS, key = "T(java.time.LocalDate).now().toString()")
    public Map<String, Object> getSectorStats() {
        LocalDate oneYearAgo = LocalDate.now().minusYears(1);
        LambdaQueryWrapper<StockIpo> wrapper = new LambdaQueryWrapper<>();
        wrapper.ge(StockIpo::getListingDate, oneYearAgo)
               .isNotNull(StockIpo::getSector);

        List<StockIpo> list = ipoMapper.selectList(wrapper);

        // 按板块分组统计；AI 与软件边界较模糊，统一合并展示为“AI/软件”
        Map<String, List<StockIpo>> bySector = new HashMap<>();
        for (StockIpo ipo : list) {
            String sector = normalizeSector(ipo.getSector());
            bySector.computeIfAbsent(sector, k -> new ArrayList<>()).add(ipo);
        }

        // 计算每个板块的统计
        List<Map<String, Object>> stats = new ArrayList<>();
        for (Map.Entry<String, List<StockIpo>> entry : bySector.entrySet()) {
            String sector = entry.getKey();
            List<StockIpo> ipos = entry.getValue();

            int total = ipos.size();
            int brokenCount = 0;
            double totalChange = 0;
            double total7dChange = 0;
            double total30dChange = 0;
            int hasChange = 0, has7d = 0, has30d = 0;

            for (StockIpo ipo : ipos) {
                if (ipo.getFirstDayChange() != null) {
                    totalChange += ipo.getFirstDayChange().doubleValue();
                    hasChange++;
                    if (ipo.getFirstDayChange().doubleValue() < 0) brokenCount++;
                }
                if (ipo.getSevenDayChange() != null) {
                    total7dChange += ipo.getSevenDayChange().doubleValue();
                    has7d++;
                }
                if (ipo.getThirtyDayChange() != null) {
                    total30dChange += ipo.getThirtyDayChange().doubleValue();
                    has30d++;
                }
            }

            if (total >= MIN_SECTOR_SAMPLE_SIZE) {
                Map<String, Object> s = new HashMap<>();
                s.put("sector", sector);
                s.put("count", total);
                s.put("avgFirstDayChange", hasChange > 0 ? Math.round(totalChange / hasChange * 100.0) / 100.0 : null);
                s.put("avgSevenDayChange", has7d > 0 ? Math.round(total7dChange / has7d * 100.0) / 100.0 : null);
                s.put("avgThirtyDayChange", has30d > 0 ? Math.round(total30dChange / has30d * 100.0) / 100.0 : null);
                s.put("breakRate", hasChange > 0 ? Math.round((double) brokenCount / hasChange * 10000.0) / 100.0 : null);
                s.put("brokenCount", brokenCount);
                stats.add(s);
            }
        }

        // 按数量降序排列
        stats.sort((a, b) -> Integer.compare((Integer) b.get("count"), (Integer) a.get("count")));

        Map<String, Object> result = new HashMap<>();
        result.put("totalSectors", stats.size());
        result.put("total", list.size());
        result.put("rawTotalSectors", bySector.size());
        result.put("hiddenSmallSectors", bySector.values().stream().filter(ipos -> ipos.size() < MIN_SECTOR_SAMPLE_SIZE).count());
        result.put("hiddenSmallSectorStocks", bySector.values().stream().filter(ipos -> ipos.size() < MIN_SECTOR_SAMPLE_SIZE).mapToInt(List::size).sum());
        result.put("minSectorSampleSize", MIN_SECTOR_SAMPLE_SIZE);
        result.put("stats", stats);
        return result;
    }

    /**
     * 破发率统计
     */
    @Cacheable(value = CacheConfig.IPO_BREAK_RATE, key = "T(java.time.LocalDate).now().toString()")
    public Map<String, Object> getBreakRate() {
        LocalDate oneYearAgo = LocalDate.now().minusYears(1);
        LambdaQueryWrapper<StockIpo> wrapper = new LambdaQueryWrapper<>();
        wrapper.ge(StockIpo::getListingDate, oneYearAgo);

        List<StockIpo> list = ipoMapper.selectList(wrapper);
        long total = list.size();
        long brokenCount = list.stream()
                .filter(ipo -> ipo.getFirstDayChange() != null && ipo.getFirstDayChange().doubleValue() < 0)
                .count();

        Map<String, Object> result = new HashMap<>();
        result.put("total", total);
        result.put("brokenCount", brokenCount);
        result.put("breakRate", total > 0 ? (double) brokenCount / total * 100 : 0);
        return result;
    }

    /**
     * AI分析新股走势
     */
    public Map<String, Object> getAiAnalysis(String stockCode) {
        validateStockCode(stockCode);
        stockCode = normalizeStockCode(stockCode);

        // 从数据库查询股票名称
        StockIpo ipo = ipoMapper.selectOne(
            new LambdaQueryWrapper<StockIpo>().eq(StockIpo::getStockCode, stockCode)
        );
        String stockName = ipo != null ? ipo.getStockName() : "";

        // 从配置服务获取 API Key / Base URL / Model。
        // 注意：业务层不要依赖 ConfigController，否则会让 Service 反向依赖接口层。
        Map<String, Object> config = configService.getCurrent();
        String apiKey = (String) config.getOrDefault("ai_api_key", "");
        String baseUrl = (String) config.getOrDefault("ai_base_url", "");
        String model = (String) config.getOrDefault("ai_model", "");

        // 调用AI服务，传入完整参数
        String url = aiServiceUrl + "/api/analyze/ipo?stock_code={code}&stock_name={name}&api_key={key}&base_url={base}&model={model}";
        try {
            Map response = restTemplate.getForObject(url, Map.class, stockCode, stockName, apiKey, baseUrl, model);
            if (response == null) {
                throw new AiServiceException("AI 服务返回为空");
            }
            return response;
        } catch (RestClientException e) {
            throw new AiServiceException("AI 服务暂时不可用，请稍后再试", e);
        }
    }

    private void validateStockCode(String stockCode) {
        if (stockCode == null || stockCode.trim().isEmpty()) {
            throw new BusinessException("股票代码不能为空");
        }
        if (!HK_STOCK_CODE_PATTERN.matcher(stockCode.trim()).matches()) {
            throw new BusinessException("股票代码格式不正确");
        }
    }

    private String normalizeStockCode(String stockCode) {
        String normalized = stockCode.trim();
        return normalized.startsWith("HK.") ? normalized.substring(3) : normalized;
    }

    /**
     * 刷新新股数据（定时任务调用）
     */
    @CacheEvict(cacheNames = {
            CacheConfig.IPO_UPCOMING,
            CacheConfig.IPO_COMPARISON,
            CacheConfig.IPO_SECTOR_STATS,
            CacheConfig.IPO_BREAK_RATE,
            CacheConfig.IPO_SECTOR_LIST
    }, allEntries = true)
    public void refreshIpoData() {
        log.info("开始刷新新股数据...");
        try {
            // 从Futu OpenAPI获取IPO列表
            List<Map<String, Object>> futuIpoList = futuService.getIpoList();
            log.info("从Futu获取到 {} 条IPO数据", futuIpoList.size());
            
            for (Map<String, Object> futuIpo : futuIpoList) {
                String stockCode = (String) futuIpo.get("code");
                String stockName = (String) futuIpo.get("name");
                
                // 检查是否已存在
                StockIpo existing = ipoMapper.selectOne(
                    new LambdaQueryWrapper<StockIpo>()
                        .eq(StockIpo::getStockCode, stockCode)
                );
                
                if (existing == null) {
                    // 新增IPO记录
                    StockIpo ipo = new StockIpo();
                    ipo.setStockCode(stockCode);
                    ipo.setStockName(stockName);
                    
                    // 解析上市日期
                    String listTime = (String) futuIpo.get("listTime");
                    if (listTime != null && !listTime.isEmpty()) {
                        try {
                            LocalDate listDate = LocalDate.parse(listTime.substring(0, 10));
                            ipo.setListingDate(listDate);
                        } catch (Exception e) {
                            log.warn("解析上市日期失败: {}", listTime);
                        }
                    }
                    
                    // 设置发行价
                    BigDecimal ipoPrice = (BigDecimal) futuIpo.get("ipoPrice");
                    if (ipoPrice != null) {
                        ipo.setIssuePrice(ipoPrice);
                    }
                    
                    ipoMapper.insert(ipo);
                    log.info("新增IPO记录: {} - {}", stockCode, stockName);
                } else {
                    // 更新已有记录（如果有新数据）
                    log.debug("IPO记录已存在: {} - {}", stockCode, stockName);
                }
            }
            
            log.info("新股数据刷新完成");
            
        } catch (Exception e) {
            throw new DataSyncException("刷新新股数据失败：" + e.getMessage(), e);
        }
    }

    private SFunction<StockIpo, ?> getSortField(String sortBy) {
        return switch (sortBy) {
            case "listingDate" -> StockIpo::getListingDate;
            case "allotmentRate" -> StockIpo::getAllotmentRate;
            case "firstDayChange" -> StockIpo::getFirstDayChange;
            case "sevenDayChange" -> StockIpo::getSevenDayChange;
            case "thirtyDayChange" -> StockIpo::getThirtyDayChange;
            default -> StockIpo::getListingDate;
        };
    }

    /**
     * 获取指定板块的所有新股
     */
    @Cacheable(value = CacheConfig.IPO_SECTOR_LIST, key = "#sector")
    public Map<String, Object> getIposBySector(String sector) {
        if (sector == null || sector.trim().isEmpty()) {
            throw new BusinessException("板块名称不能为空");
        }

        LocalDate oneYearAgo = LocalDate.now().minusYears(1);
        LambdaQueryWrapper<StockIpo> wrapper = new LambdaQueryWrapper<>();
        wrapper.ge(StockIpo::getListingDate, oneYearAgo)
               .isNotNull(StockIpo::getSector)
               .orderByDesc(StockIpo::getListingDate);

        List<StockIpo> list = ipoMapper.selectList(wrapper);
        List<StockIpo> matched = new ArrayList<>();
        for (StockIpo ipo : list) {
            if (normalizeSector(ipo.getSector()).equals(sector)) {
                matched.add(ipo);
            }
        }

        Map<String, Object> result = new HashMap<>();
        result.put("sector", sector);
        result.put("total", matched.size());
        result.put("ipos", matched);
        return result;
    }

    /**
     * 标准化板块名称。AI 与软件边界较模糊，统计时统一合并为“AI/软件”。
     */
    private String normalizeSector(String rawSector) {
        if (rawSector == null || rawSector.trim().isEmpty()) {
            return "未知";
        }

        String normalized = rawSector.trim();
        if ("AI".equalsIgnoreCase(normalized)
                || "软件".equals(normalized)
                || "AI/软件".equalsIgnoreCase(normalized)
                || "AI／软件".equalsIgnoreCase(normalized)) {
            return "AI/软件";
        }

        return normalized;
    }
}
