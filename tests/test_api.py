import pytest

from app import create_app
from extensions import db
from models import Note, User


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SECRET_KEY": "test-secret-key-for-unit-tests",
            "JWT_SECRET_KEY": "test-jwt-secret-key-for-unit-tests",
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def signup(client, username):
    response = client.post(
        "/signup",
        json={
            "username": username,
            "password": "password123",
            "password_confirmation": "password123",
        },
    )
    assert response.status_code == 201
    return response.get_json()


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_signup_hashes_password_and_me_requires_and_accepts_token(app, client):
    result = signup(client, "alice")

    with app.app_context():
        user = User.query.filter_by(username="alice").one()
        assert user.password_digest != "password123"
        assert user.check_password("password123")

    assert client.get("/me").status_code == 401
    response = client.get("/me", headers=auth_headers(result["token"]))
    assert response.status_code == 200
    assert response.get_json() == result["user"]


def test_signup_rejects_duplicate_username_and_invalid_password(client):
    signup(client, "alice")

    duplicate = client.post(
        "/signup",
        json={
            "username": "alice",
            "password": "password123",
            "password_confirmation": "password123",
        },
    )
    assert duplicate.status_code == 400
    assert "Username has already been taken." in duplicate.get_json()["errors"]

    invalid = client.post(
        "/signup",
        json={
            "username": "bob",
            "password": "short",
            "password_confirmation": "short",
        },
    )
    assert invalid.status_code == 400


def test_login_returns_token_for_valid_credentials(client):
    signup(client, "alice")

    response = client.post(
        "/login", json={"username": "alice", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.get_json()["user"]["username"] == "alice"

    rejected = client.post(
        "/login", json={"username": "alice", "password": "wrong-password"}
    )
    assert rejected.status_code == 401


def test_notes_crud_and_user_ownership(app, client):
    alice = signup(client, "alice")
    bob = signup(client, "bob")

    created = client.post(
        "/notes",
        headers=auth_headers(alice["token"]),
        json={"title": "First note", "content": "Private content", "mood": "focused"},
    )
    assert created.status_code == 201
    note_id = created.get_json()["id"]
    assert created.get_json()["user_id"] == alice["user"]["id"]

    assert client.get("/notes").status_code == 401
    alice_notes = client.get("/notes", headers=auth_headers(alice["token"]))
    assert [note["id"] for note in alice_notes.get_json()["notes"]] == [note_id]

    assert (
        client.patch(
            f"/notes/{note_id}",
            headers=auth_headers(bob["token"]),
            json={"title": "Stolen"},
        ).status_code
        == 404
    )
    assert (
        client.delete(
            f"/notes/{note_id}", headers=auth_headers(bob["token"])
        ).status_code
        == 404
    )

    updated = client.patch(
        f"/notes/{note_id}",
        headers=auth_headers(alice["token"]),
        json={"title": "Updated", "mood": None},
    )
    assert updated.status_code == 200
    assert updated.get_json()["title"] == "Updated"
    assert updated.get_json()["mood"] is None

    deleted = client.delete(
        f"/notes/{note_id}", headers=auth_headers(alice["token"])
    )
    assert deleted.status_code == 204
    with app.app_context():
        assert db.session.get(Note, note_id) is None


def test_note_pagination_is_limited_to_authenticated_users(app, client):
    alice = signup(client, "alice")
    bob = signup(client, "bob")

    with app.app_context():
        alice_user = User.query.filter_by(username="alice").one()
        bob_user = User.query.filter_by(username="bob").one()
        db.session.add_all(
            [
                Note(title=f"Note {index}", content="Body", user_id=alice_user.id)
                for index in range(3)
            ]
            + [Note(title="Bob's note", content="Private", user_id=bob_user.id)]
        )
        db.session.commit()

    response = client.get(
        "/notes?page=2&per_page=2", headers=auth_headers(alice["token"])
    )
    assert response.status_code == 200
    assert response.get_json()["page"] == 2
    assert response.get_json()["per_page"] == 2
    assert response.get_json()["total"] == 3
    assert len(response.get_json()["notes"]) == 1


@pytest.mark.parametrize(
    ("query", "status"),
    [
        ("?page=abc", 400),
        ("?page=0", 400),
        ("?per_page=101", 400),
    ],
)
def test_invalid_pagination_returns_bad_request(client, query, status):
    token = signup(client, "alice")["token"]
    response = client.get(f"/notes{query}", headers=auth_headers(token))
    assert response.status_code == status


def test_malformed_or_invalid_json_is_rejected(client):
    assert client.post("/signup", json=[]).status_code == 400
    token = signup(client, "alice")["token"]
    response = client.post(
        "/notes", headers=auth_headers(token), json={"title": " ", "content": ""}
    )
    assert response.status_code == 400
