from tastypie.authentication import Authentication
from tastypie.authorization import Authorization

class CustomAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if request.user.is_authenticated():
          return True

        return False

    def get_identifier(self, request):
        return request.user.username

class CustomAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        if request.user.is_superuser():
            return True
        else:
            return False

