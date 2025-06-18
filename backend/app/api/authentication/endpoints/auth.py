# from datetime import datetime, timedelta
# from typing import Any
# from uuid import uuid4
#
# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from jose import JWTError, jwt
# from sqlalchemy.orm import Session
#
# from app.api.authentication import crud, schemas
# from app.api.authentication.core import security
# from app.api.authentication.core.config import settings
# from app.db.session import get_db
#
# router = APIRouter()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
# @router.post("/register/step1", response_model=schemas.RegistrationTokenResponse)
# def register_step1(
#     *,
#     db: Session = Depends(get_db),
#     user_in: schemas.UserCreateStep1,
# ) -> Any:
#     """
#     First step of registration - create user and send registration token
#     """
#     user = crud.user.get_by_email(db, email=user_in.email)
#     if user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Email already registered"
#         )
#
#     # Create user with minimal data
#     user = crud.user.create_step1(db, obj_in=user_in)
#
#     # Create registration token
#     token = str(uuid4())
#     expires_at = datetime.utcnow() + timedelta(hours=24)
#     registration_token = crud.registration_token.create(
#         db,
#         obj_in=schemas.RegistrationTokenCreate(
#             token=token,
#             email=user_in.email,
#             expires_at=expires_at
#         )
#     )
#
#     # TODO: Send email with registration token
#
#     return {"is_valid": True, "message": "Registration token sent to email"}
#
# @router.post("/verify-token/{token}", response_model=schemas.RegistrationTokenResponse)
# def verify_token(
#     token: str,
#     db: Session = Depends(get_db),
# ) -> Any:
#     """
#     Verify registration token
#     """
#     registration_token = crud.registration_token.get_by_token(db, token=token)
#     if not registration_token:
#         return {"is_valid": False, "message": "Invalid token"}
#
#     if registration_token.is_used:
#         return {"is_valid": False, "message": "Token already used"}
#
#     if registration_token.expires_at < datetime.utcnow():
#         return {"is_valid": False, "message": "Token expired"}
#
#     return {"is_valid": True}
#
# @router.post("/register/step2", response_model=schemas.Token)
# def register_step2(
#     *,
#     db: Session = Depends(get_db),
#     user_in: schemas.UserCreateStep2,
# ) -> Any:
#     """
#     Second step of registration - complete user registration with password
#     """
#     registration_token = crud.registration_token.get_by_token(db, token=user_in.token)
#     if not registration_token:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid token"
#         )
#
#     if registration_token.is_used:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Token already used"
#         )
#
#     if registration_token.expires_at < datetime.utcnow():
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Token expired"
#         )
#
#     user = crud.user.get_by_email(db, email=registration_token.email)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="User not found"
#         )
#
#     # Update user with additional data
#     user = crud.user.update_step2(
#         db,
#         db_obj=user,
#         obj_in=user_in
#     )
#
#     # Mark token as used
#     crud.registration_token.mark_as_used(db, token=user_in.token)
#
#     # Create access token
#     access_token = security.create_access_token(
#         data={"sub": user.email}
#     )
#
#     return {
#         "access_token": access_token,
#         "token_type": "bearer"
#     }
#
# @router.post("/token", response_model=schemas.Token)
# def login(
#     db: Session = Depends(get_db),
#     form_data: OAuth2PasswordBearer = Depends()
# ) -> Any:
#     """
#     OAuth2 compatible token login, get an access token for future requests
#     """
#     user = crud.user.authenticate(
#         db, email=form_data.username, password=form_data.password
#     )
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     elif not user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Inactive user"
#         )
#
#     access_token = security.create_access_token(
#         data={"sub": user.email}
#     )
#
#     return {
#         "access_token": access_token,
#         "token_type": "bearer"
#     }