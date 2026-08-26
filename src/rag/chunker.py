"""语义段落切片模块

基于段落和标题层级进行语义切片，保留上下文信息。
"""

import re

from llama_index.core import Document


def _extract_heading_level(text: str) -> int | None:
    """检测 Markdown 标题层级"""
    match = re.match(r"^(#{1,6})\s+", text)
    if match:
        return len(match.group(1))
    return None


def _split_by_paragraphs(text: str) -> list[str]:
    """按段落分割文本"""
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


def _merge_small_chunks(chunks: list[str], min_size: int) -> list[str]:
    """合并过小的切片"""
    if not chunks:
        return chunks

    merged = []
    buffer = ""

    for chunk in chunks:
        if not buffer:
            buffer = chunk
        elif len(buffer) + len(chunk) < min_size:
            buffer = buffer + "\n\n" + chunk
        else:
            merged.append(buffer)
            buffer = chunk

    if buffer:
        merged.append(buffer)

    return merged


def chunk_document(
    document: Document,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
) -> list[Document]:
    """对文档进行语义段落切片

    策略：
    1. 按段落分割文档
    2. 识别标题层级，保留章节上下文
    3. 合并过小的切片
    4. 超长段落按 chunk_size 硬切分
    """
    paragraphs = _split_by_paragraphs(document.text)
    if not paragraphs:
        return []

    # 第一轮：按段落切分，超长段落硬切
    raw_chunks = []
    current_section = ""

    for para in paragraphs:
        heading_level = _extract_heading_level(para)

        # 更新当前章节上下文
        if heading_level is not None:
            current_section = para

        # 段落超过 chunk_size 时硬切
        if len(para) > chunk_size:
            # 先保存当前缓冲
            if raw_chunks:
                raw_chunks.append(current_section)
            # 硬切分
            for i in range(0, len(para), chunk_size - chunk_overlap):
                chunk_text = para[i : i + chunk_size]
                raw_chunks.append(chunk_text)
        else:
            raw_chunks.append(para)

    # 第二轮：合并过小的切片
    merged_chunks = _merge_small_chunks(raw_chunks, min_size=chunk_size // 2)

    # 构建 Document 对象
    result = []
    for i, chunk_text in enumerate(merged_chunks):
        if not chunk_text.strip():
            continue

        metadata = {
            **document.metadata,
            "chunk_index": i,
            "total_chunks": len(merged_chunks),
        }

        # 如果切片包含标题，添加标题上下文
        if _extract_heading_level(chunk_text) is not None:
            metadata["has_heading"] = True

        result.append(Document(text=chunk_text, metadata=metadata))

    return result
