CREATE KEYSPACE IF NOT EXISTS cassandra_sample WITH REPLICATION = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

CREATE TABLE IF NOT EXISTS cassandra_sample.logs (
                         id text PRIMARY KEY,
                         data text,
                         update_time timestamp
) WITH default_time_to_live = 31536000;

CREATE TABLE IF NOT EXISTS cassandra_sample.access_logs (
                         ip text,
                         url text,
                         request_headers text,
                         request_body text,
                         method text,
                         update_time timestamp,
                         PRIMARY KEY (ip, update_time)
) WITH CLUSTERING ORDER BY (update_time DESC)
 AND default_time_to_live = 31536000;

INSERT INTO cassandra_sample.logs (id, data, update_time)
 VALUES('test_id', '{"test": "data"}', toTimeStamp(now()));