from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .security import decode_token

bearer = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Login required")
    payload = decode_token(credentials.credentials)
    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Account unavailable")
    if user.role != "admin" and not user.is_approved:
        raise HTTPException(status_code=403, detail="Account is awaiting administrator approval")
    return user

def require_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user
