# RAG 检索排序逻辑研究

## 概述

本文档追踪从用户输入问题到返回检索结果的完整数据流，解释知识库如何被检索（召回）以及结果如何排序。

## 完整数据流

```
用户提问: "行内转账手续费是多少？"
   ↓
[1] 文档加载 (loader.py)
   ↓
[2] 语义切片 (chunker.py)
   ↓
[3] Embedding 向量化 (embedder.py)
   ↓
[4] Milvus 存储 (vector_store.py)
   ↓
=== 以上是离线索引阶段 ===
   ↓
[5] 用户查询向量化 (embedder.py)
   ↓
[6] 向量相似度检索 (retriever.py)
   ↓
[7] 阈值过滤 + 排序 (retriever.py)
   ↓
[8] 格式化返回 (rag_tools.py)
   ↓
返回: 检索结果列表
```

## 阶段一：离线索引构建

### 1. 文档加载 (`src/rag/loader.py`)

**职责**：读取知识库目录下的文件，转换为 LlamaIndex Document 对象。

- **支持格式**：`.docx`（Word）、`.md`（Markdown）、`.txt`（纯文本）
- **加载方式**：
  - Word：使用 `python-docx` 提取段落文本
  - Markdown：先转 HTML 再去除标签，保留段落结构
  - TXT：直接读取 UTF-8 编码内容
- **元数据**：每个 Document 附带 `file_name`、`file_path`、`file_type`

> 来源：`src/rag/loader.py:36-56`

### 2. 语义切片 (`src/rag/chunker.py`)

**职责**：将长文档切分为适合向量化的小片段。

**切片策略（三步走）**：

1. **按段落分割**：以 `\n\n`（空行）为分隔符切分文本
2. **超长段落硬切**：超过 `chunk_size`（默认 512 字符）的段落，按 `chunk_size - chunk_overlap` 步长滑窗切分
3. **合并过小切片**：小于 `chunk_size // 2`（256 字符）的相邻切片合并

**保留标题上下文**：
- 检测 Markdown `#` 标题层级
- 切片时记录当前所属章节标题
- 结果中标记 `has_heading: True`

> 来源：`src/rag/chunker.py:48-109`

### 3. Embedding 向量化 (`src/rag/embedder.py`)

**职责**：将文本切片转换为 1024 维向量。

- **模型**：`BAAI/bge-large-zh-v1.5`（中文优化的 BERT-based Embedding）
- **维度**：1024
- **初始化**：通过 LlamaIndex 的 `HuggingFaceEmbedding` 加载本地模型权重
- **全局注册**：设置到 `Settings.embed_model`，LlamaIndex 后续自动使用

> 来源：`src/rag/embedder.py:10-22`、`src/config.py:21-22`

### 4. Milvus 存储 (`src/rag/vector_store.py`)

**职责**：将向量写入 Milvus Lite，建立索引。

- **存储引擎**：Milvus Lite（嵌入式，数据存于 `./data/milvus.db`）
- **集合名**：`bank_knowledge`
- **写入流程**：
  1. `VectorStoreIndex.from_documents()` 自动对每个切片调用 Embedding 模型生成向量
  2. 向量 + 原文 + 元数据写入 Milvus 集合
  3. 写入后调用 `load_collection()` 确保集合加载到内存

> 来源：`src/rag/vector_store.py:14-74`

---

## 阶段二：在线检索

### 5. 用户查询向量化

当用户提问时，同一个 BGE 模型将查询文本转换为 1024 维向量。

**调用链路**：
```
rag_search_tool._run(query)
  → rag_pipeline.query(query)
    → retrieve(index, query)
      → index.as_retriever(similarity_top_k=5)
      → retriever.retrieve(query)
```

> 来源：`src/tools/rag_tools.py:34-57` → `src/rag/pipeline.py:96-106` → `src/rag/retriever.py:39-41`

### 6. 向量相似度检索 (`src/rag/retriever.py`)

**核心机制**：使用 LlamaIndex 的 `VectorStoreIndex.as_retriever()` 执行向量检索。

