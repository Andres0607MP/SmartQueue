from typing import Any

from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    
    response = drf_exception_handler(exc, context)


    if response is not None:
        status_code = response.status_code

        if isinstance(exc, exceptions.AuthenticationFailed):
            error_key = "authentication_failed"
        elif isinstance(exc, exceptions.NotAuthenticated):
            error_key = "not_authenticated"
        elif isinstance(exc, exceptions.PermissionDenied):
            error_key = "permission_denied"
        elif isinstance(exc, exceptions.NotFound) or isinstance(exc, Http404):
            error_key = "not_found"
        elif isinstance(exc, exceptions.ValidationError):
            error_key = "bad_request"
        else:
            error_key = "error"

        detail = response.data
        if isinstance(detail, dict) and "detail" in detail:
            message = detail["detail"]
        else:
            message = detail

        response.data = {
            "detail": message,
            "code": status_code,
            "error": error_key,
        }

        return response

    return Response(
        {
            "detail": "Internal server error.",
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error": "server_error",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
