package com.hkstock.exception;

/**
 * AI 微服务调用异常。
 */
public class AiServiceException extends ExternalApiException {

    public AiServiceException(String message) {
        super(502, message, null);
    }

    public AiServiceException(String message, Throwable cause) {
        super(502, message, cause);
    }
}
