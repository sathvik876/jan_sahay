# backend/load_chroma.py
"""Convenient script to load all documents from `backend/data/` into the Chroma collection.
Run it after you have placed your .txt or .pdf files there.
"""

from app.chroma_loader import load_documents_from_folder
import os

if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    load_documents_from_folder(data_dir)
    print("✅ Documents loaded into ChromaDB")
