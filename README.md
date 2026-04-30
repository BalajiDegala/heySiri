# heySiri

Django website for team findings and discussion tracking.

## Run with uv

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py collectstatic --noinput
DJANGO_DEBUG=false DJANGO_ALLOWED_HOSTS='localhost,127.0.0.1,0.0.0.0' DJANGO_SECRET_KEY='replace-me' uv run gunicorn heysiri.wsgi:application --bind 0.0.0.0:8000
```

Open http://127.0.0.1:8000/ and log in with the team password configured in `core/views.py`.

For a real public HTTPS deployment, set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and `DJANGO_CSRF_TRUSTED_ORIGINS` in the environment. Also enable `DJANGO_SECURE_SSL_REDIRECT`, `DJANGO_SESSION_COOKIE_SECURE`, `DJANGO_CSRF_COOKIE_SECURE`, and a positive `DJANGO_SECURE_HSTS_SECONDS` value once TLS is configured.

## Run with Docker

Build the image:

```bash
docker build -t heysiri:prod .
```

Run it:

```bash
docker run --rm -p 8000:8000 \
  -e DJANGO_SECRET_KEY='replace-me' \
  -e DJANGO_ALLOWED_HOSTS='localhost,127.0.0.1,0.0.0.0' \
  -e DJANGO_CSRF_TRUSTED_ORIGINS='http://localhost:8000,http://127.0.0.1:8000' \
  -v "$(pwd)/data/db.sqlite3:/app/db.sqlite3" \
  -v "$(pwd)/data/media:/app/media" \
  heysiri:prod
```

Notes:

- The container runs `migrate` and `collectstatic` on startup.
- SQLite and uploaded files need persistent storage. Mount `/app/db.sqlite3` for the database file and `/app/media` for uploads, or switch to an external database before a multi-instance deployment.
- Set `DJANGO_DEBUG=false` and a real `DJANGO_SECRET_KEY` in production.
- Tune Gunicorn with `PORT`, `GUNICORN_WORKERS`, `GUNICORN_THREADS`, and `GUNICORN_TIMEOUT` if needed.
