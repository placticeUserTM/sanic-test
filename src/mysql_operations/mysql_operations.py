# encode:UTF-8
from sanic import Blueprint
from sanic.response import json
from sanic.log import logger

bp_mysql = Blueprint('mysql_operations')


@bp_mysql.route('/get-mysql-data')
async def get_mysql_data(request):
    values = await request.app.mysql.query('select id, name, ip_address from users')
    result = []

    for val in values:
        result.append({
            "id": val[0],
            "name": val[1],
            "ip_address": val[2]
        })
    return json(result, status=200)


@bp_mysql.route('/insert-mysql-data', methods=['POST'])
async def insert_mysql_data(request):
    params = request.json

    if not params or 'user_name' not in params:
        return json({'message': 'invalid parameters.'}, status=400)

    ins_user = params['user_name']
    ip = request.headers['X-Real-IP']
    query = f'insert into users(name, ip_address) values("{ins_user}", "{ip}")'
    await request.app.mysql.execute(query)
    return json({'message': 'ok'}, status=200)
