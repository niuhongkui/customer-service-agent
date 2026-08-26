# 03: Pipeline 集成精排 + 依赖声明

**What to build:** RAG Pipeline 在初始化时根据配置加载精排模型，检索时自动传入 reranker 实现端到端精排。声明所需 Python 依赖。

**Blocked by:** 01: 添加精排配置字段, 02: 检索模块支持精排参数

**Status:** ready-for-agent

- [ ] `pyproject.toml` 添加 `sentence-transformers` 依赖
- [ ] `RAGPipeline.__init__` 中根据 `settings.rerank_enabled` 决定是否初始化 `SentenceTransformerRerank`
- [ ] reranker 实例存储为 `self._reranker` 属性
- [ ] reranker 初始化失败时降级为无精排模式，输出警告日志，不阻塞 Pipeline 启动
- [ ] `RAGPipeline.query()` 将 `self._reranker` 传入 `retrieve()` 调用
- [ ] `rerank_enabled=False` 时，`self._reranker` 为 `None`，检索行为与现有逻辑一致
- [ ] 端到端验证：配置 → 初始化 → 检索 → 精排 → 返回结果
