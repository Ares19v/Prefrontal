# EVAL — Prefrontal

> **Evaluation Date:** 2026-05-29
> **Evaluator:** Automated Portfolio Review
> **Maturity Level:** MVP

---

## 1. Project Purpose & Problem Statement

Prefrontal is a Retrieval-Augmented Generation platform that answers a specific question: why do modern humans experience specific fears, cravings, and behavioral patterns — and what ancestral survival pressures created them? The platform traces modern anxieties (social rejection, fear of the dark, sugar cravings) back to their evolutionary origins using a curated knowledge base of evolutionary psychology literature (Sapolsky, Dawkins, Lieberman) and academic texts.

The audience is curious individuals, psychology students, and anyone interested in the "why" behind their irrational impulses. Prefrontal occupies an interesting niche: it is not a general-purpose Q&A chatbot, but a domain-specialist RAG system with a specifically curated knowledge base. This domain specificity is both its strength (precise answers) and its limitation (narrow scope).

---

## 2. Technical Architecture

Prefrontal is a standard full-stack RAG architecture with thoughtful component choices:

**Backend (FastAPI, Python 3.11+)**:
- `rag/` — `BAAI/bge-base-en-v1.5` via Sentence-Transformers for local embedding generation. Queries are embedded and searched against Pinecone's serverless vector index.
- `llm/` — LangChain orchestration pipeline: retrieved context chunks + system prompt → Groq (Llama-3.3-70b) → Server-Sent Events (SSE) streaming response.
- `api/` — FastAPI routes; POST `/api/explain` triggers the full RAG pipeline.
- `scripts/build_index.py` — ingests PDFs from `knowledge_base/books/` and JSON from `knowledge_base/curated/` into Pinecone.
- `scripts/eval_rag.py` — RAG evaluation script (existence suggests at least some performance testing was done).

**Frontend (Next.js 15, App Router)**:
- Glassmorphic clinical UI with a custom "neural firing" CSS animation during retrieval.
- Server-Sent Events client for streaming token-by-token display.
- Context metadata display (retrieval latency, number of patterns analyzed) — shows the RAG system's reasoning is transparent to users.
- Suggestion chips for common behavioral questions.

**Knowledge Base**: Academic PDFs (ingested but not committed to git — appropriately) + curated JSON seed patterns for evolutionary survival behaviors.

**Infrastructure**: Docker Compose, GitHub Actions CI, `install.bat`/`run.bat`/`test.bat` automation.

---

## 3. Model/Algorithm Details

**Embeddings**: `BAAI/bge-base-en-v1.5` — a strong general-purpose embedding model from the BAAI BGE family, consistently competitive on MTEB benchmarks. Running locally means no embedding API costs and no data exfiltration of queries. Good choice for a domain-specific knowledge base of modest size.

**Vector Store**: Pinecone serverless — appropriate for a static knowledge base where the index is built once via `build_index.py` and then only queried. Serverless eliminates cold-start management.

**LLM**: Groq Llama-3.3-70b (70B parameter) — the largest model used in this portfolio. For evolutionary psychology explanations that require nuanced reasoning across multiple academic sources, 70B parameters is a justified choice over smaller models.

**Pipeline**: LangChain for orchestration. Retrieved chunks are passed as context in a structured system prompt; the response streams via SSE. Retrieval latency is displayed in the UI, showing awareness of RAG pipeline performance as a user-visible metric.

**RAG Evaluation**: `scripts/eval_rag.py` exists, suggesting the author has thought about RAG quality beyond "does it return something."

---

## 4. Strengths

