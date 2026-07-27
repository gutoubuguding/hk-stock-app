package com.hkstock.interceptor;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.hkstock.common.ApiResponse;
import com.hkstock.utils.JWTUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

/** Token 拦截器 */
@Component
public class TokenInterceptor implements HandlerInterceptor {

    @Value("${secret:}")
    private String secret;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        // OPTIONS 预检请求直接放行
        if ("OPTIONS".equalsIgnoreCase(request.getMethod())) {
            return true;
        }

        // 从请求头获取 token
        String token = request.getHeader("token");

        // token 为空
        if (token == null || token.isEmpty()) {
            response.setStatus(401);
            response.setContentType("application/json;charset=utf-8");
            response.getWriter().write(objectMapper.writeValueAsString(
                    ApiResponse.error(401, "未登录")));
            return false;
        }

        // 验证 token
        try {
            JWTUtil.verifyToken(token, secret, "username", "id");
            return true;
        } catch (Exception e) {
            response.setStatus(401);
            response.setContentType("application/json;charset=utf-8");
            response.getWriter().write(objectMapper.writeValueAsString(
                    ApiResponse.error(401, "非法token")));
            return false;
        }
    }
}
