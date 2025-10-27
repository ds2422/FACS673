from sqlalchemy.orm import Session
from passlib.context import CryptContext

import models, schemas


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_summaries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Summary).offset(skip).limit(limit).all()

def get_user_summaries(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Summary).filter(models.Summary.user_id == user_id).offset(skip).limit(limit).all()

def create_user_summary(db: Session, summary: schemas.SummaryCreate, user_id: int):
    db_summary = models.Summary(**summary.dict(), user_id=user_id)
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary

def get_summary(db: Session, summary_id: int):
    return db.query(models.Summary).filter(models.Summary.id == summary_id).first()

def delete_summary(db: Session, summary_id: int):
    db_summary = db.query(models.Summary).filter(models.Summary.id == summary_id).first()
    if db_summary:
        db.delete(db_summary)
        db.commit()
        return True
    return False
