"use client";

import { useCallback, useEffect, useState } from "react";
import { BookOpen, Bot, Brain, Library, Search } from "lucide-react";
import ChatPanel from "@/components/ChatPanel";
import DocumentList, { type Document } from "@/components/DocumentList";
import PDFViewer from "@/components/PDFViewer";
import UploadButton from "@/components/UploadButton";
import WelcomeDialog from "@/components/WelcomeDialog";
import styles from "./page.module.css";

type DocumentsResponse = {
  documents: Document[];
};

const DOCUMENTS_API = "http://127.0.0.1:8000/documents";

async function fetchDocuments() {
  const response = await fetch(DOCUMENTS_API, { cache: "no-store" });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  const data: DocumentsResponse = await response.json();
  return data.documents;
}

export default function Home() {
  const [selectedPdf, setSelectedPdf] = useState<string | null>(null);
  const [selectedPage, setSelectedPage] = useState<number | null>(null);
  const [citationJumpId, setCitationJumpId] = useState(0);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [documentsLoading, setDocumentsLoading] = useState(true);
  const [documentsError, setDocumentsError] = useState(false);

  const loadDocuments = useCallback(async () => {
    setDocumentsLoading(true);
    setDocumentsError(false);

    try {
      setDocuments(await fetchDocuments());
    } catch {
      setDocumentsError(true);
    } finally {
      setDocumentsLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    fetchDocuments()
      .then((loadedDocuments) => {
        if (!cancelled) {
          setDocuments(loadedDocuments);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setDocumentsError(true);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setDocumentsLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  function handleDocumentSelect(filename: string) {
    setSelectedPdf(filename);
    setSelectedPage(null);
  }

  function handleCitationClick(file: string, page: number | null) {
    setSelectedPdf(file);
    setSelectedPage(page);
    setCitationJumpId((current) => current + 1);
  }

  async function handleDocumentDeleted(filename: string) {
    const remainingDocuments = documents.filter((document) => document.filename !== filename);
    setDocuments(remainingDocuments);

    if (selectedPdf === filename) {
      const pdfDocuments = documents.filter((document) =>
        document.filename.toLowerCase().endsWith(".pdf"),
      );
      const deletedIndex = pdfDocuments.findIndex((document) => document.filename === filename);
      const remainingPdfs = pdfDocuments.filter((document) => document.filename !== filename);
      const nextDocument =
        remainingPdfs[deletedIndex] ?? remainingPdfs[deletedIndex - 1] ?? null;

      setSelectedPdf(nextDocument?.filename ?? null);
      setSelectedPage(null);
    }

    await loadDocuments();
  }

  const knowledgeBaseIsEmpty =
    !documentsLoading && !documentsError && documents.length === 0;

  return (
    <main className={styles.workspace}>
      <header className={styles.appHeader}>
        <div className={styles.brand}>
          <span className={styles.brandMark} aria-hidden="true">
            <Brain size={20} strokeWidth={1.8} />
          </span>
          <div>
            <h1>PaperMind</h1>
            <p>AI论文阅读工作台</p>
          </div>
        </div>
      </header>

      <div className={styles.columns}>
        <aside className={`${styles.panel} ${styles.knowledgePanel}`}>
          <header className={styles.panelHeader}>
            <div className={styles.panelHeading}>
              <Library size={18} strokeWidth={1.75} aria-hidden="true" />
              <div>
                <p className={styles.eyebrow}>资料库</p>
                <h2>知识库</h2>
              </div>
            </div>
            <span className={styles.documentCount}>{documents.length}</span>
          </header>
          <div className={styles.panelContent}>
            {!knowledgeBaseIsEmpty && (
              <label className={styles.searchBox}>
                <Search size={16} strokeWidth={1.75} aria-hidden="true" />
                <input type="search" placeholder="搜索论文" aria-label="搜索论文" />
              </label>
            )}
            <UploadButton
              isKnowledgeBaseEmpty={knowledgeBaseIsEmpty}
              onUploadSuccess={loadDocuments}
            />
            {!knowledgeBaseIsEmpty && (
              <div className={styles.documentsArea}>
                <DocumentList
                  documents={documents}
                  loading={documentsLoading}
                  error={documentsError}
                  selectedPdf={selectedPdf}
                  onSelectDocument={handleDocumentSelect}
                  onDocumentDeleted={handleDocumentDeleted}
                />
              </div>
            )}
          </div>
        </aside>

        <section className={`${styles.panel} ${styles.viewerPanel}`}>
          <header className={`${styles.panelHeader} ${styles.readerHeader}`}>
            <div className={`${styles.panelHeading} ${styles.readerTitle}`}>
              <BookOpen size={18} strokeWidth={1.75} aria-hidden="true" />
              <div className={styles.readerTitleText}>
                <p className={styles.eyebrow}>论文阅读</p>
                <h2 title={selectedPdf ?? undefined}>
                  {selectedPdf ?? "暂无正在阅读的论文"}
                </h2>
              </div>
            </div>
            {selectedPage !== null && (
              <span className={styles.pageBadge}>第 {selectedPage} 页</span>
            )}
          </header>
          <PDFViewer
            selectedPdf={selectedPdf}
            selectedPage={selectedPage}
            jumpId={citationJumpId}
          />
        </section>

        <aside className={`${styles.panel} ${styles.chatPanel}`}>
          <header className={styles.panelHeader}>
            <div className={styles.panelHeading}>
              <Bot size={18} strokeWidth={1.75} aria-hidden="true" />
              <div>
                <p className={styles.eyebrow}>智能研究</p>
                <h2>AI论文助手</h2>
              </div>
            </div>
            <span className={styles.aiBadge} aria-label="AI 已就绪">
              <Bot size={13} strokeWidth={1.8} aria-hidden="true" />
            </span>
          </header>
          <ChatPanel onCitationClick={handleCitationClick} />
        </aside>
      </div>
      <WelcomeDialog />
    </main>
  );
}
