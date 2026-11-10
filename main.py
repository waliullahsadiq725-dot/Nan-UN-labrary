from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .config import CORS_ORIGINS, ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASSWORD, UPLOAD_DIR
from .database import Base, engine, SessionLocal
from .models import User
from .security import hash_password
from .routers import auth, admin, documents, public

def bootstrap_admin():
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        return
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if not existing:
            db.add(User(name=ADMIN_NAME or "NUDL Administrator", email=ADMIN_EMAIL, password_hash=hash_password(ADMIN_PASSWORD), role="admin", is_approved=True, is_active=True))
            db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    bootstrap_admin()
    yield

app = FastAPI(title="NUDL — Nangarhar University Digital Library API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"] if "*" in CORS_ORIGINS else CORS_ORIGINS, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(documents.router)
app.include_router(public.router)

@app.get("/")
def root():
    return {"message":"NUDL API is running","docs":"/docs","health":"/health"}

@app.get("/health")
def health():
    return {"status":"ok"}
