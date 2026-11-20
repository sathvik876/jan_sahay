# backend/app/chroma_loader.py
"""Utility to load plain‑text documents into a local ChromaDB collection.
   For the demo we store everything in a folder `backend/data/`.
   Each file becomes one document; its filename is used as the metadata `source`.
"""

import os
from pathlib import Path
from typing import List
import chromadb
from chromadb.utils import embedding_functions
from . import db, models

# Initialize a persistent Chroma collection (stored in ./chroma_db)
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Use a simple no‑op embedding function to avoid the deprecated Google Gemini client.
# This works for demo loading; retrieval will still return results (all vectors are identical).
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_or_create_collection(
    name="scheme_documents",
    embedding_function=embedding_fn,
)

def load_documents_from_folder(folder: str) -> None:
    """Read every ``.txt`` or ``.pdf`` file in *folder* and add to Chroma.
       PDFs are processed with ``pymupdf`` to extract text.
    """
    folder_path = Path(folder)
    if not folder_path.is_dir():
        print(f"[chroma_loader] Folder {folder} does not exist – skipping")
        return

    for file_path in folder_path.iterdir():
        if file_path.suffix.lower() not in {".txt", ".pdf"}:
            continue
        try:
            if file_path.suffix.lower() == ".txt":
                text = file_path.read_text(encoding="utf-8")
            else:  # PDF
                import fitz  # PyMuPDF
                doc = fitz.open(str(file_path))
                text = "\n".join(page.get_text() for page in doc)
            # Use filename (without extension) as the document id
            doc_id = file_path.stem
            collection.upsert(
                documents=[text],
                ids=[doc_id],
                metadatas=[{"source": str(file_path)}],
            )
            print(f"[chroma_loader] Loaded {file_path.name}")
        except Exception as e:
            print(f"[chroma_loader] Failed {file_path.name}: {e}")

def retrieve_relevant(query: str, k: int = 3) -> List[dict]:
    """Return *k* most similar chunks for *query*.
       Each result dict contains ``document`` (text) and ``metadata``.
    """
    results = collection.query(
        query_texts=[query],
        n_results=k,
    )
    # The query API returns lists; we flatten to a list of dicts
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    return [{"text": d, "metadata": m} for d, m in zip(docs, metas)]
