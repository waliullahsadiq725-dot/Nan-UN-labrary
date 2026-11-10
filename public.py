from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Category

router = APIRouter(prefix="/api/public", tags=["Public"])

@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    return [{"id":c.id,"name":c.name} for c in db.query(Category).order_by(Category.name).all()]
