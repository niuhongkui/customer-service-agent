"""Triage Agent（分诊员）

分析用户意图并路由到对应专家。
"""

from crewai import Agent, Task

# 导入 LLM 配置（自动设置 Ollama 环境变量）
import src.llm_config  # noqa: F401

from src.config import settings
from src.rag.prompts import TRIAGE_SYSTEM_PROMPT


def create_triage_agent() -> Agent:
    """创建分诊员 Agent"""
    return Agent(
        role="银行客服分诊员",
        goal="准确分析客户问题意图，将请求路由到最合适的专家处理",
        backstory=TRIAGE_SYSTEM_PROMPT,
        verbose=True,
        allow_delegation=False,
        tools=[],  # 分诊员不需要工具，只做意图分析和路由
        llm=settings.ollama_model,
    )


def create_triage_task(customer_query: str) -> Task:
    """创建分诊任务"""
    return Task(
        description=(
            f"分析以下客户咨询，判断其意图并给出路由建议。\n\n"
            f"客户咨询：{customer_query}\n\n"
            f"请直接输出以下格式（不要使用工具，不要输出其他内容）：\n\n"
            f"路由决策：[Account Agent 或 Financial Advisor Agent]\n"
            f"理由：[简短说明]"
        ),
        expected_output=(
            "格式如下：\n"
            "路由决策：Account Agent\n"
            "理由：客户询问的是账户相关问题"
        ),
        agent=create_triage_agent(),
    )
