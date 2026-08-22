#!/bin/sh
set -eu

backend_pid=""
nginx_pid=""

cleanup() {
    trap - TERM INT EXIT
    [ -n "$backend_pid" ] && kill -TERM "$backend_pid" 2>/dev/null || true
    [ -n "$nginx_pid" ] && kill -TERM "$nginx_pid" 2>/dev/null || true
    [ -n "$backend_pid" ] && wait "$backend_pid" 2>/dev/null || true
    [ -n "$nginx_pid" ] && wait "$nginx_pid" 2>/dev/null || true
}

trap cleanup TERM INT EXIT

: "${PORT:=10000}"
: "${BACKEND_PATH:=/api}"
: "${MAINTENANCE_MODE:=false}"
export PORT BACKEND_PATH MAINTENANCE_MODE

python -c 'from takdora.config import get_settings; get_settings()'

envsubst '$PORT $MAINTENANCE_MODE' < /app/docker/nginx.conf.template > /tmp/nginx.conf
uv run --no-sync reflex db migrate
uv run --no-sync reflex export --env prod --frontend-only --no-zip
uv run --no-sync reflex run --env prod --backend-only --backend-host 127.0.0.1 --backend-port 8000 &
backend_pid=$!
nginx -c /tmp/nginx.conf -g 'daemon off;' &
nginx_pid=$!

wait "$backend_pid" "$nginx_pid"
