package com.hkstock.exception;

/** Data sync exception for IPO, K-line, calendar and other scheduled jobs. */
public class DataSyncException extends RuntimeException {

  private final Integer code;

  public DataSyncException(String message) {
    this(message, null);
  }

  public DataSyncException(String message, Throwable cause) {
    super(message, cause);
    this.code = 503;
  }

  public Integer getCode() {
    return code;
  }
}
