import jwt
from rest_framework import authentication, exceptions
from django.conf import settings
from django.contrib.auth import get_user_model

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
            
        try:
            # Extract the token from the header
            prefix, token = auth_header.split()
            if prefix.lower() != 'bearer':
                return None
                
            # Verify the token locally
            payload = jwt.decode(
                token,
                settings.JWT_VERIFYING_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                audience=settings.JWT_AUDIENCE,
                issuer=settings.JWT_ISSUER
            )
            
            # Get or create the user
            User = get_user_model()
            user, _ = User.objects.get_or_create(
                username=payload.get('sub'),
                defaults={'email': payload.get('email', '')}
            )
            
            return (user, None)
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(f'Invalid token: {str(e)}')
        except Exception as e:
            raise exceptions.AuthenticationFailed(str(e))