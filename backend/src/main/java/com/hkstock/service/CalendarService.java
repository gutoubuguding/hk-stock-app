package com.hkstock.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.hkstock.entity.StockCalendar;
import com.hkstock.mapper.StockCalendarMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import javax.sql.DataSource;
import java.math.BigDecimal;
import java.sql.*;
import java.time.LocalDate;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 财报/分红日历服务
 */
@Service
public class CalendarService {
    private static final Logger log = LoggerFactory.getLogger(CalendarService.class);

    private @Autowired StockCalendarMapper calendarMapper;
    private @Autowired DataSource dataSource;

    public List<StockCalendar> getUpcomingFinancialReports(Integer days) {
        LocalDate now = LocalDate.now();
        LocalDate end = now.plusDays(days);
        LambdaQueryWrapper<StockCalendar> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(StockCalendar::getEventType, "FINANCIAL")
                .between(StockCalendar::getEventDate, now, end)
                .orderByAsc(StockCalendar::getEventDate);
        return calendarMapper.selectList(wrapper);
    }

    public List<StockCalendar> getUpcomingDividends(Integer days) {
        LocalDate now = LocalDate.now();
        LocalDate end = now.plusDays(days);
        LambdaQueryWrapper<StockCalendar> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(StockCalendar::getEventType, "DIVIDEND")
                .between(StockCalendar::getEventDate, now, end)
                .orderByAsc(StockCalendar::getEventDate);
        return calendarMapper.selectList(wrapper);
    }

    /**
     * 获取大盘概览 - 从 market_overview 表读取恒生/恒科/国企指数数据。
     */
    public Map<String, Object> getMarketOverview() {
        Map<String, Object> result = new HashMap<>();
        // 复用 Spring Boot datasource 配置，避免在代码里写死数据库地址/账号/密码。
        try (Connection conn = dataSource.getConnection()) {
            result.put("hsi", getLatestIndex(conn, "HSI", "HK.800000"));
            result.put("hstech", getLatestIndex(conn, "HSTECH", "HK.800010"));
            result.put("hscei", getLatestIndex(conn, "HSCEI"));

            Map<String, Object> hsi = (Map<String, Object>) result.get("hsi");
            result.put("advance", hsi.getOrDefault("advance", 0));
            result.put("decline", hsi.getOrDefault("decline", 0));
            result.put("flat", hsi.getOrDefault("flat", 0));
            result.put("sentiment", hsi.getOrDefault("sentiment", 50.0));
        } catch (SQLException e) {
            log.error("Failed to get market overview", e);
            result.put("hsi", emptyIndex());
            result.put("hstech", emptyIndex());
            result.put("hscei", emptyIndex());
            result.put("advance", 0);
            result.put("decline", 0);
            result.put("flat", 0);
            result.put("sentiment", 50.0);
        }
        return result;
    }

    private Map<String, Object> getLatestIndex(Connection conn, String... codes) throws SQLException {
        String placeholders = String.join(",", java.util.Collections.nCopies(codes.length, "?"));
        String sql = "SELECT index_code, index_name, last_price, change_val, change_pct, " +
                "open_price, high_price, low_price, prev_close, volume, turnover, " +
                "raise_count, fall_count, equal_count, update_time " +
                "FROM market_overview WHERE index_code IN (" + placeholders + ") " +
                "ORDER BY update_time DESC LIMIT 1";
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            for (int i = 0; i < codes.length; i++) {
                stmt.setString(i + 1, codes[i]);
            }
            ResultSet rs = stmt.executeQuery();
            if (!rs.next()) {
                return emptyIndex();
            }
            Map<String, Object> index = new HashMap<>();
            index.put("code", rs.getString("index_code"));
            index.put("name", rs.getString("index_name"));
            index.put("value", rs.getDouble("last_price"));
            index.put("change", rs.getDouble("change_val"));
            index.put("changePercent", rs.getDouble("change_pct"));
            index.put("open", rs.getDouble("open_price"));
            index.put("high", rs.getDouble("high_price"));
            index.put("low", rs.getDouble("low_price"));
            index.put("prevClose", rs.getDouble("prev_close"));
            index.put("volume", rs.getLong("volume"));
            index.put("turnover", rs.getDouble("turnover"));
            index.put("updateTime", rs.getTimestamp("update_time") != null ? rs.getTimestamp("update_time").toString() : null);

            int raise = rs.getInt("raise_count");
            int fall = rs.getInt("fall_count");
            int equal = rs.getInt("equal_count");
            int total = raise + fall + equal;
            index.put("advance", raise);
            index.put("decline", fall);
            index.put("flat", equal);
            index.put("sentiment", total > 0 ? (raise * 100.0 / total) : 50.0);
            return index;
        }
    }

    private Map<String, Object> emptyIndex() {
        return Map.of(
                "value", 0,
                "change", 0,
                "changePercent", 0,
                "advance", 0,
                "decline", 0,
                "flat", 0,
                "sentiment", 50.0
        );
    }
}
