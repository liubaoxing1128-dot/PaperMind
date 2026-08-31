import { FileText } from "lucide-react";
import styles from "./PDFViewer.module.css";

type PDFViewerProps = {
  selectedPdf: string | null;
  selectedPage: number | null;
  jumpId: number;
};

const DOCUMENTS_API = "http://127.0.0.1:8000/documents";

function encodeDocumentPath(filename: string) {
  return filename.split("/").map(encodeURIComponent).join("/");
}

export default function PDFViewer({
  selectedPdf,
  selectedPage,
  jumpId,
}: PDFViewerProps) {
  if (!selectedPdf) {
    return (
      <div className={styles.emptyState}>
        <span className={styles.placeholderMark} aria-hidden="true">
          <FileText size={25} strokeWidth={1.6} />
        </span>
        <p>暂无正在阅读的论文</p>
        <small>从左侧选择论文，<br />或上传一篇新论文开始阅读。</small>
      </div>
    );
  }

  const pageFragment = selectedPage !== null ? `#page=${selectedPage}` : "";
  const pdfUrl = `${DOCUMENTS_API}/${encodeDocumentPath(selectedPdf)}/file${pageFragment}`;

  return (
    <div className={styles.viewerShell}>
      <iframe
        key={`${selectedPdf}::${selectedPage ?? "document"}::${jumpId}`}
        className={styles.viewer}
        src={pdfUrl}
        title={`论文预览：${selectedPdf}`}
      />
    </div>
  );
}
