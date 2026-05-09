package com.hkstock.service;

import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doThrow;

import com.hkstock.exception.AiServiceException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowCallbackHandler;

@ExtendWith(MockitoExtension.class)
class ConfigServiceTest {

  @Mock private JdbcTemplate jdbcTemplate;

  @Test
  void getRequiredAiConfigReturnsFriendlyErrorWhenApiKeyIsEmpty() {
    doThrow(new RuntimeException("stock_config not ready"))
        .when(jdbcTemplate)
        .query(
            eq("SELECT config_key, config_value FROM stock_config"), any(RowCallbackHandler.class));
    ConfigService configService = new ConfigService(jdbcTemplate);
    configService.afterPropertiesSet();

    assertThatThrownBy(configService::getRequiredAiConfig)
        .isInstanceOf(AiServiceException.class)
        .hasMessageContaining("请先在设置页填写 AI API Key");
  }
}
