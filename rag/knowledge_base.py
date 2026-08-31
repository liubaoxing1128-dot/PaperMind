import hashlib
import json
import os
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL
from rag.answer_cache import clear_cache
from rag.loader import load_chunks_with_pages


DATA_DIR = Path("data")
STORE_DIR = Path("faiss_store")
SUPPORTED_SUFFIXES = {".txt", ".pdf"}


def calculate_file_hash(file_path):
    """分块计算文件的 SHA-256。"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as file:
        for block in iter(lambda: file.read(8192), b""):
            sha256.update(block)
    return sha256.hexdigest()


def scan_documents(data_dir=DATA_DIR):
    """扫描 data 目录，返回相对路径与文件 Hash。"""
    data_dir = Path(data_dir)
    if not data_dir.exists():
        return {}

    files = {}
    for file_path in sorted(data_dir.rglob("*")):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_SUFFIXES:
            source = file_path.relative_to(data_dir).as_posix()
            files[source] = {"sha256": calculate_file_hash(file_path)}
    return files


def load_manifest(manifest_path):
    """读取上一次成功更新后的文件状态。"""
    if not manifest_path.exists():
        return {}
    with open(manifest_path, "r", encoding="utf-8") as file:
        return json.load(file).get("files", {})


def compare_documents(current_files, previous_files):
    """比较两次扫描结果，得到四类文件状态。"""
    current_paths = set(current_files)
    previous_paths = set(previous_files)
    common_paths = current_paths & previous_paths

    return {
        "added": sorted(current_paths - previous_paths),
        "modified": sorted(
            path for path in common_paths
            if current_files[path]["sha256"] != previous_files[path]["sha256"]
        ),
        "unchanged": sorted(
            path for path in common_paths
            if current_files[path]["sha256"] == previous_files[path]["sha256"]
        ),
        "deleted": sorted(previous_paths - current_paths),
    }


def load_existing_store(store_dir):
    """加载 Chunk Metadata 和 NumPy Embedding；旧格式视为不可复用。"""
    chunks_path = store_dir / "chunks.json"
    embeddings_path = store_dir / "embeddings.npy"

    if not chunks_path.exists() or not embeddings_path.exists():
        return [], None

    with open(chunks_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    embeddings = np.load(embeddings_path, allow_pickle=False)

    chunks = data.get("chunks", [])
    required_fields = {"id", "text", "source", "page", "file_hash"}
    if data.get("embedding_model") != EMBEDDING_MODEL:
        return [], None
    if len(chunks) != len(embeddings):
        return [], None
    if any(not required_fields.issubset(chunk) for chunk in chunks):
        return [], None

    return chunks, np.asarray(embeddings, dtype="float32")


def create_chunk_metadata(source, file_hash, parsed_chunks):
    """为新解析的 Chunk 创建稳定 ID 和完整 Metadata。"""
    metadata = []
    for position, chunk in enumerate(parsed_chunks):
        identity = f"{source}|{file_hash}|{chunk['page']}|{position}|{chunk['text']}"
        chunk_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        metadata.append({
            "id": chunk_id,
            "text": chunk["text"],
            "source": source,
            "page": chunk["page"],
            "file_hash": file_hash,
        })
    return metadata


def encode_chunks(model, chunks):
    """生成适合余弦检索的归一化 float32 Embedding。"""
    if not chunks:
        return np.empty((0, model.get_embedding_dimension()), dtype="float32")

    embeddings = model.encode(
        [chunk["text"] for chunk in chunks],
        convert_to_numpy=True,
    )
    embeddings = np.asarray(embeddings, dtype="float32")
    faiss.normalize_L2(embeddings)
    return embeddings


def save_store(chunks, embeddings, current_files, store_dir):
    """先写临时文件；索引数据成功替换后，最后提交 manifest。"""
    store_dir.mkdir(parents=True, exist_ok=True)
    index_path = store_dir / "index.faiss"
    chunks_path = store_dir / "chunks.json"
    embeddings_path = store_dir / "embeddings.npy"
    manifest_path = store_dir / "manifest.json"

    index = faiss.IndexFlatIP(embeddings.shape[1])
    if len(embeddings):
        index.add(embeddings)

    temp_index = store_dir / "index.faiss.tmp"
    temp_chunks = store_dir / "chunks.json.tmp"
    temp_embeddings = store_dir / "embeddings.npy.tmp"
    temp_manifest = store_dir / "manifest.json.tmp"

    faiss.write_index(index, str(temp_index))
    with open(temp_chunks, "w", encoding="utf-8") as file:
        json.dump(
            {"embedding_model": EMBEDDING_MODEL, "chunks": chunks},
            file,
            ensure_ascii=False,
            indent=2,
        )
    with open(temp_embeddings, "wb") as file:
        np.save(file, embeddings, allow_pickle=False)
    with open(temp_manifest, "w", encoding="utf-8") as file:
        json.dump({"files": current_files}, file, ensure_ascii=False, indent=4)

    # manifest 最后替换，代表本轮更新完整成功。
    os.replace(temp_index, index_path)
    os.replace(temp_chunks, chunks_path)
    os.replace(temp_embeddings, embeddings_path)
    os.replace(temp_manifest, manifest_path)


def update_knowledge_base(data_dir=DATA_DIR, store_dir=STORE_DIR):
    """增量复用未变化数据，只为新增或修改文件生成 Embedding。"""
    data_dir = Path(data_dir)
    store_dir = Path(store_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    current_files = scan_documents(data_dir)
    previous_files = load_manifest(store_dir / "manifest.json")
    changes = compare_documents(current_files, previous_files)
    old_chunks, old_embeddings = load_existing_store(store_dir)

    # 首次升级旧存储时无法建立 source 映射，需要安全地初始化当前全部文件。
    reusable_store = old_embeddings is not None
    if not reusable_store:
        changes = {
            "added": sorted(current_files),
            "modified": [],
            "unchanged": [],
            "deleted": sorted(set(previous_files) - set(current_files)),
        }

    changed_sources = set(changes["added"] + changes["modified"])
    removed_sources = changed_sources | set(changes["deleted"])

    kept_chunks = []
    kept_vectors = []
    if reusable_store:
        for chunk, embedding in zip(old_chunks, old_embeddings):
            if chunk["source"] not in removed_sources:
                kept_chunks.append(chunk)
                kept_vectors.append(embedding)

    model = SentenceTransformer(EMBEDDING_MODEL)
    new_chunks = []
    for source in sorted(changed_sources):
        parsed_chunks = load_chunks_with_pages(data_dir / source)
        file_hash = current_files[source]["sha256"]
        new_chunks.extend(create_chunk_metadata(source, file_hash, parsed_chunks))

    new_embeddings = encode_chunks(model, new_chunks)
    dimension = model.get_embedding_dimension()
    kept_embeddings = (
        np.asarray(kept_vectors, dtype="float32")
        if kept_vectors
        else np.empty((0, dimension), dtype="float32")
    )

    all_chunks = kept_chunks + new_chunks
    all_embeddings = np.vstack([kept_embeddings, new_embeddings])
    save_store(all_chunks, all_embeddings, current_files, store_dir)

    # Answer Cache 依赖知识库；真实文件变化完成提交后必须立即失效。
    if any(changes[status] for status in ("added", "modified", "deleted")):
        clear_cache()

    return changes


def print_changes(changes):
    """打印本轮增量更新的文件分类。"""
    for status in ("added", "modified", "unchanged", "deleted"):
        print(f"{status}:")
        if changes[status]:
            for source in changes[status]:
                print(f"  - {source}")
        else:
            print("  （无）")


def main():
    changes = update_knowledge_base()
    print_changes(changes)


if __name__ == "__main__":
    main()
