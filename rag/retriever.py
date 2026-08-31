import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL


DEFAULT_INDEX_DIR = "faiss_store"
REQUIRED_METADATA_FIELDS = {"text", "source", "page", "id", "file_hash"}


def retrieve_top_chunks(question, top_k=3, index_dir=DEFAULT_INDEX_DIR):
    """从持久化 FAISS 索引查询，并返回 TopK Chunk Metadata。"""
    index_dir = Path(index_dir)
    index_path = index_dir / "index.faiss"
    chunks_path = index_dir / "chunks.json"

    if not index_path.exists() or not chunks_path.exists():
        raise FileNotFoundError("请先运行 knowledge_base.py 构建知识库索引")

    with open(chunks_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    chunks = data.get("chunks", [])

    if not chunks:
        return []
    if data.get("embedding_model") != EMBEDDING_MODEL:
        raise ValueError("当前索引使用的 Embedding 模型与配置不一致")
    if any(not REQUIRED_METADATA_FIELDS.issubset(chunk) for chunk in chunks):
        raise ValueError("chunks.json 中的 Chunk Metadata 不完整")

    index = faiss.read_index(str(index_path))
    if index.ntotal != len(chunks):
        raise ValueError("FAISS 索引与 Chunk Metadata 数量不一致")

    # FAISS 查询逻辑保持不变：问题向量归一化后使用 IndexFlatIP 搜索。
    model = SentenceTransformer(EMBEDDING_MODEL)
    question_embedding = model.encode([question], convert_to_numpy=True)
    question_embedding = np.asarray(question_embedding, dtype="float32")
    faiss.normalize_L2(question_embedding)

    result_count = min(top_k, len(chunks))
    _, positions = index.search(question_embedding, result_count)
    return [dict(chunks[position]) for position in positions[0]]
