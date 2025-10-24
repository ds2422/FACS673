from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
import uvicorn
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from services.summarizer import URLSummarizer
from database import SessionLocal, User, Summary, get_db
import models
import schemas
import crud
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI(title="URL Summarization Service")

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class URLRequest(BaseModel):
    url: str
    summary_length: Optional[int] = Field(default=5, gt=0, le=20)  # Number of sentences for summary (1-20)
    
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserInDB(UserCreate):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# Auth endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# Summary endpoints
@app.post("/summarize")
async def summarize_url(
    request: URLRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Summarize content from a given URL and save to database.
    
    - **url**: The URL to summarize (supports YouTube and regular web pages)
    - **summary_length**: Number of sentences in the summary (1-20, default: 5)
    """
    try:
        summarizer = URLSummarizer()
        summary_text = summarizer.summarize_url(request.url, request.summary_length)
        
        # Save to database
        db_summary = Summary(
            url=request.url,
            content="",  # You might want to store the full content here
            summary=summary_text,
            summary_length=request.summary_length,
            user_id=current_user.id
        )
        db.add(db_summary)
        db.commit()
        db.refresh(db_summary)
        
        return {"url": request.url, "summary": summary_text, "summary_id": db_summary.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/summaries/me/", response_model=List[schemas.Summary])
async def read_user_summaries(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all summaries for the current user.
    """
    summaries = db.query(Summary).filter(Summary.user_id == current_user.id).offset(skip).limit(limit).all()
    return summaries

@app.get("/summaries/{summary_id}", response_model=schemas.Summary)
async def read_summary(
    summary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific summary by ID.
    """
    db_summary = db.query(Summary).filter(Summary.id == summary_id, Summary.user_id == current_user.id).first()
    if db_summary is None:
        raise HTTPException(status_code=404, detail="Summary not found")
    return db_summary

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
