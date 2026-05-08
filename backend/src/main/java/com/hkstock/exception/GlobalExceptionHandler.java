package com.hkstock.exception;

import com.hkstock.common.ApiResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/** 全局异常处理器，保证所有接口异常都返回统一的 ApiResponse 结构。 */
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
    return ApiResponse.fail(502, e.getMessage());
  }

  @ExceptionHandler(ExternalApiException.class)
  public ApiResponse<Void> handleExternalApiException(ExternalApiException e) {
    log.error("外部接口异常: {}", e.getMessage(), e);
    return ApiResponse.fail(502, e.getMessage());
  }

  @ExceptionHandler(DataSyncException.class)
  public ApiResponse<Void> handleDataSyncException(DataSyncException e) {
    log.error("数据同步异常: {}", e.getMessage(), e);
    return ApiResponse.fail(e.getCode(), e.getMessage());
  }

  @ExceptionHandler({MethodArgumentNotValidException.class, MissingServletRequestParameterException.class})
  public ApiResponse<Void> handleValidationException(Exception e) {
    log.warn("请求参数不合法: {}", e.getMessage());
    return ApiResponse.fail(400, "请求参数不合法");
  }

  @ExceptionHandler(Exception.class)
  public ApiResponse<Void> handleException(Exception e) {
    log.error("未处理异常: {}", e.getMessage(), e);
    return ApiResponse.fail(500, "服务器内部错误");
  }
}
