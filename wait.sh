#!/bin/bash

set -e

host="$1"
shift
cmd="$@"

echo "Waiting for mysql"
until mysqladmin ping -h "$host" --silent; do
  echo 'waiting for mysqld to be connectable...'
  sleep 2
done

>&2 echo "MySQL is up - executing command"
exec $cmd