# encode:UTF-8
import os
from datetime import datetime

from sanic.log import logger

from aiocassandra import aiosession
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement, BatchStatement, BatchType


class SanicCassandra:
    def __init__(self, app):
        self.init_app(app=app)

    async def start(self, _app, loop):
        _app.cluster = CassandraCluster()
        _cassandra_session = _app.cluster.connect(loop)

        insert_access_log_query = """
        INSERT INTO cassandra_sample.access_logs
         (ip, url, request_headers, request_body, method, update_time)
          VALUES (?, ?, ?, ?, ?, ?);"""
        insert_many_query = """
        INSERT INTO cassandra_sample.logs (id, data, update_time) VALUES (?, ?, ?);
        """
        prepare_insert_access_log = _cassandra_session\
            .prepare(insert_access_log_query)
        prepare_insert_many = _cassandra_session.prepare(insert_many_query)

        async def _query(cql, args: list = None):
            result = []
            statement = SimpleStatement(cql)

            if args:
                paginator = _cassandra_session.execute_futures(statement, args)
            else:
                paginator = _cassandra_session.execute_futures(statement)

            async with paginator:
                async for row in paginator:
                    result.append(row)
            return result

        async def _pagination(cql, args: list = None, fetch_size=100):
            result = []
            statement = SimpleStatement(cql, fetch_size=fetch_size)

            if args:
                paginator = _cassandra_session.execute_futures(statement, args)
            else:
                paginator = _cassandra_session.execute_futures(statement)

            async with paginator:
                async for row in paginator:
                    result.append(row)
            return result

        async def _execute_query(cql, args: list = None):
            statement = SimpleStatement(cql)
            if args:
                return _cassandra_session.execute(statement, args)
            else:
                return _cassandra_session.execute(statement)

        async def _execute_async_query(cql, args: list = None):
            statement = SimpleStatement(cql)
            if args:
                future = _cassandra_session.execute_async(statement, args)
            else:
                future = _cassandra_session.execute_async(statement)
            future.add_callbacks(handle_success_log, handle_error_log)
            return future

        async def _execute_many(args):
            batch = BatchStatement(BatchType.LOGGED)

            for item in args:
                batch.add(prepare_insert_many, item.get('id'), item.get('data'), datetime.now())
            return _cassandra_session.execute(batch)

        async def _insert_access_log(args):
            query = prepare_insert_access_log.bind(args)
            future = _cassandra_session.execute_async(query)
            future.add_callbacks(handle_success_log, handle_error_log)
            return future

        def handle_success_log(rows):
            logger.info("Success cassandra callback, rows: %s", str(rows))

        def handle_error_log(exception):
            logger.error("Failed cassandra callback, exception: %s", exception)

        setattr(_cassandra_session, 'query', _query)
        setattr(_cassandra_session, 'pagination', _pagination)
        setattr(_cassandra_session, 'execute_query', _execute_query)
        setattr(_cassandra_session, 'execute_async_query', _execute_async_query)
        setattr(_cassandra_session, 'execute_many', _execute_many)
        setattr(_cassandra_session, 'insert_access_log', _insert_access_log)

        _app.cassandra = _cassandra_session

    def init_app(self, app):

        @app.listener('before_server_start')
        async def setup_cassandra_session_listener(_app, loop):
            await self.start(_app, loop)

        @app.listener('after_server_stop')
        async def teardown_cassandra_session_listener(_app, loop):
            logger.info('closing cassandra connection for [pid:{}]'.format(os.getpid()))
            _app.cluster.shutdown()


class CassandraCluster:
    cassandra_cluster = None

    def connect(self, loop):
        self.cassandra_cluster = Cluster(
            [
                os.getenv("CLUSTER_HOST")
            ],
            os.getenv("CASSANDRA_PORT"),
            os.getenv("CASSANDRA_DC")
        )
        key_space = os.getenv("CASSANDRA_KEY_SPACE")
        session = self.cassandra_cluster.connect(key_space)
        metadata = self.cassandra_cluster.metadata
        logger.info('Connected to cluster for [pid:{}]: {}'
                    .format(os.getpid(), metadata.cluster_name))
        aiosession(session, loop=loop)
        return session

    def shutdown(self):
        self.cassandra_cluster.shutdown()
