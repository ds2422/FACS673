import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Application
    APP_NAME = "Auth Service"
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    VERSION = "1.0.0"
    
    # Database
    DB_ENGINE = os.getenv("DB_ENGINE", "postgresql")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "auth_service_db")
    
    # Construct the database URL
    if DB_ENGINE == "postgresql":
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        # Fallback to SQLite if not PostgreSQL
        DATABASE_URL = "sqlite:///./auth.db"
    
    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-this-in-production")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # API
    API_PREFIX = "/api/v1"
    
settings = Settings()
