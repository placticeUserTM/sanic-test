#!/bin/bash

set -e

host="$1"
shift
cs_host="$1"
shift
cmd="$@"

echo "Waiting for mysql"
until mysqladmin ping -h "$host" --silent; do
  echo 'Waiting for mysqld to be connectable...'
  sleep 2
done

>&2 echo "MySQL is up \nWaiting for cassandra \nWaiting for cassandra to be connectable..."

timeout 60 sh -c 'until nc -z $0 $1; do sleep 1; done' $cs_host 9042

>&2 echo "Cassandra is up executing command"

exec $cmd