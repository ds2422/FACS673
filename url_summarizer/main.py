import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

# Internal imports
from database import get_db, create_tables
import models, schemas, crud
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from url_summarizer.services.summarizer import URLSummarizer


# Initialize app
app = FastAPI(title="URL Summarization Service")

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Pydantic Models for Request/Response ----------

class URLRequest(BaseModel):
    url: str
    summary_length: Optional[int] = Field(default=5, gt=0, le=20)


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


# ---------- Helper Functions ----------

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    print("==== TOKEN VALIDATION DEBUG ====")
    print("Received token:", token)

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_aud": False}
        )
        print("Decoded payload:", payload)

        raw_user_id = payload.get("sub")
        numeric_user_id = payload.get("user_id")

        # ✅ Prefer numeric ID first
        user = None
        if numeric_user_id:
            user = db.query(models.User).filter(models.User.id == numeric_user_id).first()
            if user:
                print(f"✅ Authenticated by numeric ID: {user.id}")
                return user
            else:
                print(f"⚠️ No user found with ID {numeric_user_id}, will try email fallback")

        # ✅ Fallback: lookup by email in sub
        if raw_user_id:
            user = db.query(models.User).filter(models.User.email == raw_user_id).first()
            if user:
                print(f"✅ Authenticated by email: {user.email} (ID {user.id})")
                return user
            else:
                print(f"❌ No user found with email {raw_user_id}")
                raise credentials_exception

        print("❌ Token missing both user_id and sub")
        raise credentials_exception

    except JWTError as e:
        print(f"❌ JWT Error: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"❌ Unexpected Error in get_current_user: {e}")
        raise credentials_exception


# ---------- Auth Endpoints ----------

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # ✅ Store the numeric ID as "sub"
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "user_id": user.id,
            "iss": JWT_ISSUER,  # should be "url-summarizer"
        },
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


# ---------- Summary Endpoints ----------

@app.post("/summarize")
async def summarize_url(
    request: URLRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Summarize content from a given URL and save to the database.
    Handles both string and dictionary summaries.
    """
    try:
        summarizer = URLSummarizer()
        summary_text = await summarizer.summarize(request.url, request.summary_length)

        # ✅ Ensure summary_text is a string before saving
        if isinstance(summary_text, dict):
            summary_text = summary_text.get("summary", str(summary_text))

        db_summary = models.Summary(
            url=request.url,
            content="",  # Optional: store original full content here
            summary=summary_text,
            summary_length=request.summary_length,
            user_id=current_user.id
        )

        db.add(db_summary)
        db.commit()
        db.refresh(db_summary)

        return {
            "url": request.url,
            "summary": summary_text,
            "summary_id": db_summary.id
        }

    except Exception as e:
        # Log or print the error for debugging
        print(f"❌ Error during summarization: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/summaries/me/", response_model=List[schemas.Summary])
async def read_user_summaries(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    summaries = db.query(models.Summary).filter(models.Summary.user_id == current_user.id).offset(skip).limit(limit).all()
    return summaries


@app.get("/summaries/{summary_id}", response_model=schemas.Summary)
async def read_summary(
    summary_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_summary = db.query(models.Summary).filter(models.Summary.id == summary_id, models.Summary.user_id == current_user.id).first()
    if db_summary is None:
        raise HTTPException(status_code=404, detail="Summary not found")
    return db_summary


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ---------- Run the App ----------
if __name__ == "__main__":
    uvicorn.run("url_summarizer.main:app", host="0.0.0.0", port=8000, reload=True)
