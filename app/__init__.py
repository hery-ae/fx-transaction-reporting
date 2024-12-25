import os
from flask import Flask
from .blueprints import index, post, authorize
from .database import init_db

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(8).hex()

app.config.from_prefixed_env()

app.config['CLIENT_AUTH_URL'] = app.config.get('CLIENT_AUTH_URL') or 'http://localhost:8080/nop/token.json'

app.config['CLIENT_TOKEN_URL'] = app.config.get('CLIENT_TOKEN_URL') or 'http://localhost:8080/reports/token.json'
app.config['CLIENT_ID'] = app.config.get('CLIENT_ID') or '1'
app.config['CLIENT_SECRET'] = app.config.get('CLIENT_SECRET') or 'secret'
app.config['CLIENT_SCOPE'] = app.config.get('CLIENT_SECRET') or 'scope'
app.config['CLIENT_DATA_URL'] = app.config.get('CLIENT_DATA_URL') or 'http://localhost:8080/reports/data'
app.config['CLIENT_PLATFORM'] = app.config.get('CLIENT_PLATFORM') or 'platform'
app.config['CLIENT_BANK_ID'] = app.config.get('CLIENT_BANK_ID') or '1'
app.config['CLIENT_USERNAME'] = app.config.get('CLIENT_USERNAME') or 'username'
app.config['CLIENT_THRESHOLD'] = app.config.get('CLIENT_THRESHOLD') or 25000

with app.app_context():
    init_db()

@app.after_request
def afterrequest(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST'

    return response

app.add_url_rule(
    '/',
    view_func=index,
    methods=['GET']
)

app.add_url_rule(
    '/',
    view_func=post,
    methods=['POST']
)

app.add_url_rule(
    '/auth',
    view_func=authorize,
    methods=['POST']
)
