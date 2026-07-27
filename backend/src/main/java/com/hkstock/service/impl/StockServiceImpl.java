package com.hkstock.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.hkstock.config.CacheConfig;
import com.hkstock.domain.StockInfo;
import com.hkstock.domain.StockKline;
import com.hkstock.domain.StockValuation;
import com.hkstock.exception.BusinessException;
import com.hkstock.mapper.StockInfoMapper;
import com.hkstock.mapper.StockKlineMapper;
import com.hkstock.mapper.StockValuationMapper;
import com.hkstock.service.FutuService;
import com.hkstock.service.StockService;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;
import jakarta.annotation.Resource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

/** 股票服务实现 */
@Service
public class StockServiceImpl implements StockService {

    private static final Logger log = LoggerFactory.getLogger(StockServiceImpl.class);
    private static final Pattern HK_STOCK_CODE_PATTERN = Pattern.compile("^(HK\\.)?\\d{5}$");

    @Resource
    private StockInfoMapper stockInfoMapper;
    @Resource
    private StockKlineMapper stockKlineMapper;
    @Resource
    private StockValuationMapper valuationMapper;
    @Resource
    private FutuService futuService;

    @Override
    @Cacheable(value = CacheConfig.STOCK_SEARCH, key = "#keyword")
    public List<StockInfo> searchStocks(String keyword) {
        // 搜索股票并关联市值数据
        List<StockInfo> stocks = stockInfoMapper.selectList(
            new LambdaQueryWrapper<StockInfo>()
                .like(StockInfo::getStockCode, keyword)
                .or()
                .like(StockInfo::getStockName, keyword)
                .or()
                .like(StockInfo::getSector, keyword)
        );
        // 填充市值数据
        if (!stocks.isEmpty()) {
            List<String> codes = stocks.stream().map(StockInfo::getStockCode).toList();
            Map<String, BigDecimal> marketCapMap = new HashMap<>();
            for (String code : codes) {
                StockValuation valuation = valuationMapper.selectOne(
                    new LambdaQueryWrapper<StockValuation>()
                        .eq(StockValuation::getStockCode, code)
                        .orderByDesc(StockValuation::getDataDate)
                        .last("LIMIT 1")
                );
                if (valuation != null && valuation.getMarketCap() != null) {
                    marketCapMap.put(code, valuation.getMarketCap());
                }
            }
            for (StockInfo stock : stocks) {
                stock.setMarketCap(marketCapMap.get(stock.getStockCode()));
            }
        }
        return stocks;
    }

    @Override
    @Cacheable(value = CacheConfig.STOCK_KLINE, key = "#stockCode + ':' + #periodType + ':' + #days")
    public List<StockKline> getKlineData(String stockCode, String periodType, Integer days) {
        stockCode = normalizeAndValidateStockCode(stockCode);
        if ("5D".equals(periodType)) {
            return aggregateKline(stockCode, 5, days);
        }
        if ("10D".equals(periodType)) {
            return aggregateKline(stockCode, 10, days);
        }

        LambdaQueryWrapper<StockKline> wrapper = new LambdaQueryWrapper<>();
        wrapper
            .eq(StockKline::getStockCode, stockCode)
            .eq(StockKline::getPeriodType, periodType)
            .orderByDesc(StockKline::getTradeDate)
            .last("LIMIT " + days);
        List<StockKline> list = stockKlineMapper.selectList(wrapper);
        list.sort((a, b) -> a.getTradeDate().compareTo(b.getTradeDate()));
        return list;
    }

    private List<StockKline> aggregateKline(String stockCode, int groupSize, int resultCount) {
        int dailyLimit = resultCount * groupSize;

        LambdaQueryWrapper<StockKline> wrapper = new LambdaQueryWrapper<>();
        wrapper
            .eq(StockKline::getStockCode, stockCode)
            .eq(StockKline::getPeriodType, "D")
            .orderByDesc(StockKline::getTradeDate)
            .last("LIMIT " + dailyLimit);
        List<StockKline> dailyList = stockKlineMapper.selectList(wrapper);

        if (dailyList.isEmpty()) {
            return dailyList;
        }

        dailyList.sort((a, b) -> a.getTradeDate().compareTo(b.getTradeDate()));

        List<StockKline> result = new ArrayList<>();
        for (int i = 0; i + groupSize <= dailyList.size(); i += groupSize) {
            StockKline first = dailyList.get(i);
            StockKline last = dailyList.get(i + groupSize - 1);

            StockKline merged = new StockKline();
            merged.setStockCode(stockCode);
            merged.setPeriodType(groupSize + "D");
            merged.setTradeDate(last.getTradeDate());
            merged.setOpenPrice(first.getOpenPrice());
            merged.setClosePrice(last.getClosePrice());

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

            if (i >= groupSize) {
                StockKline prevGroupLast = dailyList.get(i - 1);
                if (prevGroupLast.getClosePrice() != null
                    && prevGroupLast.getClosePrice().compareTo(BigDecimal.ZERO) != 0) {
                    BigDecimal change =
                        last.getClosePrice()
                            .subtract(prevGroupLast.getClosePrice())
                            .divide(prevGroupLast.getClosePrice(), 6, java.math.RoundingMode.HALF_UP)
                            .multiply(new BigDecimal("100"));
                    merged.setChangePercent(change.setScale(2, java.math.RoundingMode.HALF_UP));
                }
            } else {
                merged.setChangePercent(BigDecimal.ZERO);
            }

            result.add(merged);
        }

        if (result.size() > resultCount) {
            result = result.subList(result.size() - resultCount, result.size());
        }

        return result;
    }

