### Redis Service (`docker/redis`)

**EN**
- Base: `redis:7-alpine`.
- Config: `redis.conf` enables AOF, binds `0.0.0.0`, default `noeviction` policy.
- Entry: simple wrapper then `redis-server /usr/local/etc/redis/redis.conf`.
- Volume: `redis_data` persists `/data`.

**FA**
- بیس: `redis:7-alpine`.
- کانفیگ: AOF فعال، bind روی `0.0.0.0`، policy پیش‌فرض `noeviction`.
- ورود: اجرای `redis-server` با کانفیگ.
- ولوم: `redis_data` برای پایداری داده‌ها.

