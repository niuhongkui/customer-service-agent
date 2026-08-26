"""文档加载器测试"""

from pathlib import Path

from src.rag.loader import load_document, load_documents


def test_load_markdown():
    """测试加载 Markdown 文档"""
    md_file = Path("knowledge/账户业务指南.md")
    if not md_file.exists():
        return  # 跳过测试（文档不存在）

    doc = load_document(md_file)

    assert doc is not None
    assert len(doc.text) > 0
    assert doc.metadata["file_name"] == "账户业务指南.md"
    assert doc.metadata["file_type"] == ".md"


def test_load_all_documents():
    """测试批量加载文档"""
    knowledge_dir = Path("knowledge")
    if not knowledge_dir.exists():
        return  # 跳过测试（目录不存在）

    documents = load_documents(knowledge_dir)

    assert len(documents) > 0
    for doc in documents:
        assert len(doc.text) > 0
        assert "file_name" in doc.metadata


def test_unsupported_format():
    """测试不支持的文档格式"""
    import pytest

    # 创建一个临时的不支持格式文件
    unsupported_file = Path("test_unsupported.xyz")
    unsupported_file.write_text("test", encoding="utf-8")

    try:
        with pytest.raises(ValueError, match="不支持的文档格式"):
            load_document(unsupported_file)
    finally:
        unsupported_file.unlink()  # 清理
