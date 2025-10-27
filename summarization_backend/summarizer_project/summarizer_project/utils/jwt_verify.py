import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from django.conf import settings


def verify_jwt_token(token: str):
    """
    Verifies JWT token issued by auth-service.
    Returns decoded payload dict if valid, None if invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        print("✅ JWT verified successfully:", payload)
        return payload
    except ExpiredSignatureError:
        print("❌ Token expired")
        return None
    except InvalidTokenError as e:
        print(f"❌ Invalid token: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Unexpected JWT error: {str(e)}")
        return None
