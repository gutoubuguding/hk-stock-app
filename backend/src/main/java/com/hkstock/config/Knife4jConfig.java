package com.hkstock.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** Knife4j API 文档配置 */
@Configuration
public class Knife4jConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("港股智能分析平台 API")
                        .version("1.0.0")
                        .description("港股智能分析平台后端接口文档")
                        .contact(new Contact()
                                .name("HK Stock Intelligence Platform")
                                .email("admin@hkstock.com")));
    }
}
