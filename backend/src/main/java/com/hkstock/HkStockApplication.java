package com.hkstock;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@MapperScan("com.hkstock.mapper")
@EnableScheduling
public class HkStockApplication {

    public static void main(String[] args) {
        SpringApplication.run(HkStockApplication.class, args);
    }
}
