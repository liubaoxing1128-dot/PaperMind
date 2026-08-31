"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { BookOpen, Brain, MessageCircle, Upload } from "lucide-react";
import styles from "./WelcomeDialog.module.css";

const FTUE_STORAGE_KEY = "papermind:welcome-completed";

const steps = [
  { icon: Upload, text: "上传第一篇论文" },
  { icon: BookOpen, text: "阅读论文" },
  { icon: MessageCircle, text: "向 AI 提问" },
];

export default function WelcomeDialog() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      try {
        setVisible(window.localStorage.getItem(FTUE_STORAGE_KEY) !== "true");
      } catch {
        setVisible(true);
      }
    }, 0);

    return () => window.clearTimeout(timer);
  }, []);

  function completeWelcome() {
    try {
      window.localStorage.setItem(FTUE_STORAGE_KEY, "true");
    } finally {
      setVisible(false);
    }
  }

  if (!visible || typeof document === "undefined") {
    return null;
  }

  return createPortal(
    <div className={styles.backdrop} role="presentation">
      <section
        className={styles.dialog}
        role="dialog"
        aria-modal="true"
        aria-labelledby="welcome-title"
      >
        <span className={styles.brandMark} aria-hidden="true">
          <Brain size={24} strokeWidth={1.7} />
        </span>
        <p className={styles.eyebrow}>AI 论文阅读工作台</p>
        <h2 id="welcome-title">欢迎使用 PaperMind</h2>
        <p className={styles.description}>只需三步即可开始：</p>

        <ol className={styles.steps}>
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <li key={step.text}>
                <span className={styles.stepNumber}>{index + 1}</span>
                <Icon size={17} strokeWidth={1.75} aria-hidden="true" />
                {step.text}
              </li>
            );
          })}
        </ol>

        <button type="button" onClick={completeWelcome} autoFocus>
          开始使用
        </button>
      </section>
    </div>,
    document.body,
  );
}
