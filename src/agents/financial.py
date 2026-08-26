"""Financial Advisor Agent（理财顾问）

使用 ReAct 模式处理理财产品咨询、信用卡服务、贷款咨询等问题。
"""

from crewai import Agent, Task

# 导入 LLM 配置（自动设置 Ollama 环境变量）
import src.llm_config  # noqa: F401

from src.config import settings
from src.rag.prompts import FINANCIAL_ADVISOR_SYSTEM_PROMPT
from src.tools.rag_tools import rag_search_tool


def create_financial_agent() -> Agent:
    """创建理财顾问 Agent"""
    return Agent(
        role="银行理财顾问",
        goal="准确回答客户关于理财产品、信用卡服务、贷款咨询等方面的问题，提供专业的理财建议",
        backstory=FINANCIAL_ADVISOR_SYSTEM_PROMPT,
        verbose=True,
        allow_delegation=False,
        tools=[rag_search_tool],
        llm=settings.ollama_model,
    )


def create_financial_task(customer_query: str, context: str = "") -> Task:
    """创建理财咨询任务"""
    context_block = f"\n\n## 分诊员提供的上下文\n{context}" if context else ""

    return Task(
        description=(
            f"处理以下客户咨询，提供准确、专业的回答。\n\n"
            f"## 客户咨询\n{customer_query}{context_block}\n\n"
            f"## 工作流程\n"
            f"1. 先使用 rag_search 工具在知识库中检索相关信息\n"
            f"2. 基于检索到的信息，生成准确回复\n"
            f"3. 涉及投资理财时，进行风险提示\n"
            f"4. 标注信息来源\n\n"
            f"## 重要原则\n"
            f"- 仅基于检索到的知识库内容回答\n"
            f"- 不做超出知识库范围的投资承诺\n"
            f"- 所有收益数据均为历史或预期数据，不代表实际收益\n"
            f"- 投资有风险，理财需谨慎"
        ),
        expected_output=(
            "针对客户问题的专业回复，包含：\n"
            "- 准确的回答内容\n"
            "- 风险提示（如适用）\n"
            "- 信息来源标注\n"
            "- 后续建议"
        ),
        agent=create_financial_agent(),
    )
