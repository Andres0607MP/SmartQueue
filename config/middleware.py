from typing import Optional

from django.utils.deprecation import MiddlewareMixin


class AuthorizationHeaderMiddleware(MiddlewareMixin):
    """Ensure Authorization header is available in request.META as HTTP_AUTHORIZATION.

    Some proxies / WSGI servers may put the header in different keys or strip it.
    This middleware tries common alternatives and copies them to HTTP_AUTHORIZATION
    so DRF / SimpleJWT can read the header.
    """

    def process_request(self, request):
        meta = request.META
        # If already set, nothing to do
        if meta.get('HTTP_AUTHORIZATION'):
            return None

        # Common alternatives
        for key in ('Authorization', 'authorization', 'HTTP_X_AUTHORIZATION', 'X-Authorization'):
            val = meta.get(key)
            if val:
                meta['HTTP_AUTHORIZATION'] = val
                break

        return None
