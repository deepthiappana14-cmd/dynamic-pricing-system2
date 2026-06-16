import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ActiveUser
from ..schemas import ActiveUserCreate, ActiveUserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[ActiveUserRead])
def list_users(db: Session = Depends(get_db)):
    return db.query(ActiveUser).order_by(ActiveUser.joined_at.desc()).all()


@router.post("", response_model=ActiveUserRead, status_code=201)
def join_service(payload: ActiveUserCreate, db: Session = Depends(get_db)):
    user = ActiveUser(
        session_id=str(uuid.uuid4()),
        display_name=payload.display_name.strip(),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/{session_id}/heartbeat", response_model=ActiveUserRead)
def heartbeat(session_id: str, db: Session = Depends(get_db)):
    user = db.query(ActiveUser).filter(ActiveUser.session_id == session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User session not found")
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


@router.post("/{session_id}/leave", response_model=ActiveUserRead)
def leave_service(session_id: str, db: Session = Depends(get_db)):
    user = db.query(ActiveUser).filter(ActiveUser.session_id == session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User session not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{session_id}", status_code=204)
def remove_user(session_id: str, db: Session = Depends(get_db)):
    user = db.query(ActiveUser).filter(ActiveUser.session_id == session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User session not found")
    db.delete(user)
    db.commit()
