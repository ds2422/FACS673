import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn
from jose import JWTError, jwt
from sqlalchemy.orm import Session

# Internal imports
from url_summarizer.database import get_db, create_tables
from url_summarizer import models, schemas, crud
from url_summarizer.config import SECRET_KEY, ALGORITHM
from url_summarizer.services.summarizer import URLSummarizer

# ---------------------------------------------------------
# FastAPI app setup
# ---------------------------------------------------------
app = FastAPI(title="URL Summarization Service")

# Create tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for security if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------
class URLRequest(BaseModel):
    url: str
    summary_length: Optional[int] = Field(default=5, gt=0, le=20)


# ---------------------------------------------------------
# JWT & Authentication
# ---------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Verify JWT token issued by auth-service and extract user info.
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience="url-summarizer",   # ✅ Expected audience
            issuer="auth-service"        # ✅ Must match issuer from auth-service
        )

        user_id = payload.get("user_id")
        email = payload.get("sub")

        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # ✅ Return decoded user data (no DB lookup)
        return {"user_id": user_id, "email": email}

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------
# URL Summarization Endpoints
# ---------------------------------------------------------
@app.post("/summarize")
async def summarize_url(
    request: URLRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Summarize content from a given URL and save it to the database.
    """
    try:
        # Get user ID from the JWT token
        user_id = current_user["user_id"]
        # We trust the auth service's JWT, so we don't need to create users here

        summarizer = URLSummarizer()
        summary_text = await summarizer.summarize(request.url, request.summary_length)

        # Handle dict summaries (from some AI models)
        if isinstance(summary_text, dict):
            summary_text = summary_text.get("summary", str(summary_text))

        # Save summary record
        db_summary = models.Summary(
            url=request.url,
            content="",  # Optional: store original full content here
            summary=summary_text,
            summary_length=request.summary_length,
            user_id=user_id
        )

        db.add(db_summary)
        db.commit()
        db.refresh(db_summary)

        return {
            "url": request.url,
            "summary": summary_text,
            "summary_id": db_summary.id,
            "user_id": user_id
        }

    except Exception as e:
        print(f"❌ Error during summarization: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/summaries/me/", response_model=List[schemas.Summary])
async def read_user_summaries(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all summaries created by the current user.
    The user is identified by the user_id in the JWT token from auth-service.
    """
    try:
        user_id = current_user["user_id"]
        # Get summaries for this user directly without checking if user exists
        summaries = db.query(models.Summary)\
            .filter(models.Summary.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
        return summaries
    except Exception as e:
        print(f"❌ Error fetching user summaries: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/summaries/{summary_id}", response_model=schemas.Summary)
async def read_summary(
    summary_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific summary belonging to the authenticated user.
    """
    db_summary = (
        db.query(models.Summary)
        .filter(
            models.Summary.id == summary_id,
            models.Summary.user_id == current_user["user_id"]
        )
        .first()
    )

    if db_summary is None:
        raise HTTPException(status_code=404, detail="Summary not found")

    return db_summary


@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}


# ---------------------------------------------------------
# Run the app
# ---------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("url_summarizer.main:app", host="0.0.0.0", port=8003, reload=True)
