from datetime import datetime
from flask import current_app, request, Response
from requests import post
from sqlalchemy.exc import SQLAlchemyError
from ..auth import Auth
from ..models import ReportModel

@Auth.authenticate
def index():
    model = ReportModel()
    query = model.query()
    data = model.get(query)

    return data

@Auth.authenticate
def post():
    if (request.is_json == False):
        return Response(status=400)

    try:
        corporate_id = str(request.json.get('account').get('id'))

        corporate_name = re.sub(r'/[^A-Za-z0-9\ ]/', '', request.json.get('account').get('name'))

        while len(corporate_name) > 56:
            corporate_name = corporate_name.partition(' ')
            corporate_name = corporate_name[1].join(corporate_name[2:(len(corporate_name) - 1)])

        trader_name = re.sub(r'/[^A-Za-z\ ]/', '', f'{request.json.get('user').get('first_name')} {request.json.get('user').get('last_name')}')

        while len(trader_name) > 20:
            trader_name = trader_name.partition(' ')
            trader_name = trader_name[1].join(trader_name[2:(len(trader_name) - 1)])

        remarks = request.json.get('lhbu_remarks')

        report = new ReportModel(
            transaction_id = f'FX{datetime.fromisoformat(request.json.get('created_at')).strftime('%d%m%y')}{request.json.get('id')}',
            transaction_date = request.json.get('created_at').strftime('Ymd His'),
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
            near_value_date = request.json.get('created_at').strftime('Ymd His'),
            far_value_date = None,
            confirmed_at = request.json.get('created_at').strftime('Ymd His'),
            confirmed_by = trader_name,
            trader_id = request.json.get('user_id'),
            trader_name = trader_name,
            transaction_purpose = f'{'0'{remarks[0]}[0:(len(remarks[0]) - 2)]} {'00'{remarks[1]}[0:(len(remarks[1]) - 3)]}'
        )

        client_token_url = current_app.config.get('CLIENT_TOKEN_URL')
        client_data_url = current_app.config.get('CLIENT_DATA_URL')
        client_id = current_app.config.get('CLIENT_ID')
        client_secret = current_app.config.get('CLIENT_SECRET')
        client_scope = current_app.config.get('CLIENT_SCOPE')
        client_username = current_app.config.get('CLIENT_USERNAME')
        client_bank_id = current_app.config.get('CLIENT_BANK_ID')

        client_post = post(
            client_token_url,
            data={
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': client_scope
            }
        )

        data = []

        for key, value in report.items():
            data.append((key.replace('_id', '_ID').capitalize(), value))

        if client_post.status_code == 200:
            client_post = post(
                client_data_url,
                headers={
                    'Authorization': f'Bearer {client_post.json().get('access_token')}',
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

        try:
            report.save()

        except SQLAlchemyError:
            return Response(status=500)

    except KeyError:
        return Response(status=400)

    return Response(status=200)

def authorize():
    code = request.values.get('auth-token')
    client_url = current_app.config.get('CLIENT_URL')

    client_request = post(('{}token.json').format(client_url), data={'code': code})

    if client_request.status_code == 200:
        client_response = client_request.json()

        redis = Redis()
        session = len(redis.keys())

        redis.hset(f'user-session:{session}', mapping=client_response)

        return {
            'access_token': redis.hget(f'user-session:{session}', 'access_token'),
            'token_type': 'Bearer'
        }

    return Response(status=401)
