package com.hkstock.dto;

import lombok.Data;

/** 设置AI模型配置请求 */
@Data
public class SetModelDTO {
    private String provider;
    private String model;
    private String apiKey;
    private String baseUrl;
}
