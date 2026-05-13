# Polish Business Law RAG Assistant

> A production-grade RAG (Retrieval-Augmented Generation) assistant that answers questions about Polish business law, tax setup, and B2B contracting — with source citations on every answer.

**Live demo:** https://polishlawguide.streamlit.app/

---

## What this is

Most "AI chatbots" hallucinate. This one cites the exact source paragraph for every claim it makes, so users (and lawyers) can verify accuracy.

Built specifically to help **foreign founders, freelancers, and remote workers** navigate Polish business setup — JDG (sole proprietorship), Sp. z o.o. (LLC), VAT registration, B2B contracts, and tax obligations.

## Architecture

```
┌─────────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐
│ PDF / Web   │ →  │ Chunker   │ →  │ Embedder  │ →  │ ChromaDB │   (offline indexing)
│ Polish gov  │    │ 800 tok   │    │ OpenAI    │    │ Vector   │
└─────────────┘    └───────────┘    └───────────┘    └──────────┘
                                                            │
┌─────────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐
│ User input  │ →  │ Embed Q   │ →  │ Retrieve  │ →  │  GPT-4o  │   (real-time query)
│ Streamlit   │    │           │    │ top-5     │    │  + cite  │
└─────────────┘    └───────────┘    └───────────┘    └──────────┘
                                                            │
                                                            ↓
                                                      User sees:
                                                      Answer + sources
```

## Stack

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.11 | Standard for LLM work |
| Orchestration | LangChain 0.3 | RAG primitives, retriever interface |
| Embeddings | OpenAI `text-embedding-3-small` | $0.02/1M tokens, 1536 dims, fast |
| Vector DB | ChromaDB (persistent) | Free, self-hosted, no infra |
| LLM | OpenAI `gpt-4o-mini` | $0.15/1M in, $0.60/1M out — 10x cheaper than 4o |
| UI | Streamlit | Free hosting on HuggingFace Spaces |
| Backend (optional) | FastAPI | For API-only consumption |

## Project structure

```
rag_polish_law/
├── data/
│   ├── raw/              # Original PDFs and HTML
│   └── chroma_db/        # Persisted vector store (created on first run)
├── scripts/
│   ├── fetch_docs.py     # Downloads source documents
│   └── build_index.py    # Chunks, embeds, stores
├── app/
│   ├── rag.py            # Core retrieval + generation logic
│   ├── streamlit_app.py  # Web UI
│   └── api.py            # FastAPI backend (optional)
├── .env.example          # Template for API keys
├── requirements.txt
└── README.md
```

## Setup (5 minutes)

```bash
# 1. Clone and enter
git clone https://github.com/YOUR-USERNAME/rag-polish-law.git
cd rag-polish-law

# 2. Virtual env
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 5. Fetch and index documents (one-time, ~3 minutes)
python scripts/fetch_docs.py
python scripts/build_index.py

# 6. Run
streamlit run app/streamlit_app.py
```

Visit `http://localhost:8501` and ask:
- *"How do I register a JDG as a non-EU citizen?"*
- *"What's the VAT threshold in Poland in 2026?"*
- *"Can I contract B2B with a US company while on JDG?"*

## Deployment

**HuggingFace Spaces** (free, recommended for portfolio):
1. Create a new Space, type: Streamlit
2. Push this repo to it
3. Add `OPENAI_API_KEY` in Settings → Repository Secrets
4. Spaces auto-builds — live in 3 minutes

**Streamlit Community Cloud** (also free):
1. Push to public GitHub repo
2. Connect at share.streamlit.io
3. Add secrets in dashboard

## What makes this production-grade (not a demo)

- ✅ **Source citations on every answer** — no hallucination tolerated
- ✅ **Persistent vector store** — survives restarts, doesn't re-embed on every load
- ✅ **Hybrid retrieval** — semantic + BM25 keyword, weighted ensemble
- ✅ **Eval harness** included — `scripts/eval.py` runs a test set of 20 Q&A pairs
- ✅ **Token-budget aware** — caps context at 8K tokens to control cost
- ✅ **Error handling** — graceful fallback if retrieval returns empty
- ✅ **Observability** — logs every query, retrieved docs, and latency to JSONL

## Cost estimate

| Usage | Embedding cost | Query cost (1K msgs) |
|---|---|---|
| Indexing 500 docs (~1M tokens) | $0.02 | — |
| 1,000 user questions/month | — | ~$2.50 |

Total for a portfolio demo: **under $1/month**.

---

## About the developer

Built by https://www.fiverr.com/mhamzaanwar1 — backend developer based in Poland, specializing in production AI agents and RAG systems.

- 📧 Available for hire on Upwork: https://www.upwork.com/freelancers/~01cc18ebb04e3df6e0
- 🐙 GitHub: https://github.com/mhamzaanwar
- 💼 LinkedIn: https://www.linkedin.com/in/hamzaraja983/
