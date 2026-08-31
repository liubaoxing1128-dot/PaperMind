import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import knowledge_base
from app import ask
from document_service import (
    DocumentNotFoundError,
    InvalidDocumentPathError,
    UnsupportedDocumentTypeError,
    list_documents,
    resolve_pdf_file,
)
from delete_service import DocumentDeleteSyncError, delete_and_sync_document
from upload_service import (
    InvalidUploadError,
    KnowledgeBaseSyncError,
    UploadConflictError,
    save_and_index_pdf,
)


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时同步知识库；失败只记录日志，不阻止服务启动。"""
    try:
        changes = knowledge_base.sync()
        logger.info("Knowledge Base 启动同步完成：%s", changes)
    except Exception:
        logger.exception("Knowledge Base 启动同步失败，FastAPI 将继续启动")

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","https://paper-mind-smoky.vercel.app",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


class Citation(BaseModel):
    file: str
    page: int | None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Citation]


class Document(BaseModel):
    filename: str


class DocumentsResponse(BaseModel):
    documents: list[Document]


@app.get("/")
def get_project_info():
    return {"project": "AI Research Workspace", "version": "v1"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/documents", response_model=DocumentsResponse)
def get_documents():
    """返回 data 目录中的知识库文档。"""
    return {"documents": list_documents()}


@app.delete("/documents/{filename:path}")
def delete_document(filename: str):
    """删除原始文档，并复用 Knowledge Base Manager 同步持久化索引。"""
    try:
        result = delete_and_sync_document(filename)
        return {"filename": result["filename"], "status": result["status"]}
    except (InvalidDocumentPathError, UnsupportedDocumentTypeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except DocumentDeleteSyncError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.get("/documents/{filename:path}/file")
def get_document_file(filename: str):
    """安全返回 data 目录中的原始 PDF。"""
    try:
        pdf_path = resolve_pdf_file(filename)
    except (InvalidDocumentPathError, UnsupportedDocumentTypeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
        content_disposition_type="inline",
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return ask(request.question)


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        return await save_and_index_pdf(file)
    except InvalidUploadError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except UploadConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except KnowledgeBaseSyncError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
