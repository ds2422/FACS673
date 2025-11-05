import jwt
from jwt import InvalidTokenError
from django.conf import settings
from rest_framework import authentication, exceptions


class CustomJWTAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication for microservices using shared JWT secret.
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split(" ")
            if prefix.lower() != "bearer":
                return None
        except ValueError:
            return None

        try:
            payload = jwt.decode(
                token,
                settings.JWT_CONFIG["SIGNING_KEY"],
                algorithms=[settings.JWT_CONFIG["ALGORITHM"]],
                audience=settings.JWT_CONFIG["AUDIENCE"],
                issuer=settings.JWT_CONFIG["ISSUER"]
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.InvalidAudienceError:
            raise exceptions.AuthenticationFailed("Invalid token audience")
        except jwt.InvalidIssuerError:
            raise exceptions.AuthenticationFailed("Invalid token issuer")
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(f"Invalid token: {str(e)}")

        # ✅ Create a lightweight user object compatible with DRF
        class AuthUser:
            def __init__(self, id, email):
                self.id = id
                self.email = email
                self.username = email  # optional
                self.is_authenticated = True  # ✅ Important for DRF permissions

        user = AuthUser(
            id=payload.get("user_id"),
            email=payload.get("sub"),
        )

        return (user, None)
