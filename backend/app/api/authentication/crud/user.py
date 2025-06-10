from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session

from app.api.authentication import models, schemas
from app.api.authentication.core.security import get_password_hash, verify_password

def get_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def create_step1(db: Session, *, obj_in: schemas.UserCreateStep1) -> models.User:
    db_obj = models.User(
        email=obj_in.email,
        first_name=obj_in.first_name,
        last_name=obj_in.last_name,
        patronymic=obj_in.patronymic,
        phone=obj_in.phone,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_step2(
    db: Session,
    *,
    db_obj: models.User,
    obj_in: Union[schemas.UserCreateStep2, Dict[str, Any]]
) -> models.User:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def authenticate(db: Session, *, email: str, password: str) -> Optional[models.User]:
    user = get_by_email(db, email=email)
    if not user:
        return None
    if not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user 