"""FastAPI 应用入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.chat import router as chat_router
from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时：初始化 RAG 知识库、加载模型等
    print(f"[START] {settings.app_name} v{settings.app_version} 启动中...")

    # 初始化 RAG Pipeline
    try:
        from src.rag.pipeline import rag_pipeline
        rag_pipeline.initialize()
        print("[OK] RAG Pipeline 初始化完成")
    except Exception as e:
        print(f"[WARN] RAG Pipeline 初始化失败: {e}")
        print("   系统将以无知识库模式运行")

    yield

    # 关闭时：释放资源
    print("[STOP] 服务关闭")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于 CrewAI 的多角色银行客服智能体系统",
    lifespan=lifespan,
)

app.include_router(chat_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.api.main:app", host=settings.api_host, port=settings.api_port, reload=settings.debug)
