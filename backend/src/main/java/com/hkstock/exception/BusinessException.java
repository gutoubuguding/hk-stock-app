package com.hkstock.exception;

/** 业务校验异常，例如参数不合法、业务状态不允许等。 */
public class BusinessException extends RuntimeException {

  private final Integer code;

  public BusinessException(String message) {
    this(400, message);
  }

  public BusinessException(Integer code, String message) {
    super(message);
    this.code = code;
  }

  public Integer getCode() {
    return code;
  }
}
