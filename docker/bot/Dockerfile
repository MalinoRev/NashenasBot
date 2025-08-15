FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.3 \
    PYTHONPATH=/app

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python - --version $POETRY_VERSION && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy dependency manifests from app folder if present; fallback to app/requirements.txt
COPY app/pyproject.toml app/poetry.lock* app/requirements.txt* ./

# Prefer pip via requirements.txt; fallback to Poetry if pyproject exists; else minimal set
RUN if [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt; \
    elif [ -f pyproject.toml ]; then \
      poetry config virtualenvs.create false && \
      poetry install --no-interaction --no-ansi --no-root; \
    else \
      pip install --no-cache-dir aiogram[fast] uvicorn psycopg[binary] redis; \
    fi

# Entrypoint
COPY docker/bot/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]

