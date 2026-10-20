# Productivity Notes API

A Flask REST API for a personal productivity notes app. It uses JWT bearer
tokens for authentication, bcrypt for password hashing, SQLAlchemy for
persistence, and Flask-Migrate for schema changes. Every note is owned by its
creator; authenticated users can only list, view, update, or delete their own
notes.

## Requirements

- Python 3.12 (the version pinned in `Pipfile`)
- Pipenv

## Installation and database setup

From the repository root:

```bash
pip install pipenv
pipenv install
pipenv run flask --app app:create_app db upgrade
pipenv run python seed.py
```

The migration files are included in the repository, so `db init` and
`db migrate` are not needed for a fresh install. The default database is
`app.db` in the repository root. Set `DATABASE_URL` to use another database.
Running the seed script adds three demo users (`user1`, `user2`, and `user3`)
with the password `password`, along with five sample notes per user. Seeding
is safe to repeat and does not erase existing records.

## Run the API

```bash
pipenv run flask --app app:create_app run
```

The development server is available at `http://127.0.0.1:5000`. For local
development, the app generates temporary signing keys at startup. Set stable,
unique `SECRET_KEY` and `JWT_SECRET_KEY` environment variables in any deployed
environment; access tokens expire after one hour.

## Authentication

Signup and login return a JWT in the `token` field. Send it on protected
requests as:

```http
Authorization: Bearer <token>
```

Signup requires a username, a password of at least eight characters, and a
matching `password_confirmation`. Usernames are unique. Passwords are stored
as bcrypt hashes and are never included in API responses.

## API endpoints

| Method | Path | Authentication | Description |
| --- | --- | --- | --- |
| `GET` | `/` | No | Health check |
| `POST` | `/signup` | No | Create an account and return a token. Body: `username`, `password`, `password_confirmation`. |
| `POST` | `/login` | No | Authenticate and return a token. Body: `username`, `password`. |
| `GET` | `/me` | Bearer token | Return the authenticated user's public profile. |
| `GET` | `/notes?page=1&per_page=10` | Bearer token | List only the current user's notes. Page is 1-based and `per_page` must be between 1 and 100. |
| `POST` | `/notes` | Bearer token | Create a note. Body: `title`, `content`, and optional `mood`. The owner is assigned from the token. |
| `PATCH` | `/notes/<id>` | Bearer token | Update one or more of `title`, `content`, and `mood` on an owned note. |
| `DELETE` | `/notes/<id>` | Bearer token | Delete an owned note. Returns `204 No Content`. |

Notes include `id`, `title`, `content`, optional `mood`, and `user_id`.
Requests without a valid token receive `401 Unauthorized`. A note that is
missing or belongs to another user receives `404 Not Found`.

## Tests

Run the API tests with:

```bash
pipenv run python -m pytest
```

The test suite uses an in-memory SQLite database and does not modify the
development database.
