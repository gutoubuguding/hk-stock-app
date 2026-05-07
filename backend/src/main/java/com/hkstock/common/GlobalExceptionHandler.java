package com.hkstock.common;

import com.hkstock.exception.AiServiceException;
import com.hkstock.exception.BusinessException;
import com.hkstock.exception.DataSyncException;
import com.hkstock.exception.ExternalApiException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * 全局异常处理，保证接口失败时也返回稳定的 code/message/data 结构。
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(BusinessException.class)
    public ApiResponse<Void> handleBusinessException(BusinessException e) {
        log.warn("业务异常: {}", e.getMessage());
        return ApiResponse.fail(e.getCode(), e.getMessage());
    }

    @ExceptionHandler(AiServiceException.class)
    public ApiResponse<Void> handleAiServiceException(AiServiceException e) {
        log.error("AI 服务异常: {}", e.getMessage(), e);
        return ApiResponse.fail(e.getCode(), "AI 服务暂时不可用：" + e.getMessage());
    }

    @ExceptionHandler(ExternalApiException.class)
    public ApiResponse<Void> handleExternalApiException(ExternalApiException e) {
        log.error("外部接口异常: {}", e.getMessage(), e);
        return ApiResponse.fail(e.getCode(), "外部数据源暂时不可用：" + e.getMessage());
    }

    @ExceptionHandler(DataSyncException.class)
    public ApiResponse<Void> handleDataSyncException(DataSyncException e) {
        log.error("数据同步异常: {}", e.getMessage(), e);
        return ApiResponse.fail(e.getCode(), "数据同步失败：" + e.getMessage());
    }

    @ExceptionHandler(Exception.class)
    public ApiResponse<Void> handleException(Exception e) {
        log.error("未处理异常: {}", e.getMessage(), e);
        return ApiResponse.fail("服务器内部错误：" + e.getMessage());
    }
}
