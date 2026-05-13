"""
Builds the vector index from documents in data/raw/.

Run this once after fetch_docs.py, or any time you add/change documents.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "data" / "raw"
PERSIST_DIR = ROOT / os.getenv("CHROMA_PERSIST_DIR", "data/chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# Chunking parameters — tuned for legal text.
# 800 tokens ≈ 1 page of dense text. 100 tokens overlap preserves context
# at chunk boundaries (mid-sentence cuts hurt retrieval quality).
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("ERROR: OPENAI_API_KEY not set. Edit .env first.")

    files = list(RAW_DIR.glob("*.txt"))
    if not files:
        sys.exit(f"ERROR: No .txt files in {RAW_DIR}. Run scripts/fetch_docs.py first.")

    print(f"Loading {len(files)} documents from {RAW_DIR}/")
    loader = DirectoryLoader(
        str(RAW_DIR),
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
    )
    docs = loader.load()
    print(f"  Loaded {len(docs)} documents.")

    # Attach source name to each doc for citation
    for d in docs:
        d.metadata["source_name"] = Path(d.metadata["source"]).stem

    # Chunk using recursive splitter — respects paragraph/sentence boundaries
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],  # try larger units first
        length_function=len,
    )
    chunks = splitter.split_documents(docs)
    print(f"  Split into {len(chunks)} chunks (avg {sum(len(c.page_content) for c in chunks)//len(chunks)} chars each).")

    # Embed and store
    print(f"\nEmbedding with {EMBEDDING_MODEL} and persisting to {PERSIST_DIR}/")
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    # Delete old index if it exists, to avoid duplicates on re-index
    if PERSIST_DIR.exists():
        import shutil
        shutil.rmtree(PERSIST_DIR)
        print(f"  Cleared existing index at {PERSIST_DIR}/")

    BATCH_SIZE = 150  # must be < 166 (Chroma limit)

    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=str(PERSIST_DIR),
        collection_name="polish_law",
    )

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        vectorstore.add_documents(batch)
        print(f"  Inserted batch {i // BATCH_SIZE + 1} ({len(batch)} docs)")

    # Quick sanity check
    result = vectorstore.similarity_search("VAT", k=1)
    if result:
        print(f"\nSanity check: query 'VAT' returned a chunk from '{result[0].metadata.get('source_name')}'")
    print(f"\nDone. Index ready at {PERSIST_DIR}/")
    print(f"You can now run:  streamlit run app/streamlit_app.py")


if __name__ == "__main__":
    main()
