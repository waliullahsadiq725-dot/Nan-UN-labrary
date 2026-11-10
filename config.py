import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()

DATABASE_URL = env("DATABASE_URL", f"sqlite:///{(BASE_DIR / 'data' / 'nudl.db').as_posix()}")
SECRET_KEY = env("SECRET_KEY", "development-only-change-this-secret")
UPLOAD_DIR = Path(env("UPLOAD_DIR", str(BASE_DIR / "uploads")))
MAX_UPLOAD_MB = max(1, int(env("MAX_UPLOAD_MB", "25")))
TOKEN_EXPIRE_MINUTES = max(5, int(env("TOKEN_EXPIRE_MINUTES", "720")))
CORS_ORIGINS = [x.strip() for x in env("CORS_ORIGINS", "*").split(",") if x.strip()]
ADMIN_NAME = env("ADMIN_NAME", "")
ADMIN_EMAIL = env("ADMIN_EMAIL", "").lower()
ADMIN_PASSWORD = env("ADMIN_PASSWORD", "")
