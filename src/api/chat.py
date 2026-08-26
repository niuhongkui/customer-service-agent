"""对话端点"""

import asyncio
import traceback
from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel, Field

from fastapi import APIRouter

from src.agents.crew import create_customer_service_crew

router = APIRouter(tags=["chat"])

# 线程池执行器，用于运行同步的 CrewAI 任务
_executor = ThreadPoolExecutor(max_workers=2)


class ChatRequest(BaseModel):
    """对话请求"""

    message: str = Field(..., description="用户消息", min_length=1, max_length=2000)
    session_id: str | None = Field(None, description="会话 ID，用于多轮对话")


class ChatResponse(BaseModel):
    """对话响应"""

    reply: str = Field(..., description="Agent 回复")
    agent: str = Field(..., description="处理该请求的 Agent 名称")
    reasoning_steps: list[str] = Field(default_factory=list, description="推理过程（可选）")
    sources: list[str] = Field(default_factory=list, description="信息来源文档")


def _execute_crew_sync(query: str) -> str:
    """同步执行 CrewAI 任务（在线程池中运行）"""
    crew = create_customer_service_crew(query)
    result = crew.kickoff()
    return str(result) if result else ""


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """对话测试端点

    接收用户消息，通过 CrewAI 多 Agent 协作处理并返回回复。
    """
    try:
        # 在线程池中执行同步的 CrewAI 任务
        loop = asyncio.get_event_loop()
        reply = await loop.run_in_executor(
            _executor,
            _execute_crew_sync,
            request.message,
        )

        if not reply:
            reply = "抱歉，暂时无法处理您的请求。"

        # 提取推理步骤
        reasoning_steps = _extract_reasoning(reply)

        # 提取信息来源
        sources = _extract_sources(reply)

        # 确定处理 Agent
        agent = _determine_agent(request.message, reply)

        return ChatResponse(
            reply=reply,
            agent=agent,
            reasoning_steps=reasoning_steps,
            sources=sources,
        )

    except Exception as e:
        # 记录详细错误日志
        print(f"[ERROR] /chat 执行失败: {e}")
        traceback.print_exc()

        # 返回友好的错误信息（不再抛出 500）
        return ChatResponse(
            reply=f"抱歉，处理您的请求时遇到了问题。请稍后重试。\n错误信息: {str(e)[:200]}",
            agent="system",
            reasoning_steps=[],
            sources=[],
        )


def _extract_reasoning(reply: str) -> list[str]:
    """从回复中提取推理步骤"""
    steps = []
    lines = reply.split("\n")
    for line in lines:
        line = line.strip()
        # 识别推理步骤标记
        if any(
            keyword in line
            for keyword in ["意图分析", "路由决策", "路由理由", "思考", "分析", "理由"]
        ):
            steps.append(line)
    return steps


def _extract_sources(reply: str) -> list[str]:
    """从回复中提取信息来源"""
    sources = []
    lines = reply.split("\n")
    for line in lines:
        line = line.strip()
        # 识别来源标记
        if "来源" in line and (
            "文档" in line or "文件" in line or ".md" in line or ".docx" in line
        ):
            sources.append(line)
    return sources


def _determine_agent(query: str, reply: str) -> str:
    """根据查询和回复判断处理 Agent"""
    # 优先根据用户查询判断
    if any(kw in query for kw in ["账户", "转账", "挂失", "丢失", "丢了", "冻结", "投诉"]):
        return "Account Agent（账户专家）"
    elif any(kw in query for kw in ["理财", "信用卡", "贷款", "投资"]):
        return "Financial Advisor Agent（理财顾问）"

    # 其次根据回复内容判断
    reply_lower = reply.lower()
    if any(keyword in reply_lower for keyword in ["账户", "转账", "挂失", "冻结", "投诉"]):
        return "Account Agent（账户专家）"
    elif any(keyword in reply_lower for keyword in ["理财", "信用卡", "贷款", "投资"]):
        return "Financial Advisor Agent（理财顾问）"
    else:
        return "Triage Agent（分诊员）"
