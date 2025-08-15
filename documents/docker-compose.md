### docker-compose

**Summary (EN)**
- Orchestrates 3 services: `bot` (Python/aiogram), `postgres`, `redis`.
- Uses one network `backend`, persistent volumes for DB/Redis, healthchecks, `.env` file.

**خلاصه (FA)**
- سه سرویس را مدیریت می‌کند: `bot`، `postgres`، `redis`.
- نتورک مشترک `backend`، ولوم‌های پایدار برای DB/Redis، هلس‌چک و استفاده از `.env`.

## Services
- **bot**: builds from `docker/bot/Dockerfile`, exposes 8080, depends on healthy DB/Redis. Modes: polling/webhook via `BOT_MODE`.
- ~~postgres~~ → **mysql**: builds from `docker/mysql/Dockerfile`, healthcheck with `mysqladmin ping`, volume `mysql_data`.
- **redis**: builds from `docker/redis/Dockerfile`, AOF enabled, volume `redis_data`.

## Networking / نتورک
- Single user-defined network `backend` for internal service discovery.

## Volumes / ولوم‌ها
- `./data/mysql_data` → `/var/lib/mysql` (bind mount)
- `./data/redis_data` → `/data` (bind mount)

## Healthchecks / هلس‌چک
- Postgres: `pg_isready`
- Redis: `redis-cli ping`

## Environment / محیط
- `.env` is loaded and key vars are passed explicitly (see `documents/env.md`).

