FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_DEBUG=false \
    PORT=8000 \
    GUNICORN_WORKERS=2 \
    GUNICORN_THREADS=4 \
    GUNICORN_TIMEOUT=60

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.6.17 /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY . .

RUN useradd --create-home --home-dir /home/appuser --shell /usr/sbin/nologin appuser \
    && mkdir -p /app/staticfiles /app/media \
    && chmod +x /app/docker-entrypoint.sh \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
