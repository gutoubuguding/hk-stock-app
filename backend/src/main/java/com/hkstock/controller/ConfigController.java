package com.hkstock.controller;

import com.hkstock.common.ApiResponse;
import com.hkstock.service.ConfigService;
import jakarta.annotation.Resource;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.*;
import org.springframework.web.bind.annotation.*;

/** 配置控制器 */
@RestController
@RequestMapping("/api/config")
public class ConfigController {

    @Resource
    private ConfigService configService;

    /** 获取可用模型列表 */
    @GetMapping("/models")
    public ApiResponse<Map<String, Object>> getModels() {
        Map<String, Object> result = new LinkedHashMap<>();

        // OpenAI (2026最新)
        Map<String, String> gpt56sol = new LinkedHashMap<>();
        gpt56sol.put("provider", "openai");
        gpt56sol.put("model", "gpt-5.6-sol");
        gpt56sol.put("description", "GPT-5.6 Sol (旗舰模型，复杂推理)");
        gpt56sol.put("base_url", "https://api.openai.com/v1");
        result.put("gpt-5.6-sol", gpt56sol);

        Map<String, String> gpt56terra = new LinkedHashMap<>();
        gpt56terra.put("provider", "openai");
        gpt56terra.put("model", "gpt-5.6-terra");
        gpt56terra.put("description", "GPT-5.6 Terra (平衡智能与成本)");
        gpt56terra.put("base_url", "https://api.openai.com/v1");
        result.put("gpt-5.6-terra", gpt56terra);

        Map<String, String> gpt56luna = new LinkedHashMap<>();
        gpt56luna.put("provider", "openai");
        gpt56luna.put("model", "gpt-5.6-luna");
        gpt56luna.put("description", "GPT-5.6 Luna (性价比高)");
        gpt56luna.put("base_url", "https://api.openai.com/v1");
        result.put("gpt-5.6-luna", gpt56luna);

        // Anthropic (2026最新)
        Map<String, String> claudeFable5 = new LinkedHashMap<>();
        claudeFable5.put("provider", "anthropic");
        claudeFable5.put("model", "claude-fable-5");
        claudeFable5.put("description", "Claude Fable 5 (最强，长时间Agent)");
        claudeFable5.put("base_url", "https://api.anthropic.com/v1");
        result.put("claude-fable-5", claudeFable5);

        Map<String, String> claudeOpus48 = new LinkedHashMap<>();
        claudeOpus48.put("provider", "anthropic");
        claudeOpus48.put("model", "claude-opus-4-8");
        claudeOpus48.put("description", "Claude Opus 4.8 (复杂编码和企业)");
        claudeOpus48.put("base_url", "https://api.anthropic.com/v1");
        result.put("claude-opus-4-8", claudeOpus48);

        Map<String, String> claudeSonnet5 = new LinkedHashMap<>();
        claudeSonnet5.put("provider", "anthropic");
        claudeSonnet5.put("model", "claude-sonnet-5");
        claudeSonnet5.put("description", "Claude Sonnet 5 (速度与智能平衡)");
        claudeSonnet5.put("base_url", "https://api.anthropic.com/v1");
        result.put("claude-sonnet-5", claudeSonnet5);

        Map<String, String> claudeHaiku45 = new LinkedHashMap<>();
        claudeHaiku45.put("provider", "anthropic");
        claudeHaiku45.put("model", "claude-haiku-4-5");
        claudeHaiku45.put("description", "Claude Haiku 4.5 (最快)");
        claudeHaiku45.put("base_url", "https://api.anthropic.com/v1");
        result.put("claude-haiku-4-5", claudeHaiku45);

        // DeepSeek (2026最新)
        Map<String, String> deepseekV4Pro = new LinkedHashMap<>();
        deepseekV4Pro.put("provider", "deepseek");
        deepseekV4Pro.put("model", "deepseek-v4-pro");
        deepseekV4Pro.put("description", "DeepSeek V4 Pro (最强)");
        deepseekV4Pro.put("base_url", "https://api.deepseek.com/v1");
        result.put("deepseek-v4-pro", deepseekV4Pro);

        Map<String, String> deepseekV4Flash = new LinkedHashMap<>();
        deepseekV4Flash.put("provider", "deepseek");
        deepseekV4Flash.put("model", "deepseek-v4-flash");
        deepseekV4Flash.put("description", "DeepSeek V4 Flash (快速)");
        deepseekV4Flash.put("base_url", "https://api.deepseek.com/v1");
        result.put("deepseek-v4-flash", deepseekV4Flash);

        // Qwen 阿里 (2026最新)
        Map<String, String> qwen37max = new LinkedHashMap<>();
        qwen37max.put("provider", "dashscope");
        qwen37max.put("model", "qwen3.7-max");
        qwen37max.put("description", "Qwen 3.7 Max (最强)");
        qwen37max.put("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1");
        result.put("qwen3.7-max", qwen37max);

        Map<String, String> qwen37plus = new LinkedHashMap<>();
        qwen37plus.put("provider", "dashscope");
        qwen37plus.put("model", "qwen3.7-plus");
        qwen37plus.put("description", "Qwen 3.7 Plus (平衡)");
        qwen37plus.put("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1");
        result.put("qwen3.7-plus", qwen37plus);

        Map<String, String> qwen36flash = new LinkedHashMap<>();
        qwen36flash.put("provider", "dashscope");
        qwen36flash.put("model", "qwen3.6-flash");
        qwen36flash.put("description", "Qwen 3.6 Flash (快速)");
        qwen36flash.put("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1");
        result.put("qwen3.6-flash", qwen36flash);

        // GLM 智谱 (2026最新)
        Map<String, String> glm52 = new LinkedHashMap<>();
        glm52.put("provider", "zhipu");
        glm52.put("model", "glm-5.2");
        glm52.put("description", "GLM-5.2 (最新)");
        glm52.put("base_url", "https://open.bigmodel.cn/api/paas/v4");
        result.put("glm-5.2", glm52);

        // MiniMax (2026最新)
        Map<String, String> minimaxM3 = new LinkedHashMap<>();
        minimaxM3.put("provider", "minimax");
        minimaxM3.put("model", "MiniMax-M3");
        minimaxM3.put("description", "MiniMax M3 (最新)");
        minimaxM3.put("base_url", "https://api.minimax.chat/v1");
        result.put("minimax-m3", minimaxM3);

        // Xiaomi MiMo (2026最新)
        Map<String, String> mimoV25Pro = new LinkedHashMap<>();
        mimoV25Pro.put("provider", "xiaomi");
        mimoV25Pro.put("model", "mimo-v2.5-pro");
        mimoV25Pro.put("description", "Xiaomi MiMo V2.5 Pro (最新)");
        mimoV25Pro.put("base_url", "https://api.xiaomimimo.com/v1");
        result.put("mimo-v2.5-pro", mimoV25Pro);

        // Kimi 月之暗面
        Map<String, String> kimiK3 = new LinkedHashMap<>();
        kimiK3.put("provider", "kimi");
        kimiK3.put("model", "kimi-k3");
        kimiK3.put("description", "Kimi K3 (最新)");
        kimiK3.put("base_url", "https://api.moonshot.cn/v1");
        result.put("kimi-k3", kimiK3);

        return ApiResponse.success(Map.of("models", result));
    }

