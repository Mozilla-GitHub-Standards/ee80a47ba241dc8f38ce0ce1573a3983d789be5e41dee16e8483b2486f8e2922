# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.


from functools import wraps


def set_cors_headers(origin=None, methods='GET'):
    """Decorator function that sets CORS headers on the response."""
    if isinstance(methods, str):
        methods = [methods]

    def decorator(func):

        @wraps(func)
        def inner(*args, **kwargs):
            response = func(*args, **kwargs)
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = ','.join(methods)
            return response

        return inner

    return decorator
