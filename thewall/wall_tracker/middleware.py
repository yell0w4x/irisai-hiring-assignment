from wall_tracker.stuff import make_response
from wall_tracker.models import WallProfile

from rest_framework import status
from django.http import JsonResponse

from uuid import uuid4
import logging


_logger = logging.getLogger(__name__)


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request, *args, **kwargs):
        request.id = uuid4()
        _logger.debug(f'Request: [{request.id=}; {request=}; {args=}; {kwargs=}]')
        response = self.get_response(request)
        return response


class DisallowPostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request, *args, **kwargs):
        if request.method == 'POST':
            return make_response(request_id=request.id, 
                                 result='error', 
                                 desc='Method not allowed', 
                                 status=status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.get_response(request)
        return response
