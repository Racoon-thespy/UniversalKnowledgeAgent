from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings  # ✅ FIXED: Updated import
from langchain.schema import Document
from typing import List
import os


class VectorStore:
    def __init__(self, db_path: str):
        """
        Initialize the VectorStore with a path to save/load the FAISS index.
        Uses local HuggingFace embeddings (all-MiniLM-L6-v2).
        """
        self.db_path = db_path
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = None
        self.load_or_create_store()

    def load_or_create_store(self):
        """Load existing FAISS index or create a new directory"""
        if os.path.exists(self.db_path):
            try:
                self.vectorstore = FAISS.load_local(
                    self.db_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"[VectorStore] Loaded FAISS index from {self.db_path}")
            except Exception as e:
                print(f"[VectorStore] Could not load FAISS index: {e}")
                self.vectorstore = None
        else:
            os.makedirs(self.db_path, exist_ok=True)
            print(f"[VectorStore] Created new directory at {self.db_path}")

    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store"""
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vectorstore.add_documents(documents)

        # Save updated store
        self.vectorstore.save_local(self.db_path)
        print(f"[VectorStore] Saved vector store at {self.db_path}")

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents"""
        if self.vectorstore is None:
            return []
        return self.vectorstore.similarity_search(query, k=k)

    def get_retriever(self, k: int = 4):
        """Get retriever for the vector store"""
        if self.vectorstore is None:
            return None
        return self.vectorstore.as_retriever(search_kwargs={"k": k})