### Bot Service (`docker/bot`)

**EN**
- Base: `python:3.12-slim`. Installs Poetry if `pyproject.toml` exists; else falls back to `requirements.txt`; else installs minimal `aiogram`, `uvicorn`, `psycopg`, `redis`.
- Entrypoint: waits for Postgres/Redis, then runs:
  - Polling: `python -m app.bot`
  - Webhook: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
- Port: 8080 (only used in webhook mode; still exposed for consistency).
- Expects code layout inside container `/app/src`: `bot.py` (polling), `main.py` (ASGI app for webhook).

Volumes (dev): the host `./app` folder is mounted into the container for live code updates:
- `./app:/app` (code under `app/src`)

**FA**
- بیس: `python:3.12-slim`. نصب وابستگی‌ها با Poetry (در صورت وجود)، وگرنه `requirements.txt`، و در نهایت نصب حداقل پکیج‌ها.
- entrypoint: صبر برای Postgres/Redis و سپس اجرا:
  - Polling: `python -m app.bot`
  - Webhook: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
- پورت: 8080 (در webhook استفاده می‌شود).
- ساختار کد مورد انتظار داخل کانتینر `/app/src`: `bot.py` و `main.py`.

ولوم‌ها (dev): پوشه `./app` داخل کانتینر mount می‌شود تا کد زنده به‌روز باشد:
- `./app:/app`

## Environment Vars / متغیرهای محیطی
- `BOT_MODE` (polling|webhook)
- `BOT_WEBHOOK_PORT` (default 8080; mapped in compose)
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBHOOK_URL`, `TELEGRAM_WEBHOOK_SECRET` (webhook only)
- `DATABASE_URL` (e.g., `postgresql://...`)
- `REDIS_URL` (e.g., `redis://.../0`)

