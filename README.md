# Productivity Notes API

A Flask REST API backend for a personal productivity notes app with JWT authentication.

## Project Description

This API supports user signup, login, and authenticated CRUD operations for user-owned notes. Each note belongs to a specific user, and access is restricted so that users cannot read or modify other users' notes.

## Installation

1. Install pipenv if needed: `pip install pipenv`
2. In the repository root, install dependencies:
   ```bash
   cd /home/shiks/flask-c10-summative-lab-sessions-and-jwt-clients
   pipenv install --dev
   ```

## Database Setup

Create and seed the database:

```bash
pipenv run python seed.py
```

## Running the App

Start the Flask server:

```bash
pipenv run python app.py
```

The API runs at `http://127.0.0.1:5000`.

## Deployment

This project includes a `Procfile` and `requirements.txt` for deployment compatibility.

For Heroku-style deployment:

1. Ensure `Procfile` exists in the repository root.
2. Ensure `requirements.txt` is present.
3. Commit and push the code.
4. On the deployment host, configure environment variables if needed:
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `DATABASE_URL` (optional; defaults to SQLite)
5. Start the app with the platform's process manager.

Example local command:

```bash
heroku local web
```

## Endpoints

- `GET /` - Health check
- `POST /signup` - Create a new user
  - Body: `{ "username": "user1", "password": "password", "password_confirmation": "password" }`
  - Returns: `{ "token": "...", "user": { ... } }`
- `POST /login` - Login existing user
  - Body: `{ "username": "user1", "password": "password" }`
  - Returns: `{ "token": "...", "user": { ... } }`
- `GET /me` - Get current user info
  - Requires header: `Authorization: Bearer <token>`
- `GET /notes` - Get current user's notes with pagination
  - Query params: `page`, `per_page`
- `POST /notes` - Create a new note
  - Body: `{ "title": "...", "content": "...", "mood": "..." }`
- `PATCH /notes/<id>` - Update a note
  - Body may include `title`, `content`, and/or `mood`
- `DELETE /notes/<id>` - Delete a note

## Notes

- Only authenticated users can access `/me` and `/notes` routes.
- Users may only access notes they own.
