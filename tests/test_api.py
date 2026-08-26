"""API 端点测试"""

from fastapi.testclient import TestClient

from src.api.main import app


def test_health_check():
    """测试健康检查端点"""
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data


def test_chat_endpoint():
    """测试对话端点（基础请求）"""
    client = TestClient(app)
    response = client.post(
        "/api/v1/chat",
        json={"message": "你好"},
    )

    # 基础响应格式测试
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "agent" in data
    assert "reasoning_steps" in data
    assert "sources" in data


def test_chat_empty_message():
    """测试空消息验证"""
    client = TestClient(app)
    response = client.post(
        "/api/v1/chat",
        json={"message": ""},
    )

    assert response.status_code == 422  # Validation error
