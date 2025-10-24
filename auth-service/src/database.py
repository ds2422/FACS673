from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Get database URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create the database engine
if SQLALCHEMY_DATABASE_URL.startswith('postgresql'):
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    # For SQLite (development)
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for getting a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
