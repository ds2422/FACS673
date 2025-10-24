from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    username: str

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to return to client
class User(UserBase):
    id: int
    is_active: bool = True

    class Config:
        orm_mode = True

# Token related schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Summary related schemas
class SummaryBase(BaseModel):
    url: str
    content: Optional[str] = None
    summary: str
    summary_length: int = 5

class SummaryCreate(SummaryBase):
    pass

class Summary(SummaryBase):
    id: int
    created_at: datetime
    user_id: int

    class Config:
        orm_mode = True

# For URL summarization request
class URLRequest(BaseModel):
    url: str
    summary_length: Optional[int] = 5

    class Config:
        schema_extra = {
            "example": {
                "url": "https://example.com/article",
                "summary_length": 5
            }
        }
