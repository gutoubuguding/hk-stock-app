package com.hkstock.common;

import lombok.Data;

/**
 * 统一API响应包装类
 *
 * @param <T> 业务数据类型
 */
@Data
public class ApiResponse<T> {

    private Integer code;
    private String message;
    private Long total;
    private T data;

    public ApiResponse() {}

    public ApiResponse(Integer code, String message, T data) {
        this.code = code;
        this.message = message;
        this.data = data;
    }

    public ApiResponse(Integer code, String message, Long total, T data) {
        this.code = code;
        this.message = message;
        this.total = total;
        this.data = data;
    }

    // ========== 成功响应 ==========

    public static <T> ApiResponse<T> success() {
        return new ApiResponse<>(200, "success", null);
    }

    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(200, "success", data);
    }

    public static <T> ApiResponse<T> success(String message, T data) {
        return new ApiResponse<>(200, message, data);
    }

    public static <T> ApiResponse<T> success(Long total, T data) {
        return new ApiResponse<>(200, "success", total, data);
    }

    // ========== 失败响应 ==========

    public static <T> ApiResponse<T> error(String message) {
        return new ApiResponse<>(500, message, null);
    }

    public static <T> ApiResponse<T> error(Integer code, String message) {
        return new ApiResponse<>(code, message, null);
    }
}
