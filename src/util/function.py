# encode:UTF-8
from datetime import datetime
import functools
import json


async def insert_log(request):
    ip = request.headers['X-Real-IP']
    url = request.url
    request_body = request.body.decode('UTF-8')
    request_headers = proc_request_headers(request.headers)
    request_method = request.method

    args = [ip, url, request_headers, request_body, request_method, datetime.now()]
    await request.app.cassandra.insert_access_log(args)


def register_log(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        await insert_log(*args)
        return await f(*args, **kwargs)
    return wrapper


def proc_request_headers(request_headers):
    return json.dumps({
        'x-forwarded-for': request_headers.get('x-forwarded-for'),
        'x-forwarded-proto': request_headers.get('x-forwarded-proto'),
        'x-forwarded-host': request_headers.get('x-forwarded-host'),
        'x-forwarded-server': request_headers.get('x-forwarded-server'),
        'x-real-ip': request_headers.get('x-real-ip'),
        'forwarded': request_headers.get('forwarded'),
        'host': request_headers.get('host'),
        'user-agent': request_headers.get('user-agent'),
        'accept': request_headers.get('accept'),
        'accept-encoding': request_headers.get('accept-encoding')
    })
