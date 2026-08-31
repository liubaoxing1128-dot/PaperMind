from pathlib import Path

import fitz


def load_txt(file_path):
    """读取 TXT 文件，并返回完整文本。"""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def load_pdf(file_path):
    """读取 PDF 的所有页面，并返回合并后的纯文本。"""
    page_texts = []

    with fitz.open(file_path) as document:
        for page in document:
            page_texts.append(page.get_text())

    return "\n\n".join(page_texts)


def load_document(file_path):
    """根据文件扩展名选择对应的文档读取函数。"""
    suffix = Path(file_path).suffix.lower()

    if suffix == ".txt":
        return load_txt(file_path)
    if suffix == ".pdf":
        return load_pdf(file_path)

    raise ValueError(f"暂不支持该文件类型：{suffix}")


def load_chunks_with_pages(file_path):
    """读取文档并返回 Chunk 文本及页码。TXT 的页码为 None。"""
    file_path = Path(file_path)

    if file_path.suffix.lower() == ".pdf":
        chunks = []
        with fitz.open(file_path) as document:
            for page_number, page in enumerate(document, start=1):
                page_chunks = page.get_text().split("\n\n")
                chunks.extend(
                    {"text": text.strip(), "page": page_number}
                    for text in page_chunks
                    if text.strip()
                )
        return chunks

    text = load_document(file_path)
    return [
        {"text": chunk.strip(), "page": None}
        for chunk in text.split("\n\n")
        if chunk.strip()
    ]


def load_chunks(file_path):
    """保留原有接口，只返回 Chunk 文本列表。"""
    return [chunk["text"] for chunk in load_chunks_with_pages(file_path)]
