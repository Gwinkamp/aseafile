#!/bin/bash

set -e

url="http://seafile/api2/ping/"
cmd=$1

echo "Check service for available"

response=$(curl -o /dev/null -s -w "%{http_code}" $url)

while [ "$response" != "200" ]; do
  echo "service is unavailable - sleeping"
  response=$(curl -o /dev/null -s -w "%{http_code}" $url)
  sleep 1
done

sleep 3
echo "healthy"

exec $cmd
