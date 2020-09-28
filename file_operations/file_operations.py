# encode:UTF-8
from sanic import Blueprint
from sanic.response import json, file_stream
import os
import aiofiles
import datetime
import glob

bp_file = Blueprint("file_operations")
UPLOADS_DIR = "/tmp/uploads/"


@bp_file.route('/file-upload', methods=['POST'])
async def file_upload(request):

    if "file" not in request.files:
        return json({'message': 'file not exits.'}, status=400)

    file = request.files["file"][0]
    now = datetime.datetime.now()
    today_path = os.path.join(UPLOADS_DIR, now.strftime('%Y%m%d'))
    os.makedirs(today_path, exist_ok=True)

    async with aiofiles.open(os.path.join(today_path, file.name), 'wb') as f:
        await f.write(file.body)
    return json({'message': 'ok'}, status=200)


@bp_file.route('/file-download')
async def file_download(request):
    params = request.json

    if not params or "file_name" not in params:
        return json({'message': 'invalid parameters.'}, status=400)

    file_name = params["file_name"]
    file = glob.glob(UPLOADS_DIR + "**/" + file_name, recursive=True)
    if len(file) < 1:
        return json({'message': 'file not exits.'}, status=400)
    return await file_stream(file[0])
