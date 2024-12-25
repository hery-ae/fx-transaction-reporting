from functools import wraps
from flask import current_app, request, Response
from jwt import decode, DecodeError
from redis import Redis

class Auth:
    def __init__(self, route):
        self.route = route

    def authenticate(route):
        @wraps(route)
        def wrapper(*args, **kwargs):
            access_token = request.headers.get('Authorization')
            access_token = access_token and access_token.startswith('Bearer ') and access_token[len('Bearer '):]

            try:
                payload = decode(access_token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])

                redis = Redis()

                if redis.exists(('token:{}').format(payload.get('sub'))):
                    return route(*args, **kwargs, user={ 'user_id': payload.get('user_id') })

            except DecodeError:
                pass

            return Response(status=403)

        return wrapper
