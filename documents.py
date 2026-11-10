import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..config import UPLOAD_DIR, MAX_UPLOAD_MB
from ..database import get_db
from ..dependencies import get_current_user
from ..models import User, Document, Category, Favorite

router = APIRouter(prefix="/api/documents", tags=["Documents"])
PDF_MAGIC = b"%PDF-"

@router.post("/upload", status_code=201)
async def upload_document(title: str = Form(...), description: str = Form(""), category_id: int | None = Form(None), file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(400, "Only PDF files are allowed")
    if category_id is not None and not db.get(Category, category_id):
        raise HTTPException(404, "Category not found")
    content = await file.read(MAX_UPLOAD_MB * 1024 * 1024 + 1)
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {MAX_UPLOAD_MB} MB limit")
    if not content.startswith(PDF_MAGIC):
        raise HTTPException(400, "Uploaded file is not a valid PDF")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored = f"{uuid.uuid4().hex}.pdf"
    (UPLOAD_DIR / stored).write_bytes(content)
    doc = Document(title=title.strip(), description=description.strip(), filename=Path(file.filename).name, stored_name=stored, category_id=category_id, uploader_id=user.id)
    db.add(doc); db.commit(); db.refresh(doc)
    return {"message":"PDF uploaded and sent for approval","document_id":doc.id}

@router.get("")
def list_documents(q: str = "", category_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Document).filter(Document.is_approved == True)
    if q.strip():
        term = f"%{q.strip()}%"
        query = query.filter((Document.title.ilike(term)) | (Document.description.ilike(term)))
    if category_id is not None:
        query = query.filter(Document.category_id == category_id)
    return [{"id":d.id,"title":d.title,"description":d.description,"filename":d.filename,"category_id":d.category_id,"created_at":d.created_at} for d in query.order_by(Document.id.desc()).limit(200).all()]

@router.get("/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc or not doc.is_approved: raise HTTPException(404, "Document not found")
    path = UPLOAD_DIR / doc.stored_name
    if not path.is_file(): raise HTTPException(404, "PDF file is missing from storage")
    return FileResponse(path, media_type="application/pdf", filename=doc.filename)

@router.post("/{document_id}/favorite")
def toggle_favorite(document_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    doc = db.get(Document, document_id)
    if not doc or not doc.is_approved: raise HTTPException(404, "Document not found")
    favorite = db.query(Favorite).filter(Favorite.user_id == user.id, Favorite.document_id == document_id).first()
    if favorite:
        db.delete(favorite); db.commit()
        return {"is_favorite":False}
    db.add(Favorite(user_id=user.id, document_id=document_id)); db.commit()
    return {"is_favorite":True}

@router.get("/my/favorites")
def my_favorites(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Favorite).filter(Favorite.user_id == user.id).all()
    ids = [r.document_id for r in rows]
    docs = db.query(Document).filter(Document.id.in_(ids), Document.is_approved == True).all() if ids else []
    return [{"id":d.id,"title":d.title,"filename":d.filename} for d in docs]
