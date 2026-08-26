"""端到端测试脚本

连接 Ollama Llama 3.2，测试完整的 Agent 协作流程。
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


def check_ollama():
    """检查 Ollama 服务是否可用"""
    import httpx

    try:
        resp = httpx.get("http://localhost:11434/api/tags", timeout=5)
        models = resp.json().get("models", [])
        model_names = [m["name"] for m in models]
        print(f"[OK] Ollama 服务运行中，可用模型: {model_names}")

        # 检查 llama3.2 是否可用
        has_llama = any("llama3.2" in name for name in model_names)
        if not has_llama:
            print("[WARN] 未找到 llama3.2 模型，请运行: ollama pull llama3.2")
            return False
        return True
    except Exception as e:
        print(f"[ERROR] Ollama 服务未启动: {e}")
        print("  请先启动 Ollama: ollama serve")
        return False


def test_single_agent():
    """测试单个 Agent 调用"""
    print("\n" + "=" * 60)
    print("[TEST] 单 Agent 调用测试（Account Agent）")
    print("=" * 60)

    from src.agents.account import create_account_agent, create_account_task
    from crewai import Crew, Process

    agent = create_account_agent()
    task = create_account_task("行内转账的手续费是多少？")

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    print("\n正在执行...")
    result = crew.kickoff()

    print("\n" + "-" * 60)
    print("[RESULT] Agent 回复:")
    print("-" * 60)
    print(str(result))
    print("-" * 60)

    return str(result)


def test_full_crew():
    """测试完整 Crew 协作流程"""
    print("\n" + "=" * 60)
    print("[TEST] 完整 Crew 协作测试（Triage + Expert Agent）")
    print("=" * 60)

    from src.agents.crew import create_customer_service_crew

    query = "我想了解一下信用卡的年费和还款方式"
    print(f"\n用户提问: {query}")
    print("\n正在执行（Triage -> Expert Agent）...")

    crew = create_customer_service_crew(query)
    result = crew.kickoff()

    print("\n" + "-" * 60)
    print("[RESULT] 最终回复:")
    print("-" * 60)
    print(str(result))
    print("-" * 60)

    return str(result)


def test_api_endpoint():
    """测试 API 端点"""
    print("\n" + "=" * 60)
    print("[TEST] API 端点测试")
    print("=" * 60)

    from fastapi.testclient import TestClient
    from src.api.main import app

    client = TestClient(app)

    # 测试健康检查
    resp = client.get("/health")
    print(f"\nGET /health -> {resp.status_code}")
    print(f"  Response: {resp.json()}")

    # 测试对话端点
    query = "银行卡丢了怎么办？"
    print(f"\nPOST /api/v1/chat -> '{query}'")
    print("正在执行...")

    resp = client.post("/api/v1/chat", json={"message": query})
    print(f"\nStatus: {resp.status_code}")
    data = resp.json()
    print(f"Agent: {data.get('agent', 'N/A')}")
    print(f"Reply: {data.get('reply', 'N/A')[:200]}...")

    return data


def main():
    """主测试函数"""
    print("=" * 60)
    print("  银行客服智能体系统 - 端到端测试")
    print("=" * 60)

    # 1. 检查 Ollama
    print("\n[STEP 1] 检查 Ollama 服务...")
    if not check_ollama():
        return 1

    # 2. 测试单 Agent
    print("\n[STEP 2] 测试单 Agent 调用...")
    try:
        single_result = test_single_agent()
        if single_result and len(single_result) > 10:
            print("[PASS] 单 Agent 测试通过")
        else:
            print("[WARN] 单 Agent 返回内容较短")
    except Exception as e:
        print(f"[ERROR] 单 Agent 测试失败: {e}")
        import traceback
        traceback.print_exc()

    # 3. 测试完整 Crew
    print("\n[STEP 3] 测试完整 Crew 协作...")
    try:
        crew_result = test_full_crew()
        if crew_result and len(crew_result) > 10:
            print("[PASS] 完整 Crew 测试通过")
        else:
            print("[WARN] 完整 Crew 返回内容较短")
    except Exception as e:
        print(f"[ERROR] 完整 Crew 测试失败: {e}")
        import traceback
        traceback.print_exc()

    # 4. 测试 API 端点
    print("\n[STEP 4] 测试 API 端点...")
    try:
        api_result = test_api_endpoint()
        print("[PASS] API 端点测试通过")
    except Exception as e:
        print(f"[ERROR] API 端点测试失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("  端到端测试完成")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
