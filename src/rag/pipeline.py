"""RAG Pipeline 模块

整合文档加载、切片、向量化、存储和检索的完整流程。
"""

from pathlib import Path

from llama_index.core import VectorStoreIndex

from src.config import settings
from src.rag.chunker import chunk_document
from src.rag.embedder import init_embedding
from src.rag.loader import load_documents
from src.rag.retriever import RetrievalResult, retrieve
from src.rag.vector_store import create_index, get_vector_store, load_index


class RAGPipeline:
    """RAG 知识库管道"""

    def __init__(self):
        self._index: VectorStoreIndex | None = None
        self._initialized = False

    def initialize(self, knowledge_dir: Path | None = None, force_rebuild: bool = False):
        """初始化 RAG Pipeline

        1. 加载 Embedding 模型
        2. 连接 Milvus
        3. 加载文档并建立索引

        Args:
            knowledge_dir: 知识库文档目录
            force_rebuild: 强制重建索引
        """
        if self._initialized and not force_rebuild:
            return

        doc_dir = knowledge_dir or settings.knowledge_dir

        # 初始化 Embedding 模型
        print("[INIT] 加载 Embedding 模型...")
        init_embedding(settings.embedding_model)

        # 连接 Milvus
        print("[INIT] 连接 Milvus...")
        vector_store = get_vector_store()

        # 检查是否需要重建
        need_rebuild = force_rebuild
        if not need_rebuild:
            try:
                # 尝试加载索引并验证是否有数据
                idx = load_index(vector_store)
                # 用一个测试查询验证索引是否有数据
                test_results = retrieve(idx, "测试", top_k=1, similarity_threshold=0.0)
                if len(test_results) > 0:
                    self._index = idx
                    print("[OK] 已加载现有索引")
                else:
                    need_rebuild = True
                    print("[WARN] 索引为空，将重新构建")
            except Exception:
                need_rebuild = True

        if need_rebuild:
            # 从文档创建索引
            print("[INIT] 加载文档...")
            documents = load_documents(doc_dir)

            if not documents:
                print("[WARN] 未找到文档，创建空索引")
                from llama_index.core import Document
                documents = [Document(text="占位文档，请上传业务文档到 knowledge 目录")]

            # 切片
            print("[INIT] 文档切片...")
            chunks = []
            for doc in documents:
                doc_chunks = chunk_document(
                    doc,
                    chunk_size=settings.chunk_size,
                    chunk_overlap=settings.chunk_overlap,
                )
                chunks.extend(doc_chunks)

            print(f"[INIT] 切片完成: {len(documents)} 个文档 -> {len(chunks)} 个切片")

            # 创建索引
            print("[INIT] 构建向量索引...")
            self._index = create_index(vector_store, chunks)
            print("[OK] 索引构建完成")

        self._initialized = True

    def query(self, question: str, top_k: int | None = None) -> list[RetrievalResult]:
        """执行语义检索"""
        if not self._initialized:
            raise RuntimeError("RAG Pipeline 未初始化，请先调用 initialize()")

        return retrieve(
            index=self._index,
            query=question,
            top_k=top_k or settings.retrieval_top_k,
            similarity_threshold=settings.similarity_threshold,
        )

    def rebuild(self, knowledge_dir: Path | None = None):
        """重建索引（删除旧索引后重新构建）"""
        self._initialized = False
        self._index = None

        # 删除旧的 Milvus 数据
        vector_store = get_vector_store()
        vector_store.close()

        # 重新初始化
        self.initialize(knowledge_dir)


# 全局单例
rag_pipeline = RAGPipeline()
