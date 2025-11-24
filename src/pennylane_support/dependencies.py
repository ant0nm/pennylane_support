from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from .database import get_session
from .models import User


def get_current_user(username: str, session: Session = Depends(get_session)) -> User:
    user = session.exec(select(User).where(User.name == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def require_admin(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
