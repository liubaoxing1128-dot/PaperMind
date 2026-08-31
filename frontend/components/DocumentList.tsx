"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Check, ExternalLink, FileText, MoreHorizontal, Trash2, X } from "lucide-react";
import { API_URL } from "@/lib/api";
import styles from "./DocumentList.module.css";

export type Document = {
  filename: string;
};

type DocumentListProps = {
  documents: Document[];
  loading: boolean;
  error: boolean;
  selectedPdf: string | null;
  onSelectDocument: (filename: string) => void;
  onDocumentDeleted: (filename: string) => Promise<void> | void;
};

function encodeDocumentPath(filename: string) {
  return filename.split("/").map(encodeURIComponent).join("/");
}

export default function DocumentList({
  documents,
  loading,
  error,
  selectedPdf,
  onSelectDocument,
  onDocumentDeleted,
}: DocumentListProps) {
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [documentToDelete, setDocumentToDelete] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    if (!toast) {
      return;
    }

    const timer = window.setTimeout(() => setToast(null), 3000);
    return () => window.clearTimeout(timer);
  }, [toast]);

  useEffect(() => {
    if (!openMenu) {
      return;
    }

    const closeMenu = () => setOpenMenu(null);
    document.addEventListener("click", closeMenu);
    return () => document.removeEventListener("click", closeMenu);
  }, [openMenu]);

  useEffect(() => {
    if (!documentToDelete) {
      return;
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !deleting) {
        setDocumentToDelete(null);
        setDeleteError(null);
      }
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [documentToDelete, deleting]);

  async function confirmDelete() {
    if (!documentToDelete || deleting) {
      return;
    }

    const filename = documentToDelete;
    setDeleting(true);
    setDeleteError(null);

    try {
      const response = await fetch(`${API_URL}/documents/${encodeDocumentPath(filename)}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("论文删除失败，请稍后重试。");
      }

      await onDocumentDeleted(filename);
      setDocumentToDelete(null);
      setToast(`已删除 ${filename}`);
    } catch (error) {
      setDeleteError(
        error instanceof Error ? error.message : "论文删除失败，请稍后重试。",
      );
    } finally {
      setDeleting(false);
    }
  }

  if (loading) {
    return <p className={styles.status}>正在加载知识库……</p>;
  }

  if (error) {
    return (
      <p className={`${styles.status} ${styles.error}`}>
        暂时无法加载知识库，请稍后重试。
      </p>
    );
  }

  if (documents.length === 0) {
    return <p className={styles.status}>请上传论文开始阅读。</p>;
  }

  return (
    <ul className={styles.list} aria-label="知识库文档">
      {documents.map((document) => {
        const extension = document.filename.split(".").pop()?.toUpperCase() ?? "FILE";
        const isPdf = extension === "PDF";
        const rowContent = (
          <>
            <span className={styles.fileIcon} aria-hidden="true">
              <FileText size={17} strokeWidth={1.75} />
            </span>
            <span className={styles.filename} title={document.filename}>
              {document.filename}
            </span>
          </>
        );

        return (
          <li
            className={`${styles.item} ${selectedPdf === document.filename ? styles.selected : ""}`}
            key={document.filename}
          >
            <div className={styles.itemContent}>
              {isPdf ? (
                <button
                  className={styles.documentButton}
                  type="button"
                  onClick={() => onSelectDocument(document.filename)}
                  aria-pressed={selectedPdf === document.filename}
                >
                  {rowContent}
                </button>
              ) : (
                <div className={styles.documentRow}>{rowContent}</div>
              )}

              <button
                className={styles.moreButton}
                type="button"
                aria-label={`管理 ${document.filename}`}
                aria-expanded={openMenu === document.filename}
                onClick={(event) => {
                  event.stopPropagation();
                  setOpenMenu((current) => current === document.filename ? null : document.filename);
                }}
              >
                <MoreHorizontal size={17} strokeWidth={1.8} aria-hidden="true" />
              </button>

              {openMenu === document.filename && (
                <div className={styles.moreMenu} role="menu" onClick={(event) => event.stopPropagation()}>
                  <button
                    type="button"
                    role="menuitem"
                    disabled={!isPdf}
                    onClick={() => {
                      onSelectDocument(document.filename);
                      setOpenMenu(null);
                    }}
                  >
                    <ExternalLink size={15} strokeWidth={1.75} aria-hidden="true" />
                    打开
                  </button>
                  <button
                    className={styles.deleteMenuItem}
                    type="button"
                    role="menuitem"
                    onClick={() => {
                      setDocumentToDelete(document.filename);
                      setDeleteError(null);
                      setOpenMenu(null);
                    }}
                  >
                    <Trash2 size={15} strokeWidth={1.75} aria-hidden="true" />
                    删除
                  </button>
                </div>
              )}
            </div>
          </li>
        );
      })}

      {typeof document !== "undefined" && documentToDelete && createPortal(
        <div className={styles.dialogBackdrop} role="presentation">
          <section className={styles.dialog} role="alertdialog" aria-modal="true" aria-labelledby="delete-dialog-title">
            <header className={styles.dialogHeader}>
              <div>
                <p className={styles.dialogEyebrow}>删除论文：</p>
                <h2 id="delete-dialog-title" title={documentToDelete}>{documentToDelete}</h2>
              </div>
              <button
                className={styles.dialogClose}
                type="button"
                aria-label="关闭删除确认"
                disabled={deleting}
                onClick={() => {
                  setDocumentToDelete(null);
                  setDeleteError(null);
                }}
              >
                <X size={18} strokeWidth={1.8} aria-hidden="true" />
              </button>
            </header>

            <p className={styles.dialogDescription}>删除后将同步删除：</p>
            <ul className={styles.deleteDetails}>
              {["原始论文", "Chunk", "Embedding", "FAISS 索引", "Manifest"].map((item) => (
                <li key={item}>
                  <Check size={15} strokeWidth={2} aria-hidden="true" />
                  {item}
                </li>
              ))}
            </ul>
            <p className={styles.irreversible}>此操作不可恢复。</p>
            {deleteError && <p className={styles.dialogError} role="alert">{deleteError}</p>}

            <footer className={styles.dialogActions}>
              <button
                className={styles.cancelButton}
                type="button"
                disabled={deleting}
                onClick={() => {
                  setDocumentToDelete(null);
                  setDeleteError(null);
                }}
              >
                取消
              </button>
              <button
                className={styles.confirmDeleteButton}
                type="button"
                disabled={deleting}
                onClick={() => void confirmDelete()}
              >
                <Trash2 size={15} strokeWidth={1.8} aria-hidden="true" />
                {deleting ? "正在删除……" : "确认删除"}
              </button>
            </footer>
          </section>
        </div>,
        document.body,
      )}

      {typeof document !== "undefined" && toast && createPortal(
        <div className={styles.toast} role="status">
          <Check size={16} strokeWidth={2} aria-hidden="true" />
          {toast}
        </div>,
        document.body,
      )}
    </ul>
  );
}
