#!/usr/bin/env bash
set -e

case "${1:-web}" in
  web)
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
    python manage.py search_index --create 2>/dev/null || true
    exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
    ;;
  ws)
    exec daphne -b 0.0.0.0 -p 8001 config.asgi:application
    ;;
  worker)
    exec celery -A config worker -l info
    ;;
  beat)
    exec celery -A config beat -l info
    ;;
  *)
    exec "$@"
    ;;
esac