    @Override
    @Cacheable(value = CacheConfig.STOCK_DAILY_INFO, key = "#stockCode")
    public StockKline getLatestDailyInfo(String stockCode) {
        stockCode = normalizeAndValidateStockCode(stockCode);
        LambdaQueryWrapper<StockKline> wrapper = new LambdaQueryWrapper<>();
        wrapper
            .eq(StockKline::getStockCode, stockCode)
            .eq(StockKline::getPeriodType, "D")
            .orderByDesc(StockKline::getTradeDate)
            .last("LIMIT 1");
        return stockKlineMapper.selectOne(wrapper);
    }

    @Override
    @Cacheable(value = CacheConfig.STOCK_VALUATION, key = "#stockCode")
    public StockValuation getValuation(String stockCode) {
        stockCode = normalizeAndValidateStockCode(stockCode);
        LambdaQueryWrapper<StockValuation> wrapper = new LambdaQueryWrapper<>();
        wrapper
            .eq(StockValuation::getStockCode, stockCode)
            .orderByDesc(StockValuation::getDataDate)
            .last("LIMIT 1");
        return valuationMapper.selectOne(wrapper);
    }

    @Override
    @Cacheable(value = CacheConfig.STOCK_COMPARISON, key = "#stockCodes.toString() + ':' + #metrics")
    public Map<String, Object> compareStocks(List<String> stockCodes, String metrics) {
        Map<String, Object> result = new HashMap<>();
        for (String code : stockCodes) {
            Map<String, Object> stockData = new HashMap<>();
            StockKline latest = getLatestDailyInfo(code);
            StockValuation valuation = getValuation(code);
            StockInfo info =
                stockInfoMapper.selectOne(
                    new LambdaQueryWrapper<StockInfo>().eq(StockInfo::getStockCode, code));
            stockData.put("info", info);
            stockData.put("latest", latest);
            stockData.put("valuation", valuation);
            result.put(code, stockData);
        }
        return result;
    }

    @Override
    @CacheEvict(
        cacheNames = {
            CacheConfig.STOCK_KLINE,
            CacheConfig.STOCK_DAILY_INFO,
            CacheConfig.STOCK_VALUATION,
            CacheConfig.STOCK_COMPARISON
        },
        allEntries = true)
    public void refreshKlineData(String stockCode, String periodType, int days) {
        stockCode = normalizeAndValidateStockCode(stockCode);
        log.info("开始刷新K线数据: {} - {} - {}天", stockCode, periodType, days);
        try {
            List<Map<String, Object>> futuKlineList =
                futuService.getKlineData(stockCode, periodType, days);
            log.info("从Futu获取到 {} 条K线数据", futuKlineList.size());

            for (Map<String, Object> futuKline : futuKlineList) {
                String dateStr = (String) futuKline.get("date");
                LocalDate tradeDate = LocalDate.parse(dateStr.substring(0, 10));

                StockKline existing =
                    stockKlineMapper.selectOne(
                        new LambdaQueryWrapper<StockKline>()
                            .eq(StockKline::getStockCode, stockCode)
                            .eq(StockKline::getPeriodType, periodType)
                            .eq(StockKline::getTradeDate, tradeDate));

                if (existing == null) {
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

    @Override
    @CacheEvict(
        cacheNames = {CacheConfig.STOCK_SEARCH, CacheConfig.STOCK_COMPARISON},
        allEntries = true)
    public void refreshStockList() {
        log.info("开始刷新股票列表...");
        try {
            List<Map<String, Object>> futuStockList = futuService.getStockList();
            log.info("从Futu获取到 {} 条股票数据", futuStockList.size());

            for (Map<String, Object> futuStock : futuStockList) {
                String stockCode = (String) futuStock.get("code");
                String stockName = (String) futuStock.get("name");

                StockInfo existing =
                    stockInfoMapper.selectOne(
                        new LambdaQueryWrapper<StockInfo>().eq(StockInfo::getStockCode, stockCode));

                if (existing == null) {
                    StockInfo stockInfo = new StockInfo();
                    stockInfo.setStockCode(stockCode);
                    stockInfo.setStockName(stockName);
                    stockInfoMapper.insert(stockInfo);
                } else {
                    if (!stockName.equals(existing.getStockName())) {
                        existing.setStockName(stockName);
                        stockInfoMapper.updateById(existing);
                    }
                }
            }

            log.info("股票列表刷新完成");
        } catch (Exception e) {
            log.error("刷新股票列表失败: {}", e.getMessage(), e);
        }
    }

    private String normalizeAndValidateStockCode(String stockCode) {
        if (stockCode == null || stockCode.trim().isEmpty()) {
            throw new BusinessException("股票代码不能为空");
        }
        String normalized = stockCode.trim();
        if (!HK_STOCK_CODE_PATTERN.matcher(normalized).matches()) {
            throw new BusinessException("股票代码格式不正确");
        }
        return normalized.startsWith("HK.") ? normalized.substring(3) : normalized;
    }
}
