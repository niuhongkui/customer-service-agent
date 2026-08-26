"""Crew 编排模块

管理多 Agent 协作的 Crew 创建和执行。
"""

from crewai import Crew, Process

from src.agents.account import create_account_agent, create_account_task
from src.agents.financial import create_financial_agent, create_financial_task


def _route_query(query: str) -> str:
    """基于关键词的简单路由（不依赖 LLM）"""
    account_keywords = ["账户", "转账", "挂失", "丢失", "丢了", "冻结", "投诉", "余额", "交易"]
    financial_keywords = ["理财", "信用卡", "贷款", "投资", "收益", "利率", "还款", "账单"]

    account_score = sum(1 for kw in account_keywords if kw in query)
    financial_score = sum(1 for kw in financial_keywords if kw in query)

    if account_score >= financial_score:
        return "account"
    else:
        return "financial"


def create_customer_service_crew(customer_query: str) -> Crew:
    """创建银行客服 Crew

    流程：
    1. 基于关键词路由到对应专家
    2. 专家 Agent 处理具体问题并返回回复
    """
    # 路由决策
    route = _route_query(customer_query)

    # 创建对应的 Agent 和 Task
    if route == "account":
        agent = create_account_agent()
        task = create_account_task(customer_query)
    else:
        agent = create_financial_agent()
        task = create_financial_task(customer_query)

    # 创建 Crew（单 Agent 单 Task，更稳定）
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    return crew
