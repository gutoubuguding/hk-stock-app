package com.hkstock.service.impl;

import com.hkstock.exception.AiServiceException;
import com.hkstock.service.ConfigService;
import java.util.HashMap;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

/** 系统配置服务实现 */
@Service
public class ConfigServiceImpl implements ConfigService, InitializingBean {

    private static final Logger log = LoggerFactory.getLogger(ConfigServiceImpl.class);

    private static final Map<String, Object> DEFAULT_CONFIG =
        Map.of(
            "ai_provider", "openai",
            "ai_model", "gpt-4",
            "ai_api_key", "",
            "ai_base_url", "https://api.openai.com/v1");

    private final JdbcTemplate jdbc;
    private final Map<String, Object> configStore = new HashMap<>();

    public ConfigServiceImpl(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @Override
    public void afterPropertiesSet() {
        configStore.clear();
        try {
            jdbc.query(
                "SELECT config_key, config_value FROM stock_config",
                rs -> {
                    configStore.put(rs.getString("config_key"), rs.getString("config_value"));
                });
            applyDefaultConfig();
            log.info("已从数据库加载配置项: {}", configStore.keySet());
        } catch (Exception e) {
            configStore.putAll(DEFAULT_CONFIG);
            log.warn("读取 stock_config 失败，已使用默认配置: {}", e.getMessage());
        }
    }

    @Override
    public Map<String, Object> getCurrent() {
        return new HashMap<>(configStore);
    }

    @Override
    public Map<String, Object> getRequiredAiConfig() {
        Map<String, Object> current = getCurrent();
        String apiKey = String.valueOf(current.getOrDefault("ai_api_key", ""));
        String baseUrl = String.valueOf(current.getOrDefault("ai_base_url", ""));
        String model = String.valueOf(current.getOrDefault("ai_model", ""));
        if (apiKey.isBlank()) {
            throw new AiServiceException("请先在设置页填写 AI API Key");
        }
        if (baseUrl.isBlank()) {
            throw new AiServiceException("请先在设置页填写 AI API 地址");
        }
        if (model.isBlank()) {
            throw new AiServiceException("请先在设置页选择 AI 模型");
        }
        return current;
    }

    @Override
    public void updateModelConfig(Map<String, String> body) {
        saveIfPresent("ai_provider", body.get("provider"), body.containsKey("provider"));
        saveIfPresent("ai_model", body.get("model"), body.containsKey("model"));
        saveIfPresent("ai_api_key", body.get("api_key"), body.containsKey("api_key"));
        saveIfPresent("ai_base_url", body.get("base_url"), body.containsKey("base_url"));
    }

    private void applyDefaultConfig() {
        DEFAULT_CONFIG.forEach(configStore::putIfAbsent);
    }

    private void saveIfPresent(String key, String value, boolean present) {
        if (!present) {
            return;
        }
        configStore.put(key, value == null ? "" : value);
        saveToDb(key, value == null ? "" : value);
    }

    private void saveToDb(String key, String value) {
        try {
            jdbc.update(
                "INSERT INTO stock_config (config_key, config_value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) "
                    + "ON CONFLICT (config_key) DO UPDATE SET config_value = ?, updated_at = CURRENT_TIMESTAMP",
                key, value, value);
        } catch (Exception e) {
            log.error("保存配置失败 key={}: {}", key, e.getMessage());
        }
    }
}
