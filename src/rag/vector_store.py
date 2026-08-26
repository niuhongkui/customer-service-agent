"""Milvus 向量数据库模块

管理 Milvus Lite 的连接、集合创建和数据写入。
"""

from pathlib import Path

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.milvus import MilvusVectorStore

from src.config import settings


def _ensure_collection_loaded():
    """确保 Milvus 集合已加载到内存"""
    try:
        from pymilvus import MilvusClient
        client = MilvusClient(uri=settings.milvus_uri)
        try:
            client.load_collection(settings.milvus_collection)
            print(f"[MILVUS] 集合 {settings.milvus_collection} 已加载到内存")
        except Exception:
            # 集合可能不存在，忽略
            pass
        finally:
            client.close()
    except Exception as e:
        print(f"[MILVUS] 加载集合失败: {e}")


def get_vector_store() -> MilvusVectorStore:
    """获取 Milvus 向量存储实例（使用统一配置）"""
    # 确保目录存在
    Path(settings.milvus_uri).parent.mkdir(parents=True, exist_ok=True)

    vector_store = MilvusVectorStore(
        uri=settings.milvus_uri,
        collection_name=settings.milvus_collection,
        dim=settings.embedding_dim,
        overwrite=False,
    )

    _ensure_collection_loaded()
    return vector_store


def create_index(
    vector_store: MilvusVectorStore,
    documents: list,
) -> VectorStoreIndex:
    """从文档创建向量索引"""
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
    )

    _ensure_collection_loaded()
    return index


def load_index(
    vector_store: MilvusVectorStore,
) -> VectorStoreIndex:
    """从已有向量存储加载索引"""
    _ensure_collection_loaded()

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context,
    )
