import os
from django.core.exceptions import ImproperlyConfigured


class CheckTunesDirExistsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not os.path.isdir(os.environ.get('TUNES_DIR')):
            raise ImproperlyConfigured('The directory for storing tunes does not exist. Please insert your storage device and correctly reference it in your .env file.')

        response = self.get_response(request)

        return response
