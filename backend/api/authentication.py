# api/authentication.py
from rest_framework import authentication
from rest_framework import exceptions
from firebase_admin import auth as firebase_auth
from django.contrib.auth.models import User

class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        token = auth_header.split(' ').pop()
        
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            uid = decoded_token['uid']
            # We don't necessarily need a Django User model, 
            # but DRF expects a user-like object.
            # We return a simple tuple (user_id_string, None)
            return (uid, None) 
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid Firebase Token')