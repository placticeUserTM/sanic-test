# encode:UTF-8
from sanic import Blueprint
from sanic.response import json
from sanic.log import logger
from datetime import datetime
import uuid

from src.util.function import register_log

bp_cassandra = Blueprint('cassandra_operations')


@bp_cassandra.route('/get-cassandra-data')
@bp_cassandra.route('/get-cassandra-data/<post_id>')
@register_log
async def get_cassandra_data(request, post_id=None):
    if post_id:
        query = """
        SELECT id, data, update_time FROM cassandra_sample.logs WHERE id = %s;
        """
        values = await request.app.cassandra.query(query, args=[post_id])
    else:
        query = 'SELECT id, data, update_time FROM cassandra_sample.logs;'
        values = await request.app.cassandra.query(query)
    return json(proc_response(values))


@bp_cassandra.route('/get-pagination-data')
async def get_pagination_data(request):
    query = 'SELECT id, data, update_time FROM cassandra_sample.logs;'
    values = await request.app.cassandra.pagination(query, fetch_size=10)
    return json(proc_response(values))


@bp_cassandra.route('/insert-cassandra-data', methods=['POST'])
async def insert_cassandra_data(request):
    params = request.json

    if not params or 'data' not in params:
        return json({'message': 'invalid parameters.'}, status=400)

    query = """
    INSERT INTO cassandra_sample.logs (id, data, update_time) VALUES (%s, %s, %s);
    """
    user_id = str(uuid.uuid4())
    data = params['data']

    await request.app.cassandra.execute_query(query, [user_id, data, datetime.now()])
    return json({'message': 'ok'}, status=200)


@bp_cassandra.route('/get_access_log')
async def get_access_log(request):
    query = """
    SELECT ip, url, request_headers, request_body, method, update_time
     FROM cassandra_sample.access_logs;
     """
    values = await request.app.cassandra.pagination(query, fetch_size=100)
    return json(proc_log_response(values))


def proc_response(values):
    result = []
    for val in values:
        result.append({
            'id': val.id,
            'data': val.data,
            'update_time': val.update_time.strftime('%Y/%m/%d %H:%M:%S.%f')
        })
    return {'all_count': len(result), 'result': result}


def proc_log_response(values):
    result = []
    for val in values:
        result.append({
            'ip': val.ip,
            'url': val.url,
            'request_headers': val.request_headers,
            'request_body': val.request_body,
            'method': val.method,
            'update_time': val.update_time.strftime('%Y/%m/%d %H:%M:%S.%f')
        })
    return result