- **Domain-specific knowledge base** — using real academic texts (Sapolsky's "Why Zebras Don't Get Ulcers," Dawkins, Lieberman) as the retrieval corpus gives answers genuine academic grounding.
- **Local embeddings** — `bge-base-en-v1.5` runs locally; only the LLM call is external, preserving query privacy.
- **Streaming SSE** — token-by-token streaming with context metadata visible to users is a polished UX choice.
- **RAG evaluation script** — `eval_rag.py` suggests measurement of retrieval quality, which distinguishes this from "RAG demos" that never measure if retrieval actually helps.
- **Next.js 15 App Router** — using the latest stable Next.js with App Router (not Pages Router) demonstrates currency with the React ecosystem.
- **CI/CD pipeline** — GitHub Actions with clean badge in README.
- **Curated seed patterns** — JSON seed data for common survival behaviors provides coverage even before PDF ingestion.

---

## 5. Limitations & Known Gaps

- **External API dependencies** — requires both a Groq API key and a Pinecone API key. No offline fallback or demo mode documented.
- **Knowledge base not committed** — academic PDFs are appropriately omitted from git (copyright), but this means a fresh clone cannot run the full RAG system until `build_index.py` is executed against a populated Pinecone index. The setup friction is non-trivial.
- **LangChain abstraction overhead** — LangChain adds significant abstraction for a relatively simple RAG pipeline. Direct LangChain-free implementation would be simpler to debug and maintain.
- **Pinecone index is pre-built** — if the Pinecone index is unavailable (API key invalid, index deleted), the system fails entirely. No graceful degradation.
- **Narrow domain** — evolutionary psychology is a compelling niche, but the platform has limited extensibility to other knowledge domains without rebuilding the index.
- **No citation linking** — retrieved source chunks are referenced ("N patterns analyzed") but not linked to specific passages in source documents.

---

## 6. Code Quality Assessment

**Structure**: Clean backend module layout (`rag/`, `llm/`, `api/`). Having both `build_index.py` and `eval_rag.py` in `scripts/` is professional.

**Documentation**: README is well-structured with architecture diagram (Mermaid), feature table, tech stack table, and installation steps. `CONTRIBUTING.md` and `SECURITY.md` exist.

**Tests**: `test.bat` exists; CI badge is present. Test depth is not clear from the README.

**Docker**: Compose file for both services; Next.js and FastAPI containerized.

**Security**: Pinecone and Groq keys are environment variables; `.gitignore` is present. PDFs are not committed (copyright-appropriate).

---

## 7. Maturity Breakdown

| Dimension | Score | Notes |
|-----------|-------|-------|
| Functionality | 7/10 | Full RAG pipeline; setup friction without pre-built Pinecone index |
| Code Quality | 7/10 | Clean structure; LangChain adds abstraction overhead |
| Documentation | 8/10 | Good README + eval script presence |
| Scalability | 6/10 | Pinecone serverless scales; single Groq dependency |
| Security | 7/10 | API keys in env; no auth on the API |
| **Overall** | **7/10** | Technically sound RAG implementation in a compelling domain |

---

## 8. Suggested Next Steps

1. **Add a "no-Pinecone" demo mode** — pre-embed a small subset of curated seed patterns as a static JSON file that can be searched with cosine similarity using NumPy. This eliminates the Pinecone dependency for portfolio demos.
2. **Add source citation links** — when displaying retrieved context metadata, show which book/paper each chunk came from with page numbers. This increases trust and demonstrates that the RAG system is actually grounding answers in sources, not hallucinating.
3. **Replace LangChain with direct SDK calls** — the RAG pipeline is simple enough (embed → search Pinecone → call Groq with context) to implement directly in ~50 lines. This would reduce dependency surface area and make the code easier for evaluators to read.

---

## 9. Verdict

Prefrontal is a well-executed domain-specific RAG application that makes an interesting subject matter choice (evolutionary psychology) and backs it with appropriate technical tools (local BGE embeddings, Pinecone serverless, Groq 70B for nuanced reasoning). The RAG evaluation script and streaming SSE implementation demonstrate technical maturity beyond typical "RAG demos." The main barriers are the external dependency chain (Pinecone + Groq both required, no fallback) and the knowledge base ingestion step that adds friction to portfolio evaluation. Adding a lightweight demo mode would make this project immediately more accessible.

---
<p align="center">Made by Devansh Tyagi @ 2026</p>
