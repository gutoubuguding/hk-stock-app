package com.hkstock.exception;

/** Exception thrown when the AI microservice call fails. */
public class AiServiceException extends ExternalApiException {

  public AiServiceException(String message) {
    super(502, message, null);
  }

  public AiServiceException(String message, Throwable cause) {
    super(502, message, cause);
  }
}
