### .env Reference

Keys and defaults used by `docker-compose.yml` and images.

| Key | Default | Notes |
|---|---|---|
| `COMPOSE_PROJECT_NAME` | `nashenasbot` | Compose project name |
| `TZ` | `UTC` | Container timezone |
| `BOT_MODE` | `polling` | `polling` or `webhook` |
| `BOT_WEBHOOK_PORT` | `8080` | Published by compose |
| `TELEGRAM_BOT_TOKEN` | — | Required |
| `TELEGRAM_WEBHOOK_URL` | — | Webhook mode |
| `TELEGRAM_WEBHOOK_SECRET` | — | Webhook mode |
| `DATABASE_NAME` | `nashenas` | DB name |
| `DATABASE_USER` | `root` | DB user |
| `DATABASE_PASSWORD` | `root` | DB password |
| `DATABASE_HOST` | `mysql` | Service name in network |
| `DATABASE_PORT` | `3306` | Port |
| `DATABASE_URL` | `mysql+pymysql://root:root@mysql:3306/nashenas` | Full DSN |
| `REDIS_URL` | `redis://redis:6379/0` | Redis DSN |

Notes / نکات:
- In compose, `DATABASE_URL` and `REDIS_URL` are passed directly to `bot`.
- در compose، `DATABASE_URL` و `REDIS_URL` مستقیم به سرویس `bot` داده می‌شوند.

