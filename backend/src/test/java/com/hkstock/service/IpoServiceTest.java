package com.hkstock.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.hkstock.entity.StockIpo;
import com.hkstock.mapper.StockIpoMapper;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

@ExtendWith(MockitoExtension.class)
class IpoServiceTest {

  @Mock private StockIpoMapper ipoMapper;

  private IpoService ipoService;

  @BeforeEach
  void setUp() {
    ipoService = new IpoService();
    ReflectionTestUtils.setField(ipoService, "ipoMapper", ipoMapper);
  }

  @Test
  void getUpcomingIpoReturnsEmptyListWhenNoData() {
    when(ipoMapper.selectList(any())).thenReturn(Collections.emptyList());

    List<StockIpo> result = ipoService.getUpcomingIpo();

    assertThat(result).isEmpty();
  }

  @Test
  void getIpoComparisonReturnsEmptyResultWhenNoData() {
    when(ipoMapper.selectList(any())).thenReturn(Collections.emptyList());

    Map<String, Object> result = ipoService.getIpoComparison(null, "desc");

    assertThat(result).containsEntry("total", 0);
    assertThat((List<?>) result.get("data")).isEmpty();
  }

  @Test
  void getIpoComparisonAcceptsInvalidSortByAndUsesSafeDefault() {
    when(ipoMapper.selectList(any())).thenReturn(Collections.emptyList());

    Map<String, Object> result = ipoService.getIpoComparison("notExists", "asc");

    assertThat(result).containsEntry("total", 0);
    verify(ipoMapper).selectList(any());
  }
}
