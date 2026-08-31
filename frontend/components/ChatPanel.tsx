"use client";

import { FormEvent, KeyboardEvent, UIEvent, useEffect, useRef, useState } from "react";
import { Bot, ChevronDown, ChevronUp, FileText, Send } from "lucide-react";
import { chat } from "@/lib/api";
import MarkdownRenderer from "./MarkdownRenderer";
import styles from "./ChatPanel.module.css";

type Source = {
  file: string;
  page: number | null;
};

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  sourcesExpanded?: boolean;
};

type ChatPanelProps = {
  onCitationClick: (file: string, page: number | null) => void;
};

const AUTO_FOLLOW_THRESHOLD = 96;

function createMessageId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export default function ChatPanel({ onCitationClick }: ChatPanelProps) {
  const messagesAreaRef = useRef<HTMLDivElement>(null);
  const shouldAutoFollowRef = useRef(true);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const messagesArea = messagesAreaRef.current;
    if (!messagesArea || !shouldAutoFollowRef.current) {
      return;
    }

    const animationFrame = requestAnimationFrame(() => {
      if (shouldAutoFollowRef.current) {
        messagesArea.scrollTo({ top: messagesArea.scrollHeight, behavior: "smooth" });
      }
    });

    return () => cancelAnimationFrame(animationFrame);
  }, [messages, loading, error]);

  async function sendMessage() {
    const question = input.trim();

    if (!question || loading) {
      return;
    }

    setMessages((current) => [
      ...current,
      { id: createMessageId(), role: "user", content: question },
    ]);
    setInput("");
    setError(null);
    setLoading(true);

    try {
      const data = await chat(question);
      setMessages((current) => [
        ...current,
        {
          id: createMessageId(),
          role: "assistant",
          content: data.answer,
          sources: data.sources ?? [],
          sourcesExpanded: false,
        },
      ]);
    } catch {
      setError("聊天请求失败：\n暂时无法获取回答，请稍后重试。");
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void sendMessage();
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void sendMessage();
    }
  }

  function handleMessagesScroll(event: UIEvent<HTMLDivElement>) {
    const messagesArea = event.currentTarget;
    const distanceFromBottom =
      messagesArea.scrollHeight - messagesArea.scrollTop - messagesArea.clientHeight;
    shouldAutoFollowRef.current = distanceFromBottom <= AUTO_FOLLOW_THRESHOLD;
  }

  function toggleSources(messageId: string) {
    setMessages((current) =>
      current.map((message) =>
        message.id === messageId
          ? { ...message, sourcesExpanded: !message.sourcesExpanded }
          : message,
      ),
    );
  }

  return (
    <div className={styles.chatPanel}>
      <div
        ref={messagesAreaRef}
        className={styles.messages}
        onScroll={handleMessagesScroll}
        aria-live="polite"
      >
        {messages.length === 0 && (
          <div className={styles.emptyState}>
            <span className={styles.emptyMark} aria-hidden="true">
              <Bot size={20} strokeWidth={1.75} />
            </span>
            <p>向 AI 提问，开始阅读这篇论文。</p>
            <small>我会根据知识库回答，并标注可追溯的来源。</small>
          </div>
        )}

        {messages.map((message) => (
          <article
            className={`${styles.messageRow} ${styles[message.role]}`}
            key={message.id}
          >
            <div className={styles.messageBubble}>
              {message.role === "assistant" ? (
                <MarkdownRenderer content={message.content} />
              ) : (
                <p>{message.content}</p>
              )}

              {message.role === "assistant" && message.sources && message.sources.length > 0 && (
                <div className={styles.citations}>
                  <button
                    className={styles.citationToggle}
                    type="button"
                    onClick={() => toggleSources(message.id)}
                    aria-expanded={message.sourcesExpanded}
                  >
                    {message.sourcesExpanded ? (
                      <ChevronUp size={13} strokeWidth={1.8} aria-hidden="true" />
                    ) : (
                      <ChevronDown size={13} strokeWidth={1.8} aria-hidden="true" />
                    )}
                    {message.sourcesExpanded ? "收起来源" : `查看 ${message.sources.length} 个来源`}
                  </button>

                  {message.sourcesExpanded && (
                    <ul className={styles.sourceList}>
                      {message.sources.map((source, index) => (
                        <li key={`${source.file}-${source.page}-${index}`}>
                          <button
                            className={styles.sourceButton}
                            type="button"
                            onClick={() => onCitationClick(source.file, source.page)}
                          >
                            <FileText size={14} strokeWidth={1.7} aria-hidden="true" />
                            {source.file}
                            {source.page !== null ? ` · 第 ${source.page} 页` : ""}
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          </article>
        ))}

        {loading && (
          <div className={`${styles.messageRow} ${styles.assistant}`}>
            <div className={`${styles.messageBubble} ${styles.loadingMessage}`}>
              <span />
              <span />
              <span />
              <span className={styles.loadingText}>AI 正在阅读并整理回答……</span>
            </div>
          </div>
        )}

        {error && <p className={styles.error} role="alert">{error}</p>}
      </div>

      <form className={styles.composer} onSubmit={handleSubmit}>
        <textarea
          aria-label="向 AI 论文助手提问"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="向论文提问……"
          rows={2}
          disabled={loading}
        />
        <button type="submit" disabled={loading || input.trim().length === 0}>
          <Send size={14} strokeWidth={1.8} aria-hidden="true" />
          {loading ? "生成中" : "发送"}
        </button>
        <small>Enter 发送 · Shift + Enter 换行</small>
      </form>
    </div>
  );
}
