package com.hkstock.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.hkstock.config.CacheConfig;
import com.hkstock.entity.StockInfo;
import com.hkstock.entity.StockKline;
import com.hkstock.entity.StockValuation;
import com.hkstock.mapper.StockInfoMapper;
import com.hkstock.mapper.StockKlineMapper;
import com.hkstock.mapper.StockValuationMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 股票服务
 */
@Service
public class StockService {

    private static final Logger log = LoggerFactory.getLogger(StockService.class);

    private @Autowired StockInfoMapper stockInfoMapper;
    private @Autowired StockKlineMapper stockKlineMapper;
    private @Autowired StockValuationMapper valuationMapper;
    private @Autowired FutuService futuService;

    /**
     * 搜索股票
     */
    @Cacheable(value = CacheConfig.STOCK_SEARCH, key = "#keyword")
    public List<StockInfo> searchStocks(String keyword) {
        LambdaQueryWrapper<StockInfo> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(StockInfo::getStockCode, keyword)
                .or()
                .like(StockInfo::getStockName, keyword)
                .or()
                .like(StockInfo::getSector, keyword);
        return stockInfoMapper.selectList(wrapper);
    }

    /**
     * 获取K线数据
     */
    @Cacheable(value = CacheConfig.STOCK_KLINE, key = "#stockCode + ':' + #periodType + ':' + #days")
    public List<StockKline> getKlineData(String stockCode, String periodType, Integer days) {
        // 5日K线：从日K数据动态聚合
        if ("5D".equals(periodType)) {
            return aggregateKline(stockCode, 5, days);
        }
        // 10日K线（备用）
        if ("10D".equals(periodType)) {
            return aggregateKline(stockCode, 10, days);
        }

        LambdaQueryWrapper<StockKline> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(StockKline::getStockCode, stockCode)
                .eq(StockKline::getPeriodType, periodType)
                .orderByDesc(StockKline::getTradeDate)
                .last("LIMIT " + days);
        List<StockKline> list = stockKlineMapper.selectList(wrapper);
        list.sort((a, b) -> a.getTradeDate().compareTo(b.getTradeDate())); // 按日期正序
        return list;
    }

    /**
     * 从日K数据聚合为N日K线
     * @param stockCode 股票代码
     * @param groupSize 每N个交易日合并为一根K线
     * @param resultCount 需要返回的K线数量
     */
    private List<StockKline> aggregateKline(String stockCode, int groupSize, int resultCount) {
        // 需要的日K数据量 = resultCount * groupSize
        int dailyLimit = resultCount * groupSize;

        LambdaQueryWrapper<StockKline> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(StockKline::getStockCode, stockCode)
                .eq(StockKline::getPeriodType, "D")
                .orderByDesc(StockKline::getTradeDate)
                .last("LIMIT " + dailyLimit);
        List<StockKline> dailyList = stockKlineMapper.selectList(wrapper);

        if (dailyList.isEmpty()) {
            return dailyList;
        }

        // 按日期正序排列
        dailyList.sort((a, b) -> a.getTradeDate().compareTo(b.getTradeDate()));

        // 每groupSize根日K合并为一根
        List<StockKline> result = new java.util.ArrayList<>();
        for (int i = 0; i + groupSize <= dailyList.size(); i += groupSize) {
            StockKline first = dailyList.get(i);
            StockKline last = dailyList.get(i + groupSize - 1);

            StockKline merged = new StockKline();
            merged.setStockCode(stockCode);
            merged.setPeriodType(groupSize + "D");
            merged.setTradeDate(last.getTradeDate()); // 用最后一根的日期
            merged.setOpenPrice(first.getOpenPrice()); // 第一根的开盘
            merged.setClosePrice(last.getClosePrice()); // 最后一根的收盘

            // 最高价和最低价取区间极值
            BigDecimal high = first.getHighPrice();
            BigDecimal low = first.getLowPrice();
            long totalVolume = 0;
            BigDecimal totalTurnover = BigDecimal.ZERO;

            for (int j = i; j < i + groupSize; j++) {
                StockKline d = dailyList.get(j);
                if (d.getHighPrice() != null && d.getHighPrice().compareTo(high) > 0) {
                    high = d.getHighPrice();
                }
                if (d.getLowPrice() != null && d.getLowPrice().compareTo(low) < 0) {
                    low = d.getLowPrice();
                }
                totalVolume += (d.getVolume() != null ? d.getVolume() : 0);
                if (d.getTurnover() != null) {
                    totalTurnover = totalTurnover.add(d.getTurnover());
                }
            }

            merged.setHighPrice(high);
            merged.setLowPrice(low);
            merged.setVolume(totalVolume);
            merged.setTurnover(totalTurnover);

            // 涨跌幅 = (收盘 - 前一根收盘) / 前一根收盘 * 100
            if (i >= groupSize) {
                StockKline prevGroupLast = dailyList.get(i - 1);
                if (prevGroupLast.getClosePrice() != null && prevGroupLast.getClosePrice().compareTo(BigDecimal.ZERO) != 0) {
                    BigDecimal change = last.getClosePrice().subtract(prevGroupLast.getClosePrice())
                            .divide(prevGroupLast.getClosePrice(), 6, java.math.RoundingMode.HALF_UP)
                            .multiply(new BigDecimal("100"));
                    merged.setChangePercent(change.setScale(2, java.math.RoundingMode.HALF_UP));
                }
            } else {
                merged.setChangePercent(BigDecimal.ZERO);
            }

            result.add(merged);
        }

        // 只返回最后 resultCount 根
        if (result.size() > resultCount) {
            result = result.subList(result.size() - resultCount, result.size());
        }

        return result;
    }

