from datetime import datetime
from re import sub
from flask import current_app, request, Response
from requests import post as client_request
from jwt import decode, encode
from redis import Redis
from sqlalchemy.exc import SQLAlchemyError
from ..auth import Auth
from ..models import ReportModel

@Auth.authenticate
def index(user=None):
    model = ReportModel()
    query = model.query()
    data = model.get(query)

    return data

@Auth.authenticate
def post(user=None):
    if (request.is_json == False):
        return Response(status=400)

    try:
        corporate_id = str(request.json.get('account').get('id'))

        corporate_name = sub(r'/[^A-Za-z0-9\ ]/', '', request.json.get('account').get('name'))

        while len(corporate_name) > 56:
            corporate_name = corporate_name.partition(' ')
            corporate_name = corporate_name[1].join(corporate_name[2:(len(corporate_name) - 1)])

        trader_name = sub(r'/[^A-Za-z\ ]/', '', ('{} {}').format(request.json.get('user').get('first_name'), request.json.get('user').get('last_name')))

        while len(trader_name) > 20:
            trader_name = trader_name.partition(' ')
            trader_name = trader_name[1].join(trader_name[2:(len(trader_name) - 1)])

        remarks = request.json.get('lhbu_remarks')

        report = ReportModel(
            transaction_id = ('FX{}{}').format(datetime.fromisoformat(request.json.get('created_at')).strftime('%d%m%y'), request.json.get('id')),
            transaction_date = datetime.fromisoformat(request.json.get('created_at')).strftime('Ymd His'),
            corporate_id = corporate_id[0:4],
            corporate_name = corporate_name,
            platform = current_app.config.get('CLIENT_PLATFORM'),
            deal_type = ['TOD', 'TOM', 'Spot', 'Forward'][request.json.get('tod_tom_spot_forward')],
            direction = request.json.get('buy_sell'),
            base_currency = request.json.get('currency').get('code'),
            quote_currency = 'IDR',
            base_volume = request.json.get('amount'),
            quote_volume = request.json.get('amount') * request.json.get('customer_rate'),
            periods = request.json.get('tod_tom_spot_forward'),
            near_rate = request.json.get('customer_rate'),
            far_rate = None,
            near_value_date = datetime.fromisoformat(request.json.get('created_at')).strftime('Ymd His'),
            far_value_date = None,
            confirmed_at = datetime.fromisoformat(request.json.get('created_at')).strftime('Ymd His'),
            confirmed_by = trader_name,
            trader_id = request.json.get('user_id'),
            trader_name = trader_name,
            transaction_purpose = ('{} {}').format((f'0{remarks[0]}')[-2:], (f'00{remarks[1]}')[-3:])
        )

        client_token_url = current_app.config.get('CLIENT_TOKEN_URL')
        client_data_url = current_app.config.get('CLIENT_DATA_URL')
        client_id = current_app.config.get('CLIENT_ID')
        client_secret = current_app.config.get('CLIENT_SECRET')
        client_scope = current_app.config.get('CLIENT_SCOPE')
        client_username = current_app.config.get('CLIENT_USERNAME')
        client_bank_id = current_app.config.get('CLIENT_BANK_ID')

        client_post = client_request(
            client_token_url,
            data={
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': client_scope
            }
        )

        data = []

        for key, value in vars(report).items():
            data.append((key.replace('_id', '_ID').capitalize(), value))

        if client_post.status_code == 200:
            client_post = client_request(
                client_data_url,
                headers={
                    'Authorization': ('Bearer {}').format(client_post.json().get('access_token')),
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-BI-CLIENT-ID': client_id,
                    'X-BI-CLIENT-SECRET': client_secret,
                },
                data={
                    'Username': client_username,
                    'SandiBank': client_bank_id,
                    'Data': [data]
                }
            )

            report.status_code = client_post.status_code
            report.status_text = client_post.text

        report.user_id = user.get('user_id')

        try:
            report.save()

        except SQLAlchemyError:
            return Response(status=500)

    except KeyError:
        return Response(status=400)

    return Response(status=200)

def authorize():
    code = request.values.get('auth-token')
    client_url = current_app.config.get('CLIENT_AUTH_URL')

    client_response = client_request(client_url, data={'code': code})

    if client_response.status_code == 200:
        client_response = client_response.json()

        payload = decode(client_response.get('access_token'), client_response.get('id_token'), algorithms=['HS256'])

        access_token = encode(
            {
                'sub': payload.get('sub'),
                'user_id': payload.get('user_id')
            },
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

        redis = Redis()

        redis.set(('token:{}').format(payload.get('sub')), 'authenticated')
        redis.expire(('token:{}').format(payload.get('sub')), client_response.get('expires_in'))

        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': redis.ttl(('token:{}').format(payload.get('sub')))
        }

    return Response(status=401)
