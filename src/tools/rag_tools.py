"""RAG 检索工具

供 Agent 调用的知识库检索工具。
"""

import time

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from src.rag.pipeline import rag_pipeline


class RAGQueryInput(BaseModel):
    """RAG 检索输入"""

    query: str = Field(..., description="查询问题，用于在知识库中检索相关信息")
    top_k: int = Field(5, description="返回最相关的 K 个结果，默认 5")


class RAGSearchTool(BaseTool):
    """知识库语义检索工具

    在银行业务知识库中进行语义检索，返回最相关的内容片段。
    """

    name: str = "rag_search"
    description: str = (
        "在银行知识库中搜索相关信息。输入自然语言查询，返回最相关的知识片段。"
        "适用于查询银行产品信息、业务流程、规章制度等。"
    )
    args_schema: type[BaseModel] = RAGQueryInput

    def _run(self, query: str, top_k: int = 5) -> str:
        """执行知识库检索"""
        try:
            # 自动初始化 RAG Pipeline（如果尚未初始化）
            if not rag_pipeline._initialized:
                print("[RAG] 自动初始化 RAG Pipeline...")
                rag_pipeline.initialize()
                # 等待索引构建完成
                time.sleep(1)

            results = rag_pipeline.query(query, top_k=top_k)

            if not results:
                return "未在知识库中找到相关信息。建议客户联系人工客服或稍后重试。"

            # 格式化检索结果
            formatted = []
            for i, result in enumerate(results, 1):
                formatted.append(
                    f"【来源 {i}】{result.file_name}（相关度: {result.score:.2f}）\n"
                    f"{result.content}\n"
                )

            return "\n---\n".join(formatted)

        except Exception as e:
            return f"知识库检索失败: {str(e)}。建议稍后重试。"


# 创建工具实例
rag_search_tool = RAGSearchTool()
