package com.hkstock.exception;

/** 外部数据源/API 调用异常，例如行情源、新闻源、第三方接口不可用。 */
public class ExternalApiException extends RuntimeException {

  private final Integer code;

  public ExternalApiException(String message) {
    this(502, message, null);
  }

  public ExternalApiException(String message, Throwable cause) {
    this(502, message, cause);
  }

  public ExternalApiException(Integer code, String message, Throwable cause) {
    super(message, cause);
    this.code = code;
  }

  public Integer getCode() {
    return code;
  }
}
