# encode:UTF-8
from sanic import Sanic
from sanic import Blueprint
from sanic.response import text
from sanic.log import logger
import os

from file_operations.file_operations import bp_file
from mysql_operations.mysql_operations import bp_mysql
from sanic_mysql.core import SanicMysql

bp = Blueprint("test_api")
SANIC_PREFIX = "SANIC_"


@bp.route('/')
async def hello(request):
    logger.info('api initialized.')
    return text("Hello world!")


def create_app():
    sanic_app = Sanic("test_api")
    sanic_app.blueprint(bp)
    sanic_app.blueprint(bp_file)
    sanic_app.blueprint(bp_mysql)
    # app.config.FORWARDED_SECRET = "YOUR SECRET"
    # app.config.PROXIES_COUNT = 1
    # app.config.REAL_IP_HEADER = "X-Real-IP"

    sanic_app.config.update(
        dict(MYSQL=dict(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            db=os.getenv("MYSQL_DATABASE"))
        ))
    SanicMysql(sanic_app)
    return sanic_app


if __name__ == "__main__":
    app = create_app()
    logger.info('api initialized.')
    app.run(host="0.0.0.0", port=8000, workers=os.cpu_count(), access_log=False)
