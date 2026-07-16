from app.core.config import BACKEND_DIR, get_settings


settings = get_settings()

DATABASE_PATH = settings.resolve_path(settings.database_path)
UPLOAD_DIR = settings.resolve_path(settings.upload_dir)
CHROMA_DIR = settings.resolve_path(settings.chroma_dir)
MODEL_CACHE_DIR = settings.resolve_path(settings.model_cache_dir)