    /** 获取当前配置 */
    @GetMapping("/current")
    public ApiResponse<Map<String, Object>> getCurrent() {
        return ApiResponse.success(configService.getCurrent());
    }

    /** 设置模型配置 - 持久化到数据库 */
    @PostMapping("/set-model")
    public ApiResponse<Void> setModel(@RequestBody Map<String, String> body) {
        configService.updateModelConfig(body);
        return ApiResponse.success();
    }

    /** 测试当前填写的 AI 模型配置是否可连通 */
    @PostMapping("/test-connection")
    public ApiResponse<Map<String, Object>> testConnection(@RequestBody Map<String, String> body) {
        String provider = body.getOrDefault("provider", "");
        String model = body.getOrDefault("model", "");
        String apiKey = body.getOrDefault("api_key", "");
        String baseUrl = body.getOrDefault("base_url", "");

        if (model.isBlank()) {
            return ApiResponse.success(Map.of("success", false, "message", "请填写模型名"));
        }
        if (baseUrl.isBlank()) {
            return ApiResponse.success(Map.of("success", false, "message", "请填写 API 地址"));
        }
        if (baseUrl.startsWith("openclaw://")) {
            return ApiResponse.success(Map.of("success", false, "message", "Codex/OpenClaw 登录模型暂不支持在此页面直接测试连接"));
        }
        if (apiKey.isBlank()) {
            return ApiResponse.success(Map.of("success", false, "message", "请填写 API Key"));
        }

        String endpoint = buildChatCompletionsUrl(baseUrl, model);
        String payload = "{\"model\":\"" + jsonEscape(model) + "\","
            + "\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}],"
            + "\"temperature\":0,\"max_tokens\":8}";

        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(endpoint))
                .timeout(Duration.ofSeconds(180))
                .header("Authorization", "Bearer " + apiKey)
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(payload))
                .build();

            HttpClient client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(20)).build();
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            String bodyText = response.body() != null ? response.body() : "";

            if (response.statusCode() >= 200 && response.statusCode() < 300) {
                return ApiResponse.success(Map.of(
                    "success", true, "message", "连接成功",
                    "provider", provider, "model", model, "endpoint", endpoint));
            }
            return ApiResponse.success(Map.of(
                "success", false,
                "message", "连接失败，HTTP " + response.statusCode() + ": " + summarizeBody(bodyText),
                "endpoint", endpoint));
        } catch (Exception e) {
            return ApiResponse.success(Map.of("success", false, "message", "连接失败: " + e.getMessage(), "endpoint", endpoint));
        }
    }

    /** 测试 Futu OpenD TCP 端口是否可连接 */
    @PostMapping("/test-futu")
    public ApiResponse<Map<String, Object>> testFutuConnection(@RequestBody Map<String, Object> body) {
        String host = String.valueOf(body.getOrDefault("host", "127.0.0.1"));
        int port;
        try {
            port = Integer.parseInt(String.valueOf(body.getOrDefault("port", "11111")));
        } catch (Exception e) {
            return ApiResponse.success(Map.of("success", false, "message", "端口格式不正确"));
        }

        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress(host, port), 3000);
            return ApiResponse.success(Map.of("success", true, "message", "Futu OpenD 连接成功", "host", host, "port", port));
        } catch (Exception e) {
            return ApiResponse.success(Map.of("success", false, "message", "Futu OpenD 连接失败: " + e.getMessage(), "host", host, "port", port));
        }
    }

    private String buildChatCompletionsUrl(String baseUrl, String model) {
        String url = baseUrl.trim();
        String lower = url.toLowerCase(Locale.ROOT);
        if (lower.contains("minimax")) {
            if ((model.contains("M2.7") || !model.contains("M2.5"))
                && !lower.contains("chat/completions")
                && !lower.contains("chatcompletion_v2")) {
                return trimTrailingSlash(url) + "/chat/completions";
            }
            if (!lower.contains("chatcompletion_v2") && !lower.contains("chat/completions")) {
                return trimTrailingSlash(url) + "/text/chatcompletion_v2";
            }
            return url;
        }
        if (!lower.endsWith("/chat/completions") && !lower.endsWith("/chatcompletion_v2")) {
            return trimTrailingSlash(url) + "/chat/completions";
        }
        return url;
    }

    private String trimTrailingSlash(String value) {
        while (value.endsWith("/")) {
            value = value.substring(0, value.length() - 1);
        }
        return value;
    }

    private String jsonEscape(String value) {
        return value == null ? "" : value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private String summarizeBody(String body) {
        String compact = body == null ? "" : body.replaceAll("\\s+", " ").trim();
        return compact.length() > 240 ? compact.substring(0, 240) + "..." : compact;
    }
}
