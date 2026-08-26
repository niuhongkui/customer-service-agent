"""语义检索模块

提供基于向量相似度的语义检索功能。
"""

from dataclasses import dataclass

from llama_index.core import VectorStoreIndex
from llama_index.core.schema import NodeWithScore


@dataclass
class RetrievalResult:
    """检索结果"""

    content: str
    score: float
    file_name: str
    chunk_index: int


def retrieve(
    index: VectorStoreIndex,
    query: str,
    top_k: int = 5,
    similarity_threshold: float = 0.6,
) -> list[RetrievalResult]:
    """执行语义检索（纯向量相似度，不依赖 LLM）

    Args:
        index: 向量索引
        query: 用户查询
        top_k: 返回前 K 个结果
        similarity_threshold: 相似度阈值，低于此值的结果降权

    Returns:
        检索结果列表
    """
    # 使用 retriever 直接检索，不经过 query_engine（避免 LLM 依赖）
    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(query)

    results = []
    for node in nodes:
        if isinstance(node, NodeWithScore) and node.score is not None:
            score = float(node.score)
            if score < similarity_threshold:
                continue  # 低相关性结果跳过

            results.append(
                RetrievalResult(
                    content=node.node.text,
                    score=score,
                    file_name=node.node.metadata.get("file_name", "unknown"),
                    chunk_index=node.node.metadata.get("chunk_index", 0),
                )
            )

    # 按相关性评分降序排列
    results.sort(key=lambda x: x.score, reverse=True)
    return results
