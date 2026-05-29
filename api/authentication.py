from django.utils import timezone
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CollectorTokenAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'api.authentication.CollectorTokenAuthentication'
    name = 'collectorTokenAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-Collector-Token',
            'description': 'Token de autenticação do script coletor.',
        }


class CollectorTokenAuthentication(BaseAuthentication):
    """Autentica o script coletor via header X-Collector-Token."""

    def authenticate(self, request):
        token_key = request.headers.get('X-Collector-Token')
        if not token_key:
            return None

        from .models import CollectorToken
        try:
            token = CollectorToken.objects.select_related('user').get(token=token_key)
        except CollectorToken.DoesNotExist:
            raise AuthenticationFailed('Token de coletor inválido.')

        token.last_used_at = timezone.now()
        token.save(update_fields=['last_used_at'])
        return (token.user, token)

    def authenticate_header(self, request):
        return 'X-Collector-Token'
