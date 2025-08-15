### MySQL Service (`docker/mysql`)

**EN**
- Base: `mysql:8.4-oracle`.
- Init scripts: `docker/mysql/initdb/*.sql` auto-run on first startup.
- Volume: `mysql_data` persists `/var/lib/mysql`.
- Env: `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD` from `.env`/compose.
- Healthcheck: `mysqladmin ping`.

**FA**
- بیس: `mysql:8.4-oracle`.
- اسکریپت‌های init: در اولین اجرا اعمال می‌شوند.
- ولوم: `mysql_data` برای پایداری داده‌ها.
- متغیرها: از `.env`/compose خوانده می‌شوند.
- هلس‌چک: `mysqladmin ping`.

## Troubleshooting / رفع اشکال

### EN: MySQL 8 auth requires `cryptography`
- Symptom: RuntimeError: 'cryptography' package is required for sha256_password or caching_sha2_password auth methods
- Cause: MySQL 8 default auth plugin (caching_sha2_password) with async driver (`asyncmy`).
- Fix (already applied in this repo): add `cryptography` to app deps and rebuild bot.
  - Rebuild and run:
    ```powershell
    docker compose build bot
    docker compose up -d --force-recreate bot
    docker compose exec -it bot python -m src.core.database.manage create
    ```
- Alternative: switch user auth plugin to `mysql_native_password` (optional):
  ```sql
  ALTER USER 'bot_user'@'%' IDENTIFIED WITH mysql_native_password BY 'YOUR_PASSWORD';
  FLUSH PRIVILEGES;
  ```
- Important: Inside Docker network, use internal service name and port in `DATABASE_URL`:
  - `mysql+asyncmy://USER:PASS@mysql:3306/DBNAME`

### FA: نیاز `cryptography` برای احراز هویت MySQL 8
- خطا: RuntimeError: 'cryptography' package is required for sha256_password or caching_sha2_password
- علت: پلاگین احراز هویت پیش‌فرض MySQL 8 با درایور async.
- راه‌حل (پیاده‌سازی شده): افزودن `cryptography` به وابستگی‌های اپ و rebuild سرویس `bot`.
  - اجرای دستورات:
    ```powershell
    docker compose build bot
    docker compose up -d --force-recreate bot
    docker compose exec -it bot python -m src.core.database.manage create
    ```
- جایگزین: تغییر پلاگین کاربر به `mysql_native_password` (اختیاری):
  ```sql
  ALTER USER 'bot_user'@'%' IDENTIFIED WITH mysql_native_password BY 'YOUR_PASSWORD';
  FLUSH PRIVILEGES;
  ```
- نکته: داخل نتورک داکر از نام سرویس و پورت داخلی استفاده کنید:
  - `mysql+asyncmy://USER:PASS@mysql:3306/DBNAME`

## Database management commands / دستورات مدیریت دیتابیس

### EN
- Create tables:
  ```powershell
  docker compose exec -it bot python -m src.core.database.manage create
  ```
- Seed data (e.g., states):
  ```powershell
  docker compose exec -it bot python -m src.core.database.manage seed
  ```
- Recreate (drop and create):
  ```powershell
  docker compose exec -it bot python -m src.core.database.manage recreate
  ```

### FA
- ساخت جداول:
  ```powershell
  docker compose exec -it bot python -m src.core.database.manage create
  ```
- ریختن سیدها (مثلاً استان‌ها):
  ```powershell
  docker compose exec -it bot python -m src.core.database.manage seed
  ```
- حذف و ساخت مجدد:
  ```powershell
  docker compose exec -it bot python -m src.core.database.manage recreate
  ```


