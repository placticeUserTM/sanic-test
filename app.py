# encode:UTF-8
from sanic import Sanic
from sanic import Blueprint
from sanic.response import text
from sanic.log import logger
import os

from src.cassandra_operations.cassandra_operations import bp_cassandra
from src.file_operations.file_operations import bp_file
from src.mysql_operations.mysql_operations import bp_mysql
from src.sanic_cassandra.core import SanicCassandra
from src.sanic_mysql.core import SanicMysql

bp = Blueprint("test_api")


@bp.route('/')
async def hello(request):
    return text("Hello world!")


def create_app():
    sanic_app = Sanic("test_api")
    sanic_app.blueprint(bp)
    sanic_app.blueprint(bp_file)
    sanic_app.blueprint(bp_mysql)
    sanic_app.blueprint(bp_cassandra)
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
    SanicCassandra(sanic_app)
    logger.info('api initialized.')
    return sanic_app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, workers=os.cpu_count(), access_log=False)
