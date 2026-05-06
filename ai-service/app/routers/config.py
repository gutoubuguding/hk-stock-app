"""
LLM配置管理路由
- 支持配置多个LLM模型
- 支持切换当前使用的模型
"""
from fastapi import APIRouter, Query
from typing import Dict, Any, List
from pydantic import BaseModel

router = APIRouter()


class LlmConfig(BaseModel):
    """LLM配置"""
    provider: str  # minimax, openai, claude, etc.
    model: str
    api_key: str
    base_url: str = ""


# 预设的LLM配置模板
LLM_TEMPLATES = {
    "minimax": {
        "provider": "minimax",
        "model": "MiniMax-M2.7",
        "base_url": "https://api.minimax.chat/v1/text/chatcompletion_v2",
        "description": "MiniMax M2.7 模型"
    },
    "minimax_m2.1": {
        "provider": "minimax",
        "model": "MiniMax-M2.1",
        "base_url": "https://api.minimax.chat/v1/text/chatcompletion_v2",
        "description": "MiniMax M2.1 模型"
    },
    "minimax_m2.5": {
        "provider": "minimax",
        "model": "MiniMax-M2.5",
        "base_url": "https://api.minimax.chat/v1/text/chatcompletion_v2",
        "description": "MiniMax M2.5 模型"
    },
    "openai": {
        "provider": "openai",
        "model": "gpt-4",
        "base_url": "https://api.openai.com/v1/chat/completions",
        "description": "OpenAI GPT-4"
    },
    "claude": {
        "provider": "claude",
        "model": "claude-3-opus-20240229",
        "base_url": "https://api.anthropic.com/v1/messages",
        "description": "Claude 3 Opus"
    }
}

# 当前激活的LLM配置
active_config: Dict[str, Any] = {
    "provider": "",
    "model": "",
    "api_key": "",
    "base_url": ""
}


@router.get("/models")
def get_available_models() -> Dict[str, Any]:
    """获取可用的LLM模型列表"""
    return {
        "models": LLM_TEMPLATES,
        "active": active_config
    }


@router.post("/set-model")
def set_model(config: LlmConfig) -> Dict[str, Any]:
    """设置当前使用的LLM模型"""
    global active_config
    active_config = {
        "provider": config.provider,
        "model": config.model,
        "api_key": config.api_key,
        "base_url": config.base_url or LLM_TEMPLATES.get(config.provider, {}).get("base_url", "")
    }

    # 同步更新 analyze 模块的配置
    from app.routers.analyze import llm_config
    llm_config.update(active_config)

    return {
        "status": "success",
        "message": f"已切换到 {config.provider} - {config.model}",
        "active": active_config
    }


@router.get("/current")
def get_current_config() -> Dict[str, Any]:
    """获取当前LLM配置（隐藏API Key）"""
    safe_config = active_config.copy()
    if safe_config.get("api_key"):
        safe_config["api_key"] = safe_config["api_key"][:8] + "****"
    return safe_config
