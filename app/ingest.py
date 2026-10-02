import sys
from pathlib import Path

import chromadb
import ollama
from pypdf import PdfReader

EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 1500      # characters, roughly 350-400 tokens
OVERLAP = 200

client = chromadb.PersistentClient(path="./db")
col = client.get_or_create_collection("notes")


def embed(text: str) -> list[float]:
    return ollama.embeddings(model=EMBED_MODEL, prompt=text)["embedding"]


def chunk(text: str):
    start = 0
    while start < len(text):
        piece = text[start:start + CHUNK_SIZE].strip()
        if piece:
            yield piece
        start += CHUNK_SIZE - OVERLAP


def read_pages(path: Path):
    """Yield (page_number, text) for each file type."""
    if path.suffix.lower() == ".pdf":
        for i, page in enumerate(PdfReader(path).pages, start=1):
            yield i, page.extract_text() or ""
    else:
        yield 1, path.read_text(encoding="utf-8", errors="ignore")


def ingest(path: Path):
    count = 0
    for page_no, text in read_pages(path):
        for n, piece in enumerate(chunk(text)):
            col.upsert(
                ids=[f"{path.name}-p{page_no}-c{n}"],
                documents=[piece],
                embeddings=[embed(piece)],
                metadatas=[{"source": path.name, "page": page_no}],
            )
            count += 1
    print(f"{path.name}: {count} chunks")


if __name__ == "__main__":
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else "data/notes")
    for f in folder.iterdir():
        if f.suffix.lower() in {".pdf", ".txt", ".md"}:
            ingest(f)
    print("Total chunks in DB:", col.count())