from sqlalchemy.orm import Session
from . import models, schemas
from . import security

from datetime import datetime, timedelta
from jose import JWTError, jwt
from src.config import settings
from fastapi import HTTPException, status

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
         hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not security.verify_password(password, user.hashed_password):
        return False
    return user

def get_user_by_token(db: Session, token: str):
    payload = security.verify_token(token)
    if not payload:
        return None
    email = payload.get("sub")
    if not email:
        return None
    return get_user_by_email(db, email=email)

def create_access_token(
    data: dict,
    expires_delta: timedelta = None,
    audience: str = None
):
    """
    Create a JWT access token with optional audience support.
    Works for multiple microservices (file_service, url_summarizer, etc.).
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Add standard JWT claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "auth-service",   # issuer
    })

    # ✅ Add audience dynamically if provided
    if audience:
        to_encode["aud"] = audience  # e.g., "file-service" or "url-summarizer"

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
