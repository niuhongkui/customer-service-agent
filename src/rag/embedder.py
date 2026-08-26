"""Embedding 向量化模块

使用 BGE 模型进行中文语义向量化。
"""

from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def get_embedding_model(model_name: str = "BAAI/bge-large-zh-v1.5") -> HuggingFaceEmbedding:
    """获取 BGE Embedding 模型实例"""
    return HuggingFaceEmbedding(
        model_name=model_name,
        trust_remote_code=True,
    )


def init_embedding(model_name: str = "BAAI/bge-large-zh-v1.5") -> HuggingFaceEmbedding:
    """初始化 Embedding 模型并设置到全局 Settings"""
    embed_model = get_embedding_model(model_name)
    Settings.embed_model = embed_model
    return embed_model
