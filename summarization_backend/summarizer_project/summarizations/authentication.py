from rest_framework_simplejwt.authentication import JWTAuthentication

class AuthServiceJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        # if your auth-service uses "sub" instead of "user_id"
        user_id = validated_token.get("sub") or validated_token.get("id")
        if not user_id:
            raise Exception("Token missing sub/id field")

        # You can skip DB lookup if your service just needs to trust the token:
        from django.contrib.auth.models import AnonymousUser
        user = AnonymousUser()
        user.id = user_id
        return user
