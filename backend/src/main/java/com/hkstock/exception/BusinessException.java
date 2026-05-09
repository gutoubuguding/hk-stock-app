package com.hkstock.exception;

/** Business validation exception, such as invalid parameters or forbidden business state. */
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
