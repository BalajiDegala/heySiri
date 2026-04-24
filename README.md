# heySiri

Django website for team planning, findings, and activity tracking.

## Run with uv

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py collectstatic --noinput
DJANGO_DEBUG=false DJANGO_ALLOWED_HOSTS='localhost,127.0.0.1,0.0.0.0' DJANGO_SECRET_KEY='replace-me' uv run gunicorn heysiri.wsgi:application --bind 0.0.0.0:8000
```

Open http://127.0.0.1:8000/ and log in with the team password configured in `core/views.py`.

For a real public HTTPS deployment, set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and `DJANGO_CSRF_TRUSTED_ORIGINS` in the environment. Also enable `DJANGO_SECURE_SSL_REDIRECT`, `DJANGO_SESSION_COOKIE_SECURE`, `DJANGO_CSRF_COOKIE_SECURE`, and a positive `DJANGO_SECURE_HSTS_SECONDS` value once TLS is configured.
