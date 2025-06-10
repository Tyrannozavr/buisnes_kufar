from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.api.authentication import models, schemas

def get_by_token(db: Session, token: str) -> Optional[models.RegistrationToken]:
    return db.query(models.RegistrationToken).filter(models.RegistrationToken.token == token).first()

def create(
    db: Session,
    *,
    obj_in: schemas.RegistrationTokenCreate
) -> models.RegistrationToken:
    db_obj = models.RegistrationToken(
        token=obj_in.token,
        email=obj_in.email,
        expires_at=obj_in.expires_at
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def mark_as_used(db: Session, *, token: str) -> Optional[models.RegistrationToken]:
    db_obj = get_by_token(db, token=token)
    if not db_obj:
        return None
    
    db_obj.is_used = True
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj 