from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import RegisterIn, LoginIn
from ..security import hash_password, verify_password, create_token
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    role = data.role.lower().strip()
    if role not in {"student", "teacher"}:
        raise HTTPException(status_code=400, detail="Role must be student or teacher")
    email = data.email.lower().strip()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email is already registered")
    user = User(name=data.name.strip(), email=email, password_hash=hash_password(data.password), role=role)
    db.add(user); db.commit(); db.refresh(user)
    return {"message":"Registration successful. Wait for administrator approval.", "user_id":user.id}

@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower().strip()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    if user.role != "admin" and not user.is_approved:
        raise HTTPException(status_code=403, detail="Account is awaiting administrator approval")
    return {"access_token":create_token(user.id, user.role), "token_type":"bearer", "user":{"id":user.id,"name":user.name,"email":user.email,"role":user.role}}

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id":user.id,"name":user.name,"email":user.email,"role":user.role}
