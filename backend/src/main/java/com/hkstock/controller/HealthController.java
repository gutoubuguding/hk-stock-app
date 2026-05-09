package com.hkstock.controller;

import com.hkstock.common.ApiResponse;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** Lightweight service health endpoint that does not depend on business data. */
@RestController
@RequestMapping("/api/health")
public class HealthController {

  @GetMapping
  public ApiResponse<Map<String, String>> health() {
    return ApiResponse.success(Map.of("status", "UP"));
  }
}
