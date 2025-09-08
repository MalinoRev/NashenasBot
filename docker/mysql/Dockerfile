FROM --platform=linux/amd64 mysql:5.7

ENV MYSQL_DATABASE=${MYSQL_DATABASE} \
    MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD} \
    MYSQL_USER=${MYSQL_USER} \
    MYSQL_PASSWORD=${MYSQL_PASSWORD}

# Copy MySQL configuration for UTF-8 support
COPY docker/mysql/my.cnf /etc/mysql/conf.d/

# Copy initialization scripts
COPY docker/mysql/initdb /docker-entrypoint-initdb.d


