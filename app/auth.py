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
            redis = Redis()

            if redis.keys('user-session:*'):
                return Response(status=403)

            secret_key = current_app.config.get('SECRET_KEY')
            access_token = request.headers['Authorization'].partition('Bearer ')
            access_token = access_token[2]

            for session in redis.keys('user-session:*'):
                if redis.hget(session, 'access_token') and access_token
                    try:
                        decode(access_token, secret_key, algorithms=['HS256'])

                    except DecodeError:
                        return Response(status=403)

                    return route(*args, **kwargs)

            return Response(status=403)

        return wrapper