```python
retriever = index.as_retriever(similarity_top_k=top_k)
nodes = retriever.retrieve(query)
```

**底层原理**：
1. 用户查询被 BGE 模型编码为查询向量
2. Milvus 在 `bank_knowledge` 集合中执行**向量近似最近邻搜索（ANN）**
3. 返回 `top_k`（默认 5）个与查询向量最相似的文档切片
4. 每个结果附带**相似度评分（score）**

> 来源：`src/rag/retriever.py:39-41`

### 7. 阈值过滤 + 排序 (`src/rag/retriever.py`)

**过滤逻辑**：
```python
for node in nodes:
    score = float(node.score)
    if score < similarity_threshold:  # 默认 0.4
        continue  # 低于阈值，丢弃该结果
```

- **相似度阈值**：`0.4`（可在 `src/config.py` 中调整）
- **行为**：低于阈值的检索结果直接丢弃，不返回给 Agent

**排序逻辑**：
```python
results.sort(key=lambda x: x.score, reverse=True)
```

- **排序依据**：相似度评分（score），值越大表示与查询越相关
- **排序方向**：降序（最相关的排在最前面）

**相似度评分说明**：
- 评分范围：通常在 0.0 ~ 1.0 之间
- 评分来源：向量之间的余弦相似度（由 Milvus 计算）
- 评分越高 = 语义越接近 = 越可能是用户想要的答案

> 来源：`src/rag/retriever.py:44-61`

### 8. 格式化返回 (`src/tools/rag_tools.py`)

Agent 调用 `rag_search` 工具后，检索结果被格式化为文本：

```
【来源 1】账户业务指南.md（相关度: 0.63）
行内转账手续费为 0 元...

---
【来源 2】贷款业务指南.md（相关度: 0.56）
...
```

每条结果包含：来源文件名、相关度评分、切片原文内容。

> 来源：`src/tools/rag_tools.py:44-56`

---

## 关键配置参数

| 参数 | 默认值 | 位置 | 说明 |
|------|--------|------|------|
| `embedding_model` | `BAAI/bge-large-zh-v1.5` | `config.py:21` | Embedding 模型 |
| `embedding_dim` | `1024` | `config.py:22` | 向量维度 |
| `chunk_size` | `512` | `config.py:29` | 切片最大字符数 |
| `chunk_overlap` | `50` | `config.py:30` | 硬切分时的重叠字符数 |
| `retrieval_top_k` | `5` | `config.py:31` | 返回前 K 个结果 |
| `similarity_threshold` | `0.4` | `config.py:32` | 相似度阈值，低于则丢弃 |
| `milvus_collection` | `bank_knowledge` | `config.py:26` | Milvus 集合名 |

---

## 检索质量验证

### 测试结果（test_local.py）

| 查询 | 期望来源 | 实际召回 | 评分 |
|------|----------|----------|------|
| 行内转账手续费是多少？ | 账户业务指南.md | 账户业务指南.md | 0.625 |
| 定期存款的利率是多少？ | 理财产品手册.md | 贷款业务指南.md | 0.447 |
| 信用卡年费是多少？ | 信用卡服务指南.md | 信用卡服务指南.md | 0.608 |
| 贷款申请需要什么条件？ | 贷款业务指南.md | 贷款业务指南.md | 0.561 |
| 如何冻结账户？ | 账户业务指南.md | 账户业务指南.md | 0.521 |
| 理财产品有哪些风险等级？ | 理财产品手册.md | 理财产品手册.md | 0.633 |

**召回率：6/6 = 100%**

---

## 总结

检索排序的核心逻辑：

1. **向量化**：BGE 模型将文本转为 1024 维向量
2. **近似最近邻搜索**：Milvus 在向量空间中找到最相似的 Top-K 个切片
3. **阈值过滤**：相似度低于 0.4 的结果被丢弃
4. **降序排列**：按相似度从高到低排序返回

这是一种标准的**稠密向量检索（Dense Retrieval）**方案，依赖 Embedding 模型的语义理解能力，而非关键词匹配。
