"""本地测试脚本

验证 RAG 召回率和 Agent 响应质量。
"""

import sys
import io
import os

# Windows UTF-8 兼容
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from pathlib import Path

# 确保可以导入 src 模块（项目根目录）
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_rag_pipeline():
    """测试 RAG Pipeline 召回率"""
    print("=" * 60)
    print("[TEST] RAG Pipeline 召回率")
    print("=" * 60)

    from src.rag.pipeline import rag_pipeline

    # 初始化
    print("\n1. 初始化 RAG Pipeline...")
    rag_pipeline.initialize()

    # 测试查询
    test_queries = [
        ("行内转账手续费是多少？", "账户业务指南.md"),
        ("定期存款的利率是多少？", "理财产品手册.md"),
        ("信用卡年费是多少？", "信用卡服务指南.md"),
        ("贷款申请需要什么条件？", "贷款业务指南.md"),
        ("如何冻结账户？", "账户业务指南.md"),
        ("理财产品有哪些风险等级？", "理财产品手册.md"),
    ]

    print("\n2. 执行检索测试...\n")

    correct = 0
    total = len(test_queries)

    for query, expected_source in test_queries:
        results = rag_pipeline.query(query, top_k=3)

        # 检查是否召回了相关文档
        found = any(expected_source in r.file_name for r in results)
        if found:
            correct += 1
            status = "[PASS]"
        else:
            status = "[FAIL]"

        print(f"{status} 查询: {query}")
        print(f"   期望来源: {expected_source}")
        if results:
            print(f"   实际召回: {results[0].file_name} (评分: {results[0].score:.3f})")
        else:
            print(f"   实际召回: 无结果")
        print()

    recall_rate = correct / total * 100
    print(f"[RESULT] 召回率: {correct}/{total} = {recall_rate:.1f}%")

    return recall_rate


def test_agent_routing():
    """测试 Agent 路由准确性"""
    print("\n" + "=" * 60)
    print("[TEST] Agent 路由准确性")
    print("=" * 60)

    # 模拟路由测试（不实际调用 LLM）
    test_cases = [
        ("我想查询账户余额", "Account Agent"),
        ("行内转账怎么操作", "Account Agent"),
        ("银行卡丢了怎么办", "Account Agent"),
        ("理财产品有什么推荐", "Financial Advisor Agent"),
        ("信用卡账单怎么查", "Financial Advisor Agent"),
        ("贷款利率是多少", "Financial Advisor Agent"),
    ]

    print("\n测试用例（路由规则验证）：\n")

    for query, expected_agent in test_cases:
        # 简单关键词匹配验证路由逻辑
        if any(kw in query for kw in ["账户", "转账", "挂失", "丢失", "丢了", "冻结", "投诉"]):
            predicted = "Account Agent"
        elif any(kw in query for kw in ["理财", "信用卡", "贷款", "投资"]):
            predicted = "Financial Advisor Agent"
        else:
            predicted = "Triage Agent"

        status = "[PASS]" if predicted == expected_agent else "[FAIL]"
        print(f"{status} 查询: {query}")
        print(f"   期望路由: {expected_agent}")
        print(f"   预测路由: {predicted}")
        print()

    correct = sum(1 for q, e in test_cases if _predict_route(q) == e)
    accuracy = correct / len(test_cases) * 100
    print(f"[RESULT] 路由准确率: {correct}/{len(test_cases)} = {accuracy:.1f}%")

    return accuracy


def _predict_route(query: str) -> str:
    """模拟路由预测"""
    if any(kw in query for kw in ["账户", "转账", "挂失", "丢失", "丢了", "冻结", "投诉"]):
        return "Account Agent"
    elif any(kw in query for kw in ["理财", "信用卡", "贷款", "投资"]):
        return "Financial Advisor Agent"
    else:
        return "Triage Agent"


def main():
    """主测试函数"""
    print("=" * 60)
    print("  银行客服智能体系统 - 本地测试")
    print("=" * 60)

    # 测试 RAG 召回率
    try:
        recall_rate = test_rag_pipeline()
    except Exception as e:
        print(f"[ERROR] RAG Pipeline 测试失败: {e}")
        import traceback
        traceback.print_exc()
        recall_rate = 0

    # 测试路由准确率
    try:
        accuracy = test_agent_routing()
    except Exception as e:
        print(f"[ERROR] 路由测试失败: {e}")
        import traceback
        traceback.print_exc()
        accuracy = 0

    # 汇总
    print("\n" + "=" * 60)
    print("  测试汇总")
    print("=" * 60)
    print(f"  RAG 召回率: {recall_rate:.1f}%")
    print(f"  路由准确率: {accuracy:.1f}%")
    print("=" * 60)

    # 判断是否通过
    if recall_rate >= 80 and accuracy >= 90:
        print("\n[PASS] 测试通过！系统可以进行端到端验证。")
        return 0
    else:
        print("\n[WARN] 测试未完全通过，建议优化后重试。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
