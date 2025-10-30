import jwt
import logging
from rest_framework import authentication, exceptions
from django.conf import settings
from django.contrib.auth import get_user_model
from jwt import PyJWTError

logger = logging.getLogger(__name__)

class JWTAuthentication(authentication.BaseAuthentication):
    """
    Custom JWT authentication for file_service that validates tokens from auth-service.
    """
    
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            logger.warning("No Authorization header provided")
            return None
            
        try:
            # Extract the token from the header
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                logger.warning(f"Invalid Authorization header format: {auth_header}")
                return None
                
            token = parts[1]
            logger.debug(f"Received token: {token[:20]}...")  # Log first 20 chars of token
            
            # Log settings being used
            logger.debug(f"JWT Settings - Algorithm: {settings.JWT_ALGORITHM}")
            logger.debug(f"JWT Settings - Issuer: {settings.JWT_ISSUER}")
            logger.debug(f"JWT Settings - Audience: {settings.JWT_AUDIENCE}")
            logger.debug(f"JWT Settings - Verify Audience: {settings.JWT_VERIFY_AUDIENCE}")
            
            # Get JWT settings
            verifying_key = settings.JWT_VERIFYING_KEY
            algorithm = settings.JWT_ALGORITHM
            audience = settings.JWT_AUDIENCE
            issuer = settings.JWT_ISSUER
            
            if not verifying_key:
                logger.error("JWT_VERIFYING_KEY not set in settings")
                raise exceptions.AuthenticationFailed("Authentication configuration error")
            
            # Configure verification options
            options = {
                'verify_signature': True,
                'verify_exp': True,
                'verify_aud': settings.JWT_VERIFY_AUDIENCE,
                'verify_iss': True,
                'require': ['exp', 'sub', 'aud', 'iss'],
            }
            
            logger.debug(f"Verification options: {options}")
            
            try:
                # First, decode without verification to inspect the token
                unverified = jwt.decode(token, options={"verify_signature": False})
                logger.debug(f"Unverified token payload: {unverified}")
                
                # Now verify the token
                payload = jwt.decode(
                    token,
                    verifying_key,
                    algorithms=[algorithm],
                    audience=audience,
                    issuer=issuer,
                    options=options
                )
                logger.debug(f"Token verified successfully for user: {payload.get('sub')}")
                
            except jwt.ExpiredSignatureError:
                logger.warning("Token has expired")
                raise exceptions.AuthenticationFailed('Token has expired')
            except jwt.InvalidAudienceError:
                logger.warning(f"Invalid audience. Expected: {audience}, Got: {unverified.get('aud')}")
                raise exceptions.AuthenticationFailed('Invalid audience')
            except jwt.InvalidIssuerError:
                logger.warning(f"Invalid issuer. Expected: {issuer}, Got: {unverified.get('iss')}")
                raise exceptions.AuthenticationFailed('Invalid issuer')
            except jwt.InvalidTokenError as e:
                logger.warning(f"Invalid token: {str(e)}")
                raise exceptions.AuthenticationFailed(f'Invalid token: {str(e)}')
            
            # Get or create the user
            user = self.get_or_create_user(payload)
            if not user:
                logger.error("Failed to get or create user from token")
                raise exceptions.AuthenticationFailed('User not found or could not be created')
            
            return (user, token)
            
        except exceptions.AuthenticationFailed as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise
        except Exception as e:
            logger.exception("Unexpected error during authentication")
            raise exceptions.AuthenticationFailed('Authentication failed')
    
    def get_or_create_user(self, payload):
        """Get or create a user based on JWT payload."""
        User = get_user_model()
        user_id = payload.get('sub')
        
        if not user_id:
            logger.warning("No 'sub' claim in token")
            return None
            
        try:
            # Try to get the existing user
            user = User.objects.get(username=user_id)
            # Update user details if needed
            if hasattr(user, 'email') and 'email' in payload:
                if user.email != payload['email']:
                    user.email = payload['email']
                    user.save(update_fields=['email'])
            return user
        except User.DoesNotExist:
            # Create a new user if they don't exist
            user_data = {
                'username': user_id,
                'email': payload.get('email', ''),
                'is_active': True,
            }
            try:
                return User.objects.create_user(**user_data)
            except Exception as e:
                logger.error(f"Failed to create user: {str(e)}")
                return None