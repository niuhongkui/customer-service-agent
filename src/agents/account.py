"""Account Agent（账户专家）

使用 ReAct 模式处理账户查询、转账、挂失、投诉等问题。
"""

from crewai import Agent, Task

# 导入 LLM 配置（自动设置 Ollama 环境变量）
import src.llm_config  # noqa: F401

from src.config import settings
from src.rag.prompts import ACCOUNT_SYSTEM_PROMPT
from src.tools.bank_tools import account_query_tool, freeze_account_tool, transfer_tool
from src.tools.rag_tools import rag_search_tool


def create_account_agent() -> Agent:
    """创建账户专家 Agent"""
    return Agent(
        role="银行账户专家",
        goal="准确回答客户关于账户操作、转账汇款、挂失安全、投诉工单等方面的问题",
        backstory=ACCOUNT_SYSTEM_PROMPT,
        verbose=True,
        allow_delegation=False,
        tools=[rag_search_tool, account_query_tool, transfer_tool, freeze_account_tool],
        llm=settings.ollama_model,
    )


def create_account_task(customer_query: str, context: str = "") -> Task:
    """创建账户咨询任务"""
    context_block = f"\n\n## 分诊员提供的上下文\n{context}" if context else ""

    return Task(
        description=(
            f"处理以下客户咨询，提供准确、专业的回答。\n\n"
            f"## 客户咨询\n{customer_query}{context_block}\n\n"
            f"## 工作流程\n"
            f"1. 先使用 rag_search 工具在知识库中检索相关信息\n"
            f"2. 如果需要查询具体账户信息，使用 account_query 工具\n"
            f"3. 如果涉及转账操作，使用 transfer 工具\n"
            f"4. 如果涉及挂失/冻结，使用 freeze_account 工具\n"
            f"5. 基于检索到的信息和工具返回结果，生成准确回复\n"
            f"6. 标注信息来源\n\n"
            f"## 重要原则\n"
            f"- 仅基于检索到的知识库内容回答\n"
            f"- 不确定时明确告知客户\n"
            f"- 涉及资金操作时提醒注意安全"
        ),
        expected_output=(
            "针对客户问题的专业回复，包含：\n"
            "- 准确的回答内容\n"
            "- 信息来源标注\n"
            "- 必要的操作建议或注意事项"
        ),
        agent=create_account_agent(),
    )
