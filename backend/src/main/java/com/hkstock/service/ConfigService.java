package com.hkstock.service;

import com.hkstock.exception.AiServiceException;
import java.util.HashMap;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

/**
 * 系统配置服务。
 *
 * <p>这个类专门负责读写 stock_config 表，并在内存中保留一份配置缓存。 之前配置读写逻辑放在 ConfigController 里，业务服务如果想读取 AI 配置就要依赖
 * Controller， 会让“接口层”和“业务层”耦合在一起。现在抽出来后：
 *
 * <ul>
 *   <li>Controller 只负责接收/返回 HTTP 请求；
 *   <li>Service 统一负责配置的读取、默认值和持久化；
 *   <li>IpoService 等业务代码可以直接依赖 ConfigService，更清楚也更容易测试。
 * </ul>
 */
@Service
public class ConfigService implements InitializingBean {

  private static final Logger log = LoggerFactory.getLogger(ConfigService.class);

  /** 默认 AI 配置，数据库没有值或读取失败时使用。 */
  private static final Map<String, Object> DEFAULT_CONFIG =
      Map.of(
          "ai_provider", "openai",
          "ai_model", "gpt-4",
          "ai_api_key", "",
          "ai_base_url", "https://api.openai.com/v1");

  private final JdbcTemplate jdbc;

  /** 简单内存缓存，避免每次请求都查数据库。 当前项目是单机运行，HashMap 足够；如果以后多实例部署，再换成数据库直读或分布式缓存。 */
  private final Map<String, Object> configStore = new HashMap<>();

  public ConfigService(JdbcTemplate jdbc) {
    this.jdbc = jdbc;
  }

  /** Spring Bean 初始化后加载数据库配置。 如果数据库还没建表或读取失败，也会填入默认值，保证设置页和 AI 分析接口可用。 */
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

  /** 返回当前配置副本，避免外部代码直接修改内部缓存。 */
  public Map<String, Object> getCurrent() {
    return new HashMap<>(configStore);
  }

  /** 获取可用于 AI 调用的配置；缺少关键配置时给出面向用户的友好错误。 */
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

  /** 更新并持久化 AI 模型配置。 body 来自设置页表单；api_key 允许为空字符串，因为用户可能想清空旧 Key。 */
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

  /** PostgreSQL upsert：有则更新，没有则插入。 单个配置保存失败不影响应用继续运行，但会写日志方便排查。 */
  private void saveToDb(String key, String value) {
    try {
      jdbc.update(
          "INSERT INTO stock_config (config_key, config_value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) "
              + "ON CONFLICT (config_key) DO UPDATE SET config_value = ?, updated_at = CURRENT_TIMESTAMP",
          key,
          value,
          value);
    } catch (Exception e) {
      log.error("保存配置失败 key={}: {}", key, e.getMessage());
    }
  }
}
