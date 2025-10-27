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
                settings.SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
        except InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

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
