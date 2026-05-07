package com.hkstock.service;

import com.hkstock.entity.StockInfo;
import com.hkstock.exception.BusinessException;
import com.hkstock.mapper.StockInfoMapper;
import com.hkstock.mapper.StockKlineMapper;
import com.hkstock.mapper.StockValuationMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class StockSearchServiceTest {

    @Mock
    private StockInfoMapper stockInfoMapper;

    @Mock
    private StockKlineMapper stockKlineMapper;

    @Mock
    private StockValuationMapper valuationMapper;

    private StockService stockService;

    @BeforeEach
    void setUp() {
        stockService = new StockService();
        ReflectionTestUtils.setField(stockService, "stockInfoMapper", stockInfoMapper);
        ReflectionTestUtils.setField(stockService, "stockKlineMapper", stockKlineMapper);
        ReflectionTestUtils.setField(stockService, "valuationMapper", valuationMapper);
    }

    @Test
    void searchStocksReturnsMapperResult() {
        StockInfo tencent = new StockInfo();
        tencent.setStockCode("00700");
        tencent.setStockName("腾讯控股");
        when(stockInfoMapper.selectList(any())).thenReturn(List.of(tencent));

        List<StockInfo> result = stockService.searchStocks("腾讯");

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getStockCode()).isEqualTo("00700");
    }

    @Test
    void getLatestDailyInfoRejectsIllegalStockCode() {
        assertThatThrownBy(() -> stockService.getLatestDailyInfo("00700;drop table"))
                .isInstanceOf(BusinessException.class)
                .hasMessageContaining("股票代码格式不正确");
    }
}
