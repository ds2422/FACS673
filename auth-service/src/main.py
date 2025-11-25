from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import uvicorn
import os

# Local imports
from .auth import schemas, security, models, crud
from .database import SessionLocal, engine

# Create DB tables
models.Base.metadata.create_all(bind=engine)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Auth Service API",
        version="1.0.0",
        description="Authentication and User Management Service",
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    # Add security to all endpoints
    for path in openapi_schema["paths"].values():
        for method in path.values():
            if method.get("operationId") == "login_for_access_token_token_post":
                continue
            method["security"] = [{"OAuth2PasswordBearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Initialize FastAPI with custom docs
app = FastAPI(
    title="Auth Service API",
    description="Authentication and User Management Service with JWT Tokens",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/v1/openapi.json"
)

# Apply custom OpenAPI schema
app.openapi = custom_openapi

# Custom docs endpoints
@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation():
    return get_swagger_ui_html(
        openapi_url="/api/v1/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation():
    return get_redoc_html(
        openapi_url="/api/v1/openapi.json",
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ✅ Verify token and get current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = security.verify_token(token)
    if not payload:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    return user

# ✅ Generate token with both email & user_id
@app.post(
    "/token",
    response_model=schemas.Token,
    summary="User Login",
    description="Authenticate user and get access token",
    response_description="Access token for authenticated requests",
    tags=["Authentication"]
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(
        data={
            "sub": user.email,     # ✅ subject (email)
            "user_id": user.id     # ✅ new field for Django compatibility
        },
        expires_delta=timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# ✅ Register a new user
@app.post(
    "/register/",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Create a new user account",
    response_description="User details for the newly created account",
    tags=["Users"]
)
def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return crud.create_user(db=db, user=user)

# ✅ Get user profile
@app.get(
    "/users/me/",
    response_model=schemas.User,
    summary="Get Current User",
    description="Get details of the currently authenticated user",
    response_description="User details",
    tags=["Users"]
)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# ✅ Health check
@app.get(
    "/health",
    summary="Health Check",
    description="Check if the authentication service is running",
    response_description="Service status information",
    tags=["System"]
)
async def health_check():
    return {
        "status": "healthy",
        "service": "auth-service",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
