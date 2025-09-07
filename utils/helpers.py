import os
import shutil


def clear_uploads(upload_dir: str = "data/uploads") -> None:
    """Clear all uploaded files and recreate the directory."""
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    os.makedirs(upload_dir, exist_ok=True)


def clear_vector_db(db_dir: str = "data/vector_db") -> None:
    """Clear vector database and recreate the directory."""
    if os.path.exists(db_dir):
        shutil.rmtree(db_dir)
    os.makedirs(db_dir, exist_ok=True)


def get_file_size(file_path: str) -> str:
    """Return human-readable file size for a given file."""
    try:
        size = os.path.getsize(file_path)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except FileNotFoundError:
        return "File not found"
