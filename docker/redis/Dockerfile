FROM redis:7-alpine

COPY docker/redis/redis.conf /usr/local/etc/redis/redis.conf
COPY docker/redis/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]

