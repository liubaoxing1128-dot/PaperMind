import hashlib
import os
import tempfile
from pathlib import Path

from fastapi import UploadFile

DATA_DIR = Path("data")
STORE_DIR = Path("faiss_store")


class InvalidUploadError(Exception):
    """上传文件不符合要求。"""


class UploadConflictError(Exception):
    """同名文件存在，但文件内容不同。"""


class KnowledgeBaseSyncError(Exception):
    """文件已接收，但知识库同步失败。"""


def _calculate_existing_hash(file_path):
    """需要比较同名文件时才加载 Knowledge Base 模块。"""
    from rag.knowledge_base import calculate_file_hash

    return calculate_file_hash(file_path)


def _sync_knowledge_base(data_dir, store_dir):
    """新文件提交后才加载并调用增量同步逻辑。"""
    from rag.knowledge_base import update_knowledge_base

    return update_knowledge_base(data_dir=data_dir, store_dir=store_dir)


async def save_and_index_pdf(upload_file: UploadFile, data_dir=DATA_DIR, store_dir=STORE_DIR):
    """安全保存 PDF，并调用现有 Knowledge Base Manager 完成索引同步。"""
    original_name = upload_file.filename or ""
    filename = Path(original_name).name

    if not filename or filename != original_name:
        raise InvalidUploadError("文件名无效")
    if Path(filename).suffix.lower() != ".pdf":
        raise InvalidUploadError("只允许上传 .pdf 文件")

    data_dir = Path(data_dir)
    store_dir = Path(store_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    target_path = data_dir / filename
    upload_hash = hashlib.sha256()

    # 先写入 data 目录内的临时文件，完整接收后再决定是否提交。
    with tempfile.NamedTemporaryFile(
        mode="wb",
        dir=data_dir,
        prefix=".upload-",
        suffix=".tmp",
        delete=False,
    ) as temp_file:
        temp_path = Path(temp_file.name)
        while content := await upload_file.read(1024 * 1024):
            upload_hash.update(content)
            temp_file.write(content)

    try:
        if target_path.exists():
            existing_hash = _calculate_existing_hash(target_path)
            if existing_hash == upload_hash.hexdigest():
                return {"filename": filename, "status": "already_exists"}

            raise UploadConflictError(
                f"同名文件 {filename} 已存在，但内容不同；需要显式 replace"
            )

        os.replace(temp_path, target_path)

        try:
            _sync_knowledge_base(data_dir, store_dir)
        except Exception as error:
            # 同步失败时撤销本次新文件，避免 data 与 manifest 状态不一致。
            target_path.unlink(missing_ok=True)
            raise KnowledgeBaseSyncError(f"知识库同步失败：{error}") from error

        return {"filename": filename, "status": "indexed"}
    finally:
        temp_path.unlink(missing_ok=True)
