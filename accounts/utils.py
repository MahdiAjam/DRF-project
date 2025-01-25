from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.exceptions import TokenError

class CustomAccessToken(AccessToken):
    def verify(self):
        super().verify()

        jti = self.payload.get('jti')
        try:
            token_obj = OutstandingToken.objects.get(jti=jti)

            if token_obj.blacklistedtoken:
                raise TokenError('Token is blacklisted.')

        except OutstandingToken.DoesNotExist:
            pass
        except BlacklistedToken.DoesNotExist:
            pass