    /**
     * 获取最新日K数据（当日关键信息）
     */
    @Cacheable(value = CacheConfig.STOCK_DAILY_INFO, key = "#stockCode")
    public StockKline getLatestDailyInfo(String stockCode) {
        LambdaQueryWrapper<StockKline> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(StockKline::getStockCode, stockCode)
                .eq(StockKline::getPeriodType, "D")
                .orderByDesc(StockKline::getTradeDate)
                .last("LIMIT 1");
        return stockKlineMapper.selectOne(wrapper);
    }

    /**
     * 获取估值指标
     */
    @Cacheable(value = CacheConfig.STOCK_VALUATION, key = "#stockCode")
    public StockValuation getValuation(String stockCode) {
        LambdaQueryWrapper<StockValuation> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(StockValuation::getStockCode, stockCode)
                .orderByDesc(StockValuation::getDataDate)
                .last("LIMIT 1");
        return valuationMapper.selectOne(wrapper);
    }

    /**
     * 对比多只股票
     */
    @Cacheable(value = CacheConfig.STOCK_COMPARISON, key = "#stockCodes.toString() + ':' + #metrics")
    public Map<String, Object> compareStocks(List<String> stockCodes, String metrics) {
        Map<String, Object> result = new HashMap<>();
        for (String code : stockCodes) {
            Map<String, Object> stockData = new HashMap<>();
            StockKline latest = getLatestDailyInfo(code);
            StockValuation valuation = getValuation(code);
            StockInfo info = stockInfoMapper.selectOne(
                    new LambdaQueryWrapper<StockInfo>().eq(StockInfo::getStockCode, code)
            );
            stockData.put("info", info);
            stockData.put("latest", latest);
            stockData.put("valuation", valuation);
            result.put(code, stockData);
        }
        return result;
    }

