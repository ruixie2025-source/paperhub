from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BACKEND_DIR / "paperhub.db"
UPLOAD_DIR = BACKEND_DIR / "uploads"
CHROMA_DIR = BACKEND_DIR / "chroma"
