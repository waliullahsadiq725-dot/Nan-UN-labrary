from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import require_admin
from ..models import User, Document, Category
from ..schemas import CategoryIn

router = APIRouter(prefix="/api/admin", tags=["Administration"])

@router.get("/users")
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return [{"id":u.id,"name":u.name,"email":u.email,"role":u.role,"is_approved":u.is_approved,"is_active":u.is_active} for u in db.query(User).order_by(User.id.desc()).all()]

@router.patch("/users/{user_id}/approve")
def approve_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.get(User, user_id)
    if not user: raise HTTPException(404, "User not found")
    user.is_approved = True; db.commit()
    return {"message":"User approved"}

@router.patch("/users/{user_id}/disable")
def disable_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.get(User, user_id)
    if not user: raise HTTPException(404, "User not found")
    if user.id == admin.id: raise HTTPException(400, "You cannot disable your own account")
    user.is_active = not user.is_active; db.commit()
    return {"message":"User status updated","is_active":user.is_active}

@router.get("/documents/pending")
def pending_documents(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    docs = db.query(Document).filter(Document.is_approved == False).order_by(Document.id.desc()).all()
    return [{"id":d.id,"title":d.title,"filename":d.filename,"uploader_id":d.uploader_id} for d in docs]

@router.patch("/documents/{document_id}/approve")
def approve_document(document_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    doc = db.get(Document, document_id)
    if not doc: raise HTTPException(404, "Document not found")
    doc.is_approved = True; db.commit()
    return {"message":"Document approved"}

@router.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    doc = db.get(Document, document_id)
    if not doc: raise HTTPException(404, "Document not found")
    db.delete(doc); db.commit()
    return {"message":"Document deleted"}

@router.post("/categories", status_code=201)
def create_category(data: CategoryIn, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    name = data.name.strip()
    if db.query(Category).filter(Category.name == name).first():
        raise HTTPException(409, "Category already exists")
    category = Category(name=name); db.add(category); db.commit(); db.refresh(category)
    return {"id":category.id,"name":category.name}

@router.get("/stats")
def stats(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return {"users":db.query(User).count(),"pending_users":db.query(User).filter(User.is_approved == False, User.role != "admin").count(),"documents":db.query(Document).count(),"pending_documents":db.query(Document).filter(Document.is_approved == False).count(),"categories":db.query(Category).count()}
