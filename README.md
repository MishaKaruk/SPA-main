# SPA Comments

Cascading comments app — dZENcode test task, Middle tier.

## Stack

Django 5 · DRF · Channels · Celery · Graphene · Vue 3 · Vite · Tailwind · Postgres · Redis · RabbitMQ · Elasticsearch · Docker.

## Run

```bash
cp .env.example .env
docker compose up --build
```

- App: http://localhost/
- Admin: http://localhost/admin/
- API: http://localhost/api/
- GraphQL: http://localhost/graphql/

Create superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

Wipe every comment, attachment, uploaded file and expired captcha — handy before a demo:

```bash
docker compose exec web python manage.py clear_comments
```

## Layout

```
backend/    Django project (users, comments, core apps)
frontend/   Vue 3 SPA
docker/     Dockerfiles, nginx configs, entrypoint
docs/       task PDF + schema.sql (MySQL dialect, opens in Workbench)
```

## Who can post

Anyone, and there are no accounts. The author is identified by the form itself — User Name, E-mail
and optional Home page are stored on the comment.

A successful post comes back with a signed JWT holding that identity. The page keeps it and sends it
with later comments instead of the three fields, so the visitor fills them once and the server reads
the author from a signature rather than from free-form input. Editing the fields overrides the token
and a new one is issued. A tampered or expired token is ignored — the form simply asks for the
fields again. The lifetime is `IDENTITY_LIFETIME_DAYS`, 30 days by default.

## Caching

Root listings and threads are cached in Redis for 5 minutes. Keys carry a generation counter that
is incremented whenever a comment is created, so a new comment — or a reply, which changes the
reply count shown on its root — drops every cached page at once instead of waiting out the TTL.

## Search

Every new comment is queued to Celery over RabbitMQ and indexed into Elasticsearch there, so a slow
or missing search cluster never delays posting; indexing retries with backoff until it lands. Rebuild
the index by hand with:

```bash
docker compose exec web python manage.py search_index --populate
```

## Endpoints

| Method | Path | |
|---|---|---|
| GET  | `/api/comments/` | roots, `?page`, `?ordering` |
| POST | `/api/comments/` | open; `username` + `email`, or `identity`; plus `captcha_key`, `captcha_value` |
| GET  | `/api/comments/{id}/tree/` | full subtree |
| GET  | `/api/comments/search/` | full-text over Elasticsearch, `?q=` |
| POST | `/api/comments-preview/` | sanitize + render |
| GET  | `/api/captcha/` | new captcha |
| WS   | `/ws/comments/` | root broadcasts |
| WS   | `/ws/comments/{root_id}/` | thread broadcasts |

## Features

- MPTT cascading, LIFO by default, 25/page, sortable by user/email/date.
- Allowed HTML: `<a href title>`, `<code>`, `<i>`, `<strong>`. XHTML validated.
- XSS via bleach+lxml, SQL via ORM only, CSRF, per-IP ratelimit.
- Image uploads auto-resized to 320×240 (client canvas + server Pillow).
- TXT ≤ 100 KB.
- WebSocket push on create (Channels + Redis).
- Celery + RabbitMQ for resize/index.
- GraphQL query for roots and threads.

## Middle tier extras

- Broker: RabbitMQ.
- Search: Elasticsearch.
- Cache: Redis (list cache, channels layer, ratelimit).
- Cloud-ready: env-driven config, health checks, split web/ws/worker processes.

## Sanity check

`docker compose down -v` then re-run "Run" on a clean machine — should come up in one shot.
