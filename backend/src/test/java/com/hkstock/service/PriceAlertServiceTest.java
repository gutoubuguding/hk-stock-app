package com.hkstock.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.hkstock.domain.PriceAlert;
import com.hkstock.domain.StockKline;
import com.hkstock.mapper.PriceAlertMapper;
import com.hkstock.service.impl.PriceAlertServiceImpl;
import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

@ExtendWith(MockitoExtension.class)
class PriceAlertServiceTest {

    @Mock private PriceAlertMapper priceAlertMapper;
    @Mock private StockService stockService;

    private PriceAlertServiceImpl priceAlertService;

    @BeforeEach
    void setUp() {
        priceAlertService = new PriceAlertServiceImpl();
        ReflectionTestUtils.setField(priceAlertService, "priceAlertMapper", priceAlertMapper);
        ReflectionTestUtils.setField(priceAlertService, "stockService", stockService);
    }

    @Test
    void checkAlertsTriggersWhenPriceIsAboveThreshold() {
        PriceAlert alert = new PriceAlert();
        alert.setId(1L);
        alert.setStockCode("00700");
        alert.setAlertType("ABOVE");
        alert.setTargetPrice(new BigDecimal("300"));

        StockKline latest = new StockKline();
        latest.setStockCode("00700");
        latest.setClosePrice(new BigDecimal("320"));

        when(priceAlertMapper.selectList(any())).thenReturn(List.of(alert));
        when(stockService.getLatestDailyInfo("00700")).thenReturn(latest);

        List<PriceAlert> triggered = priceAlertService.checkAlerts(1L);

        assertThat(triggered).containsExactly(alert);
        assertThat(alert.getTriggered()).isTrue();
        assertThat(alert.getTriggeredAt()).isNotNull();
        verify(priceAlertMapper).updateById(alert);
    }
}
