from Warehouse import settings
from rest_framework import authentication, exceptions
from django.contrib.auth.models import User


class StoreAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'StoreToken'

    def authenticate(self, request):
        request.user = None

        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            return None

        elif len(auth_header) > 2:
            return None

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            return None

        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        if token != settings.STORE_TOKEN:
            raise(exceptions.AuthenticationFailed("Invalid token"))
        request.data['updated_by_store'] = True

        user = User()
        return user, token
