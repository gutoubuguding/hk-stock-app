package com.hkstock.exception;

/** External API exception for market data, news and third-party service failures. */
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
