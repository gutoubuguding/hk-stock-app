package com.hkstock.controller;

import com.hkstock.service.ConfigService;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.*;
import org.springframework.web.bind.annotation.*;

/**
 * 配置控制器。
 *
 * <p>只负责 HTTP 入参/出参：模型列表、当前配置、保存配置、连接测试。 真正的数据库读写已经下沉到 {@link ConfigService}，避免业务层反向依赖 Controller。
 */
@RestController
@RequestMapping("/api/config")
public class ConfigController {

  private final ConfigService configService;

  public ConfigController(ConfigService configService) {
    this.configService = configService;
  }

  /** 获取可用模型列表 */
  @GetMapping("/models")
  public Map<String, Object> getModels() {
    Map<String, Object> result = new LinkedHashMap<>();

    Map<String, String> openai = new LinkedHashMap<>();
    openai.put("provider", "openai");
    openai.put("model", "gpt-4");
    openai.put("description", "OpenAI GPT-4");
    openai.put("base_url", "https://api.openai.com/v1");
    result.put("openai", openai);

    Map<String, String> openrouterGpt55 = new LinkedHashMap<>();
    openrouterGpt55.put("provider", "openrouter");
    openrouterGpt55.put("model", "openai/gpt-5.5");
    openrouterGpt55.put("description", "GPT 5.5（OpenRouter/OpenAI-compatible）");
    openrouterGpt55.put("base_url", "https://openrouter.ai/api/v1");
    result.put("openrouter-gpt-5.5", openrouterGpt55);

    Map<String, String> openai35 = new LinkedHashMap<>();
    openai35.put("provider", "openai");
    openai35.put("model", "gpt-3.5-turbo");
    openai35.put("description", "OpenAI GPT-3.5 Turbo");
    openai35.put("base_url", "https://api.openai.com/v1");
    result.put("openai-3.5", openai35);

    Map<String, String> claude = new LinkedHashMap<>();
    claude.put("provider", "anthropic");
    claude.put("model", "claude-3-opus");
    claude.put("description", "Anthropic Claude 3 Opus");
    claude.put("base_url", "https://api.anthropic.com/v1");
    result.put("claude", claude);

    Map<String, String> deepseek = new LinkedHashMap<>();
    deepseek.put("provider", "deepseek");
    deepseek.put("model", "deepseek-chat");
    deepseek.put("description", "DeepSeek Chat");
    deepseek.put("base_url", "https://api.deepseek.com/v1");
    result.put("deepseek", deepseek);

    Map<String, String> qwen = new LinkedHashMap<>();
    qwen.put("provider", "dashscope");
    qwen.put("model", "qwen-max");
    qwen.put("description", "Alibaba Qwen Max");
    qwen.put("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1");
    result.put("qwen", qwen);

    Map<String, String> glm = new LinkedHashMap<>();
    glm.put("provider", "zhipu");
    glm.put("model", "glm-4");
    glm.put("description", "Zhipu GLM-4");
    glm.put("base_url", "https://open.bigmodel.cn/api/paas/v4");
    result.put("glm", glm);

    Map<String, String> minimax = new LinkedHashMap<>();
    minimax.put("provider", "minimax");
    minimax.put("model", "MiniMax-M2.7");
    minimax.put("description", "MiniMax M2.7");
    minimax.put("base_url", "https://api.minimax.chat/v1");
    result.put("minimax", minimax);

    Map<String, String> xiaomi = new LinkedHashMap<>();
    xiaomi.put("provider", "xiaomi");
    xiaomi.put("model", "mimo-v2-pro");
    xiaomi.put("description", "Xiaomi MiMo V2 Pro");
    xiaomi.put("base_url", "https://api.xiaomimimo.com/v1");
    result.put("xiaomi", xiaomi);

    return Map.of("models", result);
  }

  /** 获取当前配置 */
  @GetMapping("/current")
  public Map<String, Object> getCurrent() {
    // 返回 API Key：前端设置页需要展示/传递当前配置，生产环境建议改成脱敏返回。
    return configService.getCurrent();
  }

  /** 设置模型配置 - 持久化到数据库 */
  @PostMapping("/set-model")
  public Map<String, String> setModel(@RequestBody Map<String, String> body) {
    configService.updateModelConfig(body);
    return Map.of("status", "success", "message", "配置已保存");
  }

  /** 测试当前填写的 AI 模型配置是否可连通。 前端会传入未保存的表单值，所以这里不依赖已保存配置。 */
  @PostMapping("/test-connection")
  public Map<String, Object> testConnection(@RequestBody Map<String, String> body) {
    String provider = body.getOrDefault("provider", "");
    String model = body.getOrDefault("model", "");
    String apiKey = body.getOrDefault("api_key", "");
    String baseUrl = body.getOrDefault("base_url", "");

    if (model.isBlank()) {
      return Map.of("success", false, "message", "请填写模型名");
    }
    if (baseUrl.isBlank()) {
      return Map.of("success", false, "message", "请填写 API 地址");
    }
    if (baseUrl.startsWith("openclaw://")) {
      return Map.of("success", false, "message", "Codex/OpenClaw 登录模型暂不支持在此页面直接测试连接");
    }
    if (apiKey.isBlank()) {
      return Map.of("success", false, "message", "请填写 API Key");
    }

    String endpoint = buildChatCompletionsUrl(baseUrl, model);
    String payload =
        "{"
            + "\"model\":\""
            + jsonEscape(model)
            + "\","
            + "\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}],"
            + "\"temperature\":0,"
            + "\"max_tokens\":8"
            + "}";

    try {
      HttpRequest request =
          HttpRequest.newBuilder()
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
        return Map.of(
            "success", true,
            "message", "连接成功",
            "provider", provider,
            "model", model,
            "endpoint", endpoint);
      }

      return Map.of(
          "success",
          false,
          "message",
          "连接失败，HTTP " + response.statusCode() + ": " + summarizeBody(bodyText),
          "endpoint",
          endpoint);
    } catch (Exception e) {
      return Map.of("success", false, "message", "连接失败: " + e.getMessage(), "endpoint", endpoint);
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

  /** 测试 Futu OpenD TCP 端口是否可连接。 */
  @PostMapping("/test-futu")
  public Map<String, Object> testFutuConnection(@RequestBody Map<String, Object> body) {
    String host = String.valueOf(body.getOrDefault("host", "127.0.0.1"));
    int port;
    try {
      port = Integer.parseInt(String.valueOf(body.getOrDefault("port", "11111")));
    } catch (Exception e) {
      return Map.of("success", false, "message", "端口格式不正确");
    }

    try (Socket socket = new Socket()) {
      socket.connect(new InetSocketAddress(host, port), 3000);
      return Map.of("success", true, "message", "Futu OpenD 连接成功", "host", host, "port", port);
    } catch (Exception e) {
      return Map.of(
          "success",
          false,
          "message",
          "Futu OpenD 连接失败: " + e.getMessage(),
          "host",
          host,
          "port",
          port);
    }
  }
}
