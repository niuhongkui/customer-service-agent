# RAG 精排（Reranking）功能规格说明

## Problem Statement

当前 RAG 检索管线仅依赖向量相似度（cosine similarity）对召回结果排序，存在以下问题：

1. 向量相似度是 bi-encoder 的粗排分数，无法精确捕捉 query 与 document 之间的细粒度语义相关性
2. 低相关性结果可能因向量空间中的偶然邻近而排在前面，导致 LLM 生成时受到噪声干扰
3. 检索质量的上限受限于 embedding 模型的表达能力，缺乏二次校准机制

用户期望在召回阶段之后增加一个精排（reranking）步骤，使用 cross-encoder 模型对召回结果进行重排序，提升最终输送给 LLM 的上下文质量。

## Solution

在现有 RAG 检索管线中引入 LlamaIndex 内置的 `SentenceTransformerRerank` 组件，作为向量检索之后的精排步骤。采用本地 cross-encoder 模型 `BAAI/bge-reranker-large`，对召回的候选文档进行逐对（query-document pair）精排打分，输出重排序后的 top-N 结果。

## User Stories

1. As a 银行客服系统开发者, I want RAG 检索结果经过 cross-encoder 精排, so that 输送给 LLM 的上下文相关性更高，回答质量更好
2. As a 银行客服系统开发者, I want 精排功能可通过配置开关控制（`rerank_enabled`）, so that 在调试或资源受限时可以关闭精排
3. As a 银行客服系统开发者, I want 精排模型可通过配置指定（`rerank_model`）, so that 可以灵活切换不同大小或厂商的 reranker 模型
4. As a 银行客服系统开发者, I want 精排截断数量可配置（`rerank_top_n`）, so that 可以根据业务需求调整最终保留的文档条数
5. As a 银行客服系统开发者, I want 精排模型在 Pipeline 初始化时加载一次并复用, so that 避免每次检索都重复加载模型带来的性能开销
6. As a 银行客服系统开发者, I want `retrieve()` 函数保持纯函数特性（通过参数传入 reranker）, so that 便于单元测试和 mock
7. As a 银行客服系统开发者, I want 精排过程输出调试日志（如召回条数 → 精排后保留条数）, so that 方便排查检索质量和性能问题
8. As a 银行客服系统开发者, I want 精排对下游工具层（`rag_search_tool`）透明, so that Agent 代码无需修改即可享受精排收益
9. As a 银行客服系统开发者, I want 精排使用 LlamaIndex 框架内置方法而非自定义实现, so that 降低维护成本并享受框架持续优化
10. As a 银行客服系统开发者, I want 精排后的结果仍包含原始向量相似度分数, so that 可以对比精排前后排序变化，评估精排效果
11. As a 银行客服系统开发者, I want 精排功能与现有 Milvus 向量存储和 BGE embedding 体系兼容, so that 不影响现有索引构建和检索流程
12. As a 银行客服系统开发者, I want 精排模型使用中文优化的 cross-encoder（`bge-reranker-large`）, so that 对中文银行领域文本的排序效果更好

## Implementation Decisions

### 依赖变更

- 新增 Python 依赖：`sentence-transformers`（`SentenceTransformerRerank` 的底层依赖）
- 不需要新增 llama-index 额外 reranker 包，`SentenceTransformerRerank` 已包含在 `llama-index-core` 中

### 配置模块

在 `Settings` 中新增三个字段：

- `rerank_model: str` — 精排模型名，默认 `"BAAI/bge-reranker-large"`
- `rerank_top_n: int` — 精排后保留条数，默认 `3`
- `rerank_enabled: bool` — 是否启用精排，默认 `True`

配置前缀沿用 `CSA_`，对应环境变量 `CSA_RERANK_MODEL`、`CSA_RERANK_TOP_N`、`CSA_RERANK_ENABLED`。

### 检索模块

`retrieve()` 函数签名变更：

- 新增可选参数 `reranker: SentenceTransformerRerank | None = None`
- 当 `reranker` 不为 `None` 时，在 score 过滤之后、排序之前调用 `reranker.postprocess_nodes(nodes)`
- 当 `reranker` 为 `None` 时，行为与现有逻辑完全一致（向后兼容）
- 精排后保留 `rerank_top_n` 条结果
- 添加日志：`[RERANK] 召回 {N} 条 → 精排后保留 {M} 条`

### Pipeline 模块

`RAGPipeline` 类变更：

- `__init__` 中新增 `_reranker` 属性，根据 `settings.rerank_enabled` 决定是否初始化 `SentenceTransformerRerank`
- `query()` 方法将 `self._reranker` 传入 `retrieve()` 调用
- reranker 初始化失败时降级为无精排模式并输出警告日志

### 工具层

- `rag_tools.py` **不修改**，`top_k` 默认值保持 5 不变
- 精排截断对工具层完全透明

### 数据流

```
用户查询
  ↓
index.as_retriever(similarity_top_k=10)  ← 召回 10 条
  ↓
score 过滤（similarity_threshold=0.4）
  ↓
SentenceTransformerRerank.postprocess_nodes()  ← cross-encoder 精排
  ↓
保留 top 3 条（rerank_top_n=3）
  ↓
按精排分数降序排列
  ↓
返回 RetrievalResult 列表
```

## Testing Decisions

### 测试策略

- **单元测试**：测试 `retrieve()` 函数在有/无 reranker 参数时的行为差异
- **集成测试**：测试 `RAGPipeline.query()` 在 `rerank_enabled=True/False` 时的端到端流程
- **边界测试**：测试召回结果数 < `rerank_top_n`、召回结果数 = 0 等边界情况

### 测试 seams

- **最高层 seam**：`retrieve()` 函数 — 这是精排逻辑的唯一插入点，所有测试通过此 seam 覆盖
- 现有 `retrieve()` 的纯函数特性使其易于 mock `VectorStoreIndex` 和 `SentenceTransformerRerank`
- 不需要新增测试 seam

### 测试先例

参照现有测试模式：

- `test_chunker.py` — 纯函数单元测试，无外部依赖
- `test_loader.py` — 文件系统依赖测试，条件跳过模式（`if not exists: return`）
- `test_e2e.py` — 端到端集成测试，依赖外部服务

新增测试应遵循相同模式：纯函数测试 + 条件跳过 + 集成测试分层。

## Out of Scope

- **Reranker 模型微调**：仅使用预训练模型，不涉及 fine-tuning
- **多阶段精排**：不做 multi-stage reranking（如先粗排再精排再 LLM 排序）
- **Query 改写/扩展**：不在本次范围内修改查询处理逻辑
- **异步 reranking**：当前实现为同步调用，异步优化留待后续
- **Reranker 模型量化/蒸馏**：使用模型原始精度
- **其他 reranker 实现**（Cohere、Jina 等）：仅实现 `SentenceTransformerRerank` 一种

## Further Notes

- `bge-reranker-large` 模型约 1.3GB，首次加载需要下载和初始化时间，后续复用无此开销
- cross-encoder 精排的延迟约为 50-200ms（取决于候选条数和模型大小），对整体 RAG 延迟影响可控
- 精排分数与向量相似度分数的量纲不同，`RetrievalResult.score` 将使用精排分数（当精排启用时）
