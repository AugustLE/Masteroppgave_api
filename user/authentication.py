from rest_framework.authentication import TokenAuthentication
from django.conf import settings
from rest_framework import exceptions
from rest_framework.authtoken.models import Token
import pytz
from datetime import datetime


class ExpiringTokenAuthentication(TokenAuthentication):

    def authenticate_credentials(self, key):

        try:
            #token = self.model.objects.get(key=key)
            token = Token.objects.get(key=key)

        except: #self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')

        utc_now = datetime.utcnow()
        utc_now = utc_now.replace(tzinfo=pytz.utc)

        if token.created < utc_now - settings.TOKEN_EXPIRE_TIME:
            raise exceptions.AuthenticationFailed('Token has expired')

        return token.user, token