"""文档切片器测试"""

from llama_index.core import Document

from src.rag.chunker import chunk_document


def test_chunk_document_basic():
    """测试基础文档切片"""
    doc = Document(
        text="这是一段测试文本。\n\n这是第二段。\n\n这是第三段。",
        metadata={"file_name": "test.md"},
    )

    chunks = chunk_document(doc, chunk_size=512)

    assert len(chunks) > 0
    for chunk in chunks:
        assert len(chunk.text) > 0
        assert chunk.metadata["file_name"] == "test.md"
        assert "chunk_index" in chunk.metadata


def test_chunk_preserves_headings():
    """测试切片保留标题"""
    doc = Document(
        text="# 第一章\n\n内容一\n\n## 第一节\n\n内容二\n\n# 第二章\n\n内容三",
        metadata={"file_name": "test.md"},
    )

    chunks = chunk_document(doc, chunk_size=512)

    # 应该有多个切片
    assert len(chunks) >= 2

    # 检查切片是否包含标题信息
    has_heading = any(chunk.metadata.get("has_heading") for chunk in chunks)
    assert has_heading


def test_chunk_merge_small():
    """测试小切片合并"""
    doc = Document(
        text="短句1\n\n短句2\n\n短句3\n\n短句4",
        metadata={"file_name": "test.md"},
    )

    chunks = chunk_document(doc, chunk_size=512, chunk_overlap=50)

    # 小段落应该被合并
    assert len(chunks) <= 2
