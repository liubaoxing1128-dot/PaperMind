import os
import uuid
from pathlib import Path

from document_service import DATA_DIR, resolve_document_file


STORE_DIR = Path("faiss_store")


class DocumentDeleteSyncError(Exception):
    """原始文档已暂存，但知识库删除同步失败。"""


def _sync_knowledge_base(data_dir, store_dir):
    """复用现有 Knowledge Base Manager 完成增量删除。"""
    from rag.knowledge_base import update_knowledge_base

    return update_knowledge_base(data_dir=data_dir, store_dir=store_dir)


def delete_and_sync_document(filename, data_dir=DATA_DIR, store_dir=STORE_DIR):
    """安全删除原始文档，并同步 Chunk、Embedding、FAISS 和 Manifest。"""
    data_dir = Path(data_dir).resolve()
    store_dir = Path(store_dir)
    document_path = resolve_document_file(filename, data_dir)
    temporary_path = data_dir / f".delete-{uuid.uuid4().hex}.tmp"

    # 先暂存原文件；同步失败时可以恢复，避免 data 与索引状态分离。
    os.replace(document_path, temporary_path)
    try:
        changes = _sync_knowledge_base(data_dir, store_dir)
    except Exception as error:
        try:
            os.replace(temporary_path, document_path)
        except Exception as restore_error:
            raise DocumentDeleteSyncError(
                f"知识库删除同步失败，原文件保留在：{temporary_path}"
            ) from restore_error
        raise DocumentDeleteSyncError(f"知识库删除同步失败：{error}") from error

    temporary_path.unlink(missing_ok=True)
    return {"filename": filename, "status": "deleted", "changes": changes}
