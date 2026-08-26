"""Agent 定义测试"""

from src.agents.account import create_account_agent
from src.agents.financial import create_financial_agent
from src.agents.triage import create_triage_agent


def test_create_triage_agent():
    """测试创建分诊员 Agent"""
    agent = create_triage_agent()

    assert agent is not None
    assert agent.role == "银行客服分诊员"
    assert len(agent.tools) > 0  # 应该有 RAG 检索工具


def test_create_account_agent():
    """测试创建账户专家 Agent"""
    agent = create_account_agent()

    assert agent is not None
    assert agent.role == "银行账户专家"
    assert len(agent.tools) > 0  # 应该有多个工具


def test_create_financial_agent():
    """测试创建理财顾问 Agent"""
    agent = create_financial_agent()

    assert agent is not None
    assert agent.role == "银行理财顾问"
    assert len(agent.tools) > 0  # 应该有 RAG 检索工具


def test_agent_has_tools():
    """测试所有 Agent 都有工具"""
    agents = [
        create_triage_agent(),
        create_account_agent(),
        create_financial_agent(),
    ]

    for agent in agents:
        assert len(agent.tools) > 0, f"{agent.role} 应该有工具"
