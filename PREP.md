# 🧠 Prefrontal Study Guide (From-Scratch)

Welcome to the beginner's learning guide for **Prefrontal**, a domain-specialist Retrieval-Augmented Generation (RAG) platform. In this guide, you will learn how modern search pipelines retrieve and validate academic knowledge to answer complex questions about evolutionary psychology.

---

## 🗺️ Architectural Map

Prefrontal maps user questions to evolutionary academic texts and streams back analytical answers.

```
┌────────────────────────────────────────────────────────┐
│             Next.js 15 App Router UI                   │
│  - User inputs questions about behaviors & fears        │
│  - Renders dynamic token-by-token text feeds (SSE)     │
└────────────┬──────────────────────────────▲────────────┘
             │ POST /api/explain            │ Server-Sent Events (SSE)
┌────────────▼──────────────────────────────┴────────────┐
│                  FastAPI Backend                       │
├────────────────────────────────────────────────────────┤
│ 1. main.py (FastAPI entry point orchestration)         │
│ 2. Embedder: Sentence-Transformers (Local BGE Model)   │
│    - BAAI/bge-base-en-v1.5 converts text to vectors   │
│ 3. Pinecone Vector DB (Queries serverless indexes)      │
│ 4. LangChain / Groq Pipeline (Llama-3.3-70b client)    │
└────────────────────────────────────────────────────────┘
```

---

## ⚙️ Core Technical Concepts

Let's explore the operational layers of this specialized RAG system:

### 1. What is RAG?
**Retrieval-Augmented Generation** (RAG) is a pipeline designed to improve LLM accuracy. Instead of relying purely on the LLM's pre-trained weights (which can result in hallucinations), RAG:
1.  **Retrieves** relevant passages from a custom database of books/documents.
2.  **Augments** the user's prompt by attaching these academic passages.
3.  **Generates** an answer using the LLM, forcing it to stick strictly to the attached facts.

### 2. Semantic Search and Vector Indexes
Traditional databases search for exact word matches. Prefrontal searches for **meanings**:
*   **Embeddings**: The local Python backend runs `BAAI/bge-base-en-v1.5` (a high-performance embedding model). It converts sentences into a mathematical vector (a long array of numbers representing semantic meaning).
*   **Pinecone Vector Database**: Pinecone stores these text vectors. When a user asks a question, Python embeds the question and calculates **cosine similarity** inside Pinecone to find the document chunks that are closest in meaning!

### 3. Server-Sent Events (SSE)
Standard APIs use REST requests, which wait for the entire text to generate before sending it back. Prefrontal uses **Server-Sent Events** (SSE):
*   FastAPI streams the text token-by-token as the Llama model outputs it.
*   The Next.js client renders the tokens immediately, creating a dynamic, real-time typing effect.

---

## 🛠️ Step-by-Step Local Deployment

### 1. Windows Script Launch
*   **Install**: Run `install.bat`. This configures the FastAPI Python environment and downloads dependencies.
*   **Run**: Run `run.bat` to launch both services.
*   **Test**: Run `test.bat` to run local diagnostic test sequences.
*   **Uninstall**: Run `uninstall.bat` to clean up the workspace.

### 2. Manual Dev Commands

**Backend Launch:**
```bash
cd backend
python -m venv venv
# Activate the venv
.\venv\Scripts\activate
# Install requirements
pip install -r requirements.txt
# Run FastAPI server
uvicorn main:app --host 127.0.0.1 --port 8000
```

**Frontend Launch:**
```bash
cd frontend
npm install
npm run dev
```

### 3. Required API Keys
To connect to the database and models, create a `.env` file inside the root directory (matching `.env.example` configurations):
```env
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name
```
