#!/usr/bin/env sh
set -e

# Wait for MySQL
if [ -n "$DATABASE_URL" ]; then
  echo "Waiting for MySQL..."
  until nc -z mysql 3306; do
    sleep 1
  done
  echo "MySQL is up"
fi

# Wait for Redis
if [ -n "$REDIS_URL" ]; then
  echo "Waiting for Redis..."
  until nc -z redis 6379; do
    sleep 1
  done
  echo "Redis is up"
fi

BOT_MODE=${BOT_MODE:-polling}

if [ "$BOT_MODE" = "webhook" ]; then
  echo "Starting bot in webhook mode on :8080"
  exec uvicorn src.main:app --host 0.0.0.0 --port 8080
else
  echo "Starting bot in polling mode"
  exec python -m src.bot
fi

