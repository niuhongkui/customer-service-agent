# 银行客服智能体系统

基于 CrewAI 的多角色银行客服智能体集群，利用 Plan&Execute 规划模式完成客户咨询任务拆解，通过 ReAct 推理执行链路实现思考、调用工具、结果校验的完整闭环。

## 技术栈

- **API 框架**：FastAPI
- **Agent 框架**：CrewAI（Plan&Execute + ReAct）
- **RAG 框架**：LlamaIndex
- **向量数据库**：Milvus Lite（嵌入式）
- **Embedding**：BGE（bge-large-zh-v1.5）
- **大语言模型**：Ollama + Llama 3.2（本地部署）
- **包管理**：uv

## 快速开始

### 环境要求

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Ollama](https://ollama.com/) 并拉取 Llama 3.2 模型

### 安装依赖

```bash
uv sync
```

### 拉取 Ollama 模型

```bash
ollama pull llama3.2:3b
```

### 启动服务

```bash
uv run uvicorn src.api.main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档。

## Docker 部署

### 使用 Docker Compose

```bash
# 启动所有服务（API + Ollama）
docker-compose up -d

# 查看日志
docker-compose logs -f app

# 停止服务
docker-compose down
```

### 首次部署

```bash
# 1. 启动 Ollama 服务
docker-compose up -d ollama

# 2. 进入 Ollama 容器拉取模型
docker exec -it ollama ollama pull llama3.2:3b

# 3. 启动应用服务
docker-compose up -d app
```

### 访问服务

- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health
- 对话端点：POST http://localhost:8000/api/v1/chat

## API 端点

| 方法 | 路径           | 说明         |
| ---- | -------------- | ------------ |
| POST | `/api/v1/chat` | 对话测试端点 |
| GET  | `/health`      | 健康检查     |

## 项目结构

```
customer-service-agent/
├── src/
│   ├── agents/          # 智能体定义
│   ├── rag/             # RAG 知识库模块
│   ├── tools/           # Agent 工具
│   ├── api/             # FastAPI 路由
│   └── config.py        # 配置管理
├── knowledge/           # 知识库文档目录
├── tests/               # 测试文件
├── docs/                # 项目文档
├── docker-compose.yml   # Docker 部署
├── Dockerfile           # Docker 镜像构建
└── pyproject.toml       # 项目依赖
```
