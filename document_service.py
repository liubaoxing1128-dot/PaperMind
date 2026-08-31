from pathlib import Path


DATA_DIR = Path("data")
SUPPORTED_SUFFIXES = {".pdf", ".txt"}


class InvalidDocumentPathError(Exception):
    """请求路径试图离开 data 目录。"""


class UnsupportedDocumentTypeError(Exception):
    """请求的文件不是知识库支持的文档类型。"""


class DocumentNotFoundError(Exception):
    """请求的知识库文档不存在。"""


def list_documents(data_dir=DATA_DIR):
    """直接扫描 data 目录，返回排序后的知识库文档。"""
    data_dir = Path(data_dir)
    if not data_dir.exists():
        return []

    filenames = [
        file_path.relative_to(data_dir).as_posix()
        for file_path in data_dir.rglob("*")
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_SUFFIXES
    ]
    filenames.sort(key=str.casefold)
    return [{"filename": filename} for filename in filenames]


def resolve_document_file(filename, data_dir=DATA_DIR):
    """在 data 目录内安全解析受支持的知识库文档。"""
    data_root = Path(data_dir).resolve()
    requested_path = (data_root / filename).resolve()

    try:
        requested_path.relative_to(data_root)
    except ValueError as error:
        raise InvalidDocumentPathError("无效的文档路径") from error

    if requested_path.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise UnsupportedDocumentTypeError("当前只支持 .pdf 和 .txt 文档")
    if not requested_path.is_file():
        raise DocumentNotFoundError(f"文档不存在：{filename}")

    return requested_path


def resolve_pdf_file(filename, data_dir=DATA_DIR):
    """在 data 目录内安全解析可预览的 PDF。"""
    requested_path = resolve_document_file(filename, data_dir)
    if requested_path.suffix.lower() != ".pdf":
        raise UnsupportedDocumentTypeError("当前只允许读取 PDF 文件")
    return requested_path
