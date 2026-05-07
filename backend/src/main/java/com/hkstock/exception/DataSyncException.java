package com.hkstock.exception;

/**
 * 数据同步异常，例如 IPO、K 线、日历等同步任务失败。
 */
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
