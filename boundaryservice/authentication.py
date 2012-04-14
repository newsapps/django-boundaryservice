from django.contrib.auth.models import User

from tastypie.authentication import ApiKeyAuthentication


class NoOpApiKeyAuthentication(ApiKeyAuthentication):
    """
    Allows all users access to all objects, but ensures ApiKeys are properly
    processed for throttling.
    """
    def is_authenticated(self, request, **kwargs):

        username = request.GET.get('username') or request.POST.get('username')
        api_key = request.GET.get('api_key') or request.POST.get('api_key')

        if not username:
            return True

        try:
            user = User.objects.get(username=username)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return self._unauthorized()

        request.user = user

        return self.get_key(user, api_key)

    def _get_anonymous_identifier(self, request):
        return 'anonymous_%s' % request.META.get('REMOTE_ADDR', 'noaddr')

    def get_identifier(self, request):
        return request.REQUEST.get(
            'username', self._get_anonymous_identifier(request))
