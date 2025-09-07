import os
from dotenv import load_dotenv

load_dotenv()

# === API Keys ===
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")

# === Model Settings ===
LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")  
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# === Vector Store Settings ===
VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "data/vector_db")
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 200))

# === Web Search Settings ===
MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", 5))

WEB_SEARCH_KEYWORDS = [
    "latest", "current", "2024", "2023", "recent", "today",
    "explain", "how does", "what is", "vs", "compared to",
    "alternatives", "price", "cost", "stock", "trend"
]
