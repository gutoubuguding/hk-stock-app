package com.hkstock.utils;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.interfaces.DecodedJWT;
import java.util.Date;
import java.util.Map;

/** JWT 工具类 */
public class JWTUtil {

    /** 生成 JWT token */
    public static String generateToken(String secret, int seconds, Map<String, String> data) {
        Algorithm algorithm = Algorithm.HMAC256(secret);
        var builder = JWT.create()
                .withExpiresAt(new Date(System.currentTimeMillis() + seconds * 1000L));

        // 将数据放入 payload
        for (Map.Entry<String, String> entry : data.entrySet()) {
            builder.withClaim(entry.getKey(), entry.getValue());
        }

        return builder.sign(algorithm);
    }

    /** 验证 token 并提取数据 */
    public static Map<String, String> verifyToken(String token, String secret, String... keys) {
        Algorithm algorithm = Algorithm.HMAC256(secret);
        DecodedJWT jwt = JWT.require(algorithm).build().verify(token);

        // 提取指定的 claims
        Map<String, String> result = new java.util.HashMap<>();
        for (String key : keys) {
            String value = jwt.getClaim(key).asString();
            if (value != null) {
                result.put(key, value);
            }
        }
        return result;
    }
}
