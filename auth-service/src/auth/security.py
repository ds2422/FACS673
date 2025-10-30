from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 🔐 Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ------------------------
# Password Hashing Helpers
# ------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its bcrypt hash."""
    try:
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        if len(plain_password) > 72:
            plain_password = plain_password[:72]
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"❌ Error verifying password: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Generate a bcrypt hash (truncated to 72 bytes for safety)."""
    password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(password)


# ------------------------
# JWT Token Functions
# ------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, audience: Optional[str] = None) -> str:
    """
    Create a JWT access token.
    The token will include sub, user_id, iss, exp, and iat claims.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    # ✅ Add required claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "auth-service",  # issuer name
        "aud" : "file-service"
    })
   
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, audience: Optional[str] = None) -> Optional[dict]:
    """
    Decode and verify a JWT token.
    - Verifies signature, expiration, and optionally audience + issuer.
    - Returns payload if valid, or raises HTTPException if invalid.
    """
    try:
        # Enable audience check only if an audience is specified
        decode_options = {"verify_aud": bool(audience)}

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience=audience,          # Will verify only if not None
            issuer=JWT_ISSUER,
            options=decode_options
        )

        # Optional: verify token expiration manually
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )

        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )