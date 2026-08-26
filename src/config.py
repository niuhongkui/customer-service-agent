"""应用配置管理"""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    app_name: str = "银行客服智能体"
    app_version: str = "0.1.0"
    debug: bool = True

    # Ollama 配置
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    # Embedding 配置
    embedding_model: str = "BAAI/bge-large-zh-v1.5"
    embedding_dim: int = 1024

    # Milvus 配置
    milvus_uri: str = "./data/milvus.db"
    milvus_collection: str = "bank_knowledge"

    # RAG 配置
    chunk_size: int = 512
    chunk_overlap: int = 50
    retrieval_top_k: int = 5
    similarity_threshold: float = 0.4

    # 知识库文档目录
    knowledge_dir: Path = Path("./knowledge")

    # API 配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    model_config = {"env_prefix": "CSA_"}


settings = Settings()