    /**
     * 从Futu OpenAPI刷新K线数据
     */
    @CacheEvict(cacheNames = {
            CacheConfig.STOCK_KLINE,
            CacheConfig.STOCK_DAILY_INFO,
            CacheConfig.STOCK_VALUATION,
            CacheConfig.STOCK_COMPARISON
    }, allEntries = true)
    public void refreshKlineData(String stockCode, String periodType, int days) {
        log.info("开始刷新K线数据: {} - {} - {}天", stockCode, periodType, days);
        try {
            // 从Futu OpenAPI获取K线数据
            List<Map<String, Object>> futuKlineList = futuService.getKlineData(stockCode, periodType, days);
            log.info("从Futu获取到 {} 条K线数据", futuKlineList.size());
            
            for (Map<String, Object> futuKline : futuKlineList) {
                String dateStr = (String) futuKline.get("date");
                LocalDate tradeDate = LocalDate.parse(dateStr.substring(0, 10));
                
                // 检查是否已存在
                StockKline existing = stockKlineMapper.selectOne(
                    new LambdaQueryWrapper<StockKline>()
                        .eq(StockKline::getStockCode, stockCode)
                        .eq(StockKline::getPeriodType, periodType)
                        .eq(StockKline::getTradeDate, tradeDate)
                );
                
                if (existing == null) {
                    // 新增K线记录
                    StockKline kline = new StockKline();
                    kline.setStockCode(stockCode);
                    kline.setPeriodType(periodType);
                    kline.setTradeDate(tradeDate);
                    kline.setOpenPrice((BigDecimal) futuKline.get("open"));
                    kline.setClosePrice((BigDecimal) futuKline.get("close"));
                    kline.setHighPrice((BigDecimal) futuKline.get("high"));
                    kline.setLowPrice((BigDecimal) futuKline.get("low"));
                    kline.setVolume((Long) futuKline.get("volume"));
                    kline.setTurnover((BigDecimal) futuKline.get("turnover"));
                    kline.setChangePercent((BigDecimal) futuKline.get("changePercent"));
                    kline.setTurnoverRate((BigDecimal) futuKline.get("turnoverRate"));
                    
                    stockKlineMapper.insert(kline);
                } else {
                    // 更新已有记录
                    existing.setOpenPrice((BigDecimal) futuKline.get("open"));
                    existing.setClosePrice((BigDecimal) futuKline.get("close"));
                    existing.setHighPrice((BigDecimal) futuKline.get("high"));
                    existing.setLowPrice((BigDecimal) futuKline.get("low"));
                    existing.setVolume((Long) futuKline.get("volume"));
                    existing.setTurnover((BigDecimal) futuKline.get("turnover"));
                    existing.setChangePercent((BigDecimal) futuKline.get("changePercent"));
                    existing.setTurnoverRate((BigDecimal) futuKline.get("turnoverRate"));
                    
                    stockKlineMapper.updateById(existing);
                }
            }
            
            log.info("K线数据刷新完成: {} - {}", stockCode, periodType);
            
        } catch (Exception e) {
            log.error("刷新K线数据失败: {} - {} - {}", stockCode, periodType, e.getMessage(), e);
        }
    }

    /**
     * 刷新股票列表
     */
    @CacheEvict(cacheNames = {
            CacheConfig.STOCK_SEARCH,
            CacheConfig.STOCK_COMPARISON
    }, allEntries = true)
    public void refreshStockList() {
        log.info("开始刷新股票列表...");
        try {
            // 从Futu OpenAPI获取股票列表
            List<Map<String, Object>> futuStockList = futuService.getStockList();
            log.info("从Futu获取到 {} 条股票数据", futuStockList.size());
            
            for (Map<String, Object> futuStock : futuStockList) {
                String stockCode = (String) futuStock.get("code");
                String stockName = (String) futuStock.get("name");
                
                // 检查是否已存在
                StockInfo existing = stockInfoMapper.selectOne(
                    new LambdaQueryWrapper<StockInfo>()
                        .eq(StockInfo::getStockCode, stockCode)
                );
                
                if (existing == null) {
                    // 新增股票记录
                    StockInfo stockInfo = new StockInfo();
                    stockInfo.setStockCode(stockCode);
                    stockInfo.setStockName(stockName);
                    
                    stockInfoMapper.insert(stockInfo);
                    log.debug("新增股票记录: {} - {}", stockCode, stockName);
                } else {
                    // 更新股票名称（如果有变化）
                    if (!stockName.equals(existing.getStockName())) {
                        existing.setStockName(stockName);
                        stockInfoMapper.updateById(existing);
                        log.debug("更新股票名称: {} - {}", stockCode, stockName);
                    }
                }
            }
            
            log.info("股票列表刷新完成");
            
        } catch (Exception e) {
            log.error("刷新股票列表失败: {}", e.getMessage(), e);
        }
    }
}
