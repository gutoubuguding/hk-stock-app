package com.hkstock.service;

import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;

import com.hkstock.exception.AiServiceException;
import com.hkstock.exception.BusinessException;
import com.hkstock.mapper.StockIpoMapper;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

@ExtendWith(MockitoExtension.class)
class AiAnalysisServiceTest {

  @Mock private StockIpoMapper ipoMapper;

  @Mock private RestTemplate restTemplate;

  @Mock private ConfigService configService;

  private IpoService ipoService;

  @BeforeEach
  void setUp() {
    ipoService = new IpoService();
    ReflectionTestUtils.setField(ipoService, "ipoMapper", ipoMapper);
    ReflectionTestUtils.setField(ipoService, "restTemplate", restTemplate);
    ReflectionTestUtils.setField(ipoService, "configService", configService);
    ReflectionTestUtils.setField(ipoService, "aiServiceUrl", "http://ai-service:8082");
  }

  @Test
  void getAiAnalysisReturnsFriendlyErrorWhenAiServiceTimeouts() {
    when(ipoMapper.selectOne(any())).thenReturn(null);
    when(configService.getRequiredAiConfig())
        .thenReturn(
            Map.of(
                "ai_api_key", "test-key",
                "ai_base_url", "http://llm.example",
                "ai_model", "test-model"));
    when(restTemplate.getForObject(
            any(String.class), eq(Map.class), any(), any(), any(), any(), any()))
        .thenThrow(new ResourceAccessException("Read timed out"));

    assertThatThrownBy(() -> ipoService.getAiAnalysis("00700"))
        .isInstanceOf(AiServiceException.class)
        .hasMessageContaining("AI 服务暂时不可用，请稍后再试");
  }

  @Test
  void getAiAnalysisRejectsIllegalStockCode() {
    assertThatThrownBy(() -> ipoService.getAiAnalysis("bad-code"))
        .isInstanceOf(BusinessException.class)
        .hasMessageContaining("股票代码格式不正确");
  }
}
