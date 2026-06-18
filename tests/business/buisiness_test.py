import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from server.extensions import db
from flask_jwt_extended import create_access_token, create_refresh_token


# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret",
}   )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ── Helper para criar um mock de User ──────────────────────────────────────────
def fake_user(id="abc123", name="João", email="joao@banana.com"):
    user = MagicMock()
    user.id = id
    user.name = name
    user.email = email
    return user
