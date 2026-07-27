package com.hkstock.service;

import java.util.Map;

/** 系统配置服务接口 */
public interface ConfigService {

    /** 返回当前配置副本 */
    Map<String, Object> getCurrent();

    /** 获取可用于 AI 调用的配置 */
    Map<String, Object> getRequiredAiConfig();

    /** 更新并持久化 AI 模型配置 */
    void updateModelConfig(Map<String, String> body);
}
