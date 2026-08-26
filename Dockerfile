FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN pip install --no-cache-dir uv

# 复制依赖文件
COPY pyproject.toml ./

# 安装 Python 依赖
RUN uv sync --no-dev --no-install-project

# 复制源代码
COPY src/ ./src/
COPY knowledge/ ./knowledge/
COPY data/ ./data/

# 创建数据目录
RUN mkdir -p data

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
