"use client";

import { ChangeEvent, useRef, useState } from "react";
import { Brain, LoaderCircle, Upload } from "lucide-react";
import styles from "./UploadButton.module.css";

type UploadStatus = "idle" | "uploading" | "success" | "error";

type UploadResponse = {
  filename: string;
  status: "indexed" | "already_exists";
};

type UploadButtonProps = {
  isKnowledgeBaseEmpty: boolean;
  onUploadSuccess: () => Promise<void> | void;
};

const UPLOAD_API = "http://127.0.0.1:8000/upload";

export default function UploadButton({
  isKnowledgeBaseEmpty,
  onUploadSuccess,
}: UploadButtonProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [message, setMessage] = useState("");

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setStatus("error");
      setMessage("仅支持上传 PDF 文件。");
      event.target.value = "";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    const isFirstUpload = isKnowledgeBaseEmpty;
    setStatus("uploading");
    setMessage("正在处理论文……\nAI 正在读取内容，完成后就可以开始提问。");

    try {
      const response = await fetch(UPLOAD_API, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error("存在同名但内容不同的论文，当前版本暂不支持替换。");
        }

        throw new Error("论文上传失败，请检查文件后重试。");
      }

      const data: UploadResponse = await response.json();

      if (data.status === "already_exists") {
        setStatus("success");
        setMessage("该论文已存在于知识库中。");
        return;
      }

      if (data.status !== "indexed") {
        throw new Error("论文上传失败，请检查文件后重试。");
      }

      await onUploadSuccess();
      setStatus("success");
      setMessage(
        isFirstUpload
          ? "第一篇论文已准备完成，\n现在可以向 AI 提问了。"
          : "论文已准备完成，可以开始提问。",
      );
    } catch (uploadError) {
      setStatus("error");
      setMessage(
        uploadError instanceof Error
          ? uploadError.message
          : "论文上传失败，请检查文件后重试。",
      );
    } finally {
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    }
  }

  return (
    <div
      className={`${styles.uploadArea} ${isKnowledgeBaseEmpty ? styles.emptyUploadArea : ""}`}
    >
      <input
        ref={inputRef}
        className={styles.fileInput}
        type="file"
        accept=".pdf,application/pdf"
        onChange={handleFileChange}
        disabled={status === "uploading"}
        id="pdf-upload"
      />
      {isKnowledgeBaseEmpty && (
        <div className={styles.emptyIntroduction}>
          <span className={styles.emptyMark} aria-hidden="true">
            <Brain size={22} strokeWidth={1.7} />
          </span>
          <strong>PaperMind</strong>
          <p>你的知识库还是空的。</p>
          <small>上传第一篇论文，<br />开始你的 AI 阅读之旅。</small>
        </div>
      )}

      <label
        className={`${styles.uploadButton} ${status === "uploading" ? styles.disabled : ""}`}
        htmlFor="pdf-upload"
      >
        {status === "uploading" ? (
          <LoaderCircle className={styles.spinner} size={16} strokeWidth={1.8} aria-hidden="true" />
        ) : (
          <Upload size={16} strokeWidth={1.8} aria-hidden="true" />
        )}
        {status === "uploading" ? "正在处理…" : "上传论文"}
      </label>

      {status !== "idle" && (
        <p
          className={`${styles.feedback} ${status === "error" ? styles.error : ""}`}
          role={status === "error" ? "alert" : "status"}
        >
          {message}
        </p>
      )}
    </div>
  );
}
