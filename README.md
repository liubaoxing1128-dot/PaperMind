 🧠
PaperMind

AI-Powered Paper Reading Workspace

An AI paper reading workspace powered by Retrieval-Augmented Generation (RAG).

支持 PDF 阅读、知识库管理、AI 问答、Citation 来源跳转与本地知识检索。

## 📷 Product Screenshot

![PaperMind Product](image-2.png)

## 📄 Built-in Demo Paper

![PaperMind Demo](image-3.png)

<img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white"> <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white"> <img src="https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black"> <img src="https://img.shields.io/badge/Next.js-000000?logo=nextdotjs&logoColor=white"> <img src="https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white"> <img src="https://img.shields.io/badge/FAISS-Vector_Search-orange"> <img src="https://img.shields.io/badge/License-MIT-green">

────────────────────

让每一篇论文，
都能像与 AI 对话一样简单。

────────────────────

## ✨ Features

- 📄 PDF Reading
    支持 PDF 在线阅读与自动页码定位
- 🤖 AI Chat
    基于 RAG 的智能问答
- 📍 Citation Navigation
    点击来源自动跳转 PDF 页面
- 📚 本地知识库
- ⚡ Manifest 增量同步
- 🧠 RAG 检索增强生成
- 🔍 文档搜索
- 🗂 文件夹管理

> 🚀 Upload a PDF. Ask anything. Get cited answers instantly.

## 🚀 Installation

```bash
git clone https://github.com/liubaoxing1128-dot/PaperMind.git

cd PaperMind
```

Backend

```bash
pip install -r requirements.txt
```

Frontend

```bash
cd frontend

npm install

npm run dev
```

## 📖 Quick Start

1. 启动后端

```bash
python app.py
```

2. 启动前端

```bash
npm run dev
```

3. Open in browser

```text
http://localhost:3000

上传 PDF 文件开始聊天。

## 📂 Project Structure

```text
PaperMind
├── frontend/          # Next.js 前端
├── rag/               # RAG 核心模块
├── data/              # 示例 PDF
├── app.py             # FastAPI 服务入口
├── main.py            # 程序入口
├── requirements.txt
├── README.md
└── .env.example
```

## 📌 Future Work

- [ ] Multi-document retrieval
- [ ] OCR support
- [ ] Hybrid Search (BM25 + Vector)
- [ ] Online deployment
- [ ] Multi-user workspace
- [ ] AI Summary & Notes