"""LLM 配置模块

配置 CrewAI 使用 Ollama 作为 LLM 后端。
"""

import os

from src.config import settings


def setup_ollama_llm():
    """配置 Ollama 作为 CrewAI 的 LLM 后端

    CrewAI 通过 OpenAI 兼容 API 连接 Ollama，
    需要设置 OPENAI_API_BASE 和 OPENAI_API_KEY。
    """
    # 设置 Ollama API 地址（OpenAI 兼容格式）
    os.environ["OPENAI_API_BASE"] = settings.ollama_base_url + "/v1"

    # 设置一个虚拟 API Key（Ollama 不需要真实 key）
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "ollama"

    return settings.ollama_model


# 模块加载时自动配置
setup_ollama_llm()
