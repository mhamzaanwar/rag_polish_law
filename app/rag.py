"""
Core RAG logic — retrieval + generation with source citations.

This module is intentionally framework-light so it can be called from
Streamlit, FastAPI, a CLI, or a notebook.
"""
import os
import time
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

ROOT = Path(__file__).parent.parent
PERSIST_DIR = ROOT / os.getenv("CHROMA_PERSIST_DIR", "data/chroma_db")
LOG_FILE = ROOT / "data" / "queries.jsonl"
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# Cap retrieved context to keep cost predictable. ~8K tokens of context
# is plenty for legal Q&A — more usually adds noise, not signal.
TOP_K = 5
MAX_CONTEXT_CHARS = 12_000

SYSTEM_PROMPT = """You are an assistant specializing in Polish business law, tax, and B2B contracting.

Rules you MUST follow:
1. Answer ONLY based on the provided context below. If the context doesn't contain the answer, say "I don't have specific information about that in my sources" — do not guess.
2. Cite the source for every factual claim using [Source: filename] inline.
3. If the user's question is in Polish, answer in Polish. Otherwise, answer in English.
4. Be concise. Lawyers and founders are busy — give them the answer, then the nuance.
5. If something is time-sensitive (e.g., 2024 tax brackets, current VAT thresholds), say so and recommend the user verify with a current source.

Context:
{context}
"""


@dataclass
class RAGResponse:
    answer: str
    sources: list[dict]  # [{name, content_preview, score}]
    latency_ms: int
    tokens_used: Optional[int] = None


class RAGPipeline:
    """A production-ready RAG pipeline with hybrid retrieval and citation."""

    def __init__(self) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY not set in environment.")
        if not PERSIST_DIR.exists():
            raise RuntimeError(
                f"No vector index at {PERSIST_DIR}. Run scripts/build_index.py first."
            )

        self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        self.vectorstore = Chroma(
            persist_directory=str(PERSIST_DIR),
            embedding_function=self.embeddings,
            collection_name="polish_law",
        )

        # Semantic retriever (vector search)
        self.semantic = self.vectorstore.as_retriever(search_kwargs={"k": TOP_K})

        # BM25 keyword retriever, built from all docs in the store
        # (lets us catch exact-match terms that semantic search might miss,
        # e.g. specific statute numbers like "art. 113 ust. 1")
        all_docs = self._load_all_chunks()
        self.bm25 = BM25Retriever.from_documents(all_docs)
        self.bm25.k = TOP_K

        # Ensemble: 60% semantic, 40% keyword — empirically good for legal text
        self.retriever = EnsembleRetriever(
            retrievers=[self.semantic, self.bm25],
            weights=[0.6, 0.4],
        )

        self.llm = ChatOpenAI(model=LLM_MODEL, temperature=0.1)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{question}"),
        ])

    def _load_all_chunks(self) -> list[Document]:
        """Pull every chunk out of Chroma so BM25 has the same corpus."""
        data = self.vectorstore.get()
        return [
            Document(page_content=text, metadata=meta or {})
            for text, meta in zip(data["documents"], data["metadatas"])
        ]

    def _format_context(self, docs: list[Document]) -> str:
        """Format retrieved docs for the prompt, with source labels."""
        parts = []
        running = 0
        for i, d in enumerate(docs):
            source = d.metadata.get("source_name", f"doc_{i}")
            chunk = f"[Source: {source}]\n{d.page_content}\n"
            if running + len(chunk) > MAX_CONTEXT_CHARS:
                break
            parts.append(chunk)
            running += len(chunk)
        return "\n---\n".join(parts)

    def _log_query(self, response: RAGResponse, question: str) -> None:
        """Append to a JSONL log for later analysis."""
        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "ts": time.time(),
                    "question": question,
                    **asdict(response),
                }, ensure_ascii=False) + "\n")
        except Exception:
            pass  # logging must never break the user request

    def query(self, question: str) -> RAGResponse:
        """Answer a question using retrieval-augmented generation."""
        t0 = time.time()

        # 1. Retrieve relevant chunks
        docs = self.retriever.invoke(question)
        if not docs:
            return RAGResponse(
                answer="I don't have any documents indexed that relate to that question. "
                       "Try rephrasing, or ensure the indexing step ran successfully.",
                sources=[],
                latency_ms=int((time.time() - t0) * 1000),
            )

        # 2. Format context and call LLM
        context = self._format_context(docs)
        chain = self.prompt | self.llm
        result = chain.invoke({"context": context, "question": question})
        answer = result.content

        # 3. Build response with source previews
        sources = [
            {
                "name": d.metadata.get("source_name", "unknown"),
                "preview": d.page_content[:200] + ("..." if len(d.page_content) > 200 else ""),
            }
            for d in docs[:TOP_K]
        ]

        response = RAGResponse(
            answer=answer,
            sources=sources,
            latency_ms=int((time.time() - t0) * 1000),
            tokens_used=result.response_metadata.get("token_usage", {}).get("total_tokens"),
        )
        self._log_query(response, question)
        return response


# Module-level singleton for Streamlit's @cache_resource
_pipeline: Optional[RAGPipeline] = None

def get_pipeline() -> RAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline


if __name__ == "__main__":
    # CLI mode — useful for testing without spinning up Streamlit
    import sys
    if len(sys.argv) < 2:
        print("Usage: python app/rag.py 'your question here'")
        sys.exit(1)
    pipe = get_pipeline()
    resp = pipe.query(" ".join(sys.argv[1:]))
    print("\n" + resp.answer)
    print("\n--- Sources ---")
    for s in resp.sources:
        print(f"\n[{s['name']}]\n{s['preview']}")
    print(f"\n({resp.latency_ms}ms, {resp.tokens_used} tokens)")
