import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from server.extensions import db
from flask_jwt_extended import create_access_token, create_refresh_token

# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # banco em memória
        "JWT_SECRET_KEY": "test-secret",
    })
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


# ─── REGISTER ───────────────────────────────────────────────────────────────
class TestRegister:

    @patch("routes.auth.auth_routes.AuthenticationService.register")
    def test_register_success(self, mock_register, client):
        mock_register.return_value = (fake_user(), "fake.jwt.token")

        resp = client.post("/auth/register", json={
            "name": "João",
            "email": "joao@banana.com",
            "password": "Banana@123",
        })

        print(resp.get_json())
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["user_id"] == "abc123"
        assert data["access_token"] == "fake.jwt.token"
        assert data["message"] == "Usuário criado com sucesso!"

    def test_register_validation_error(self, client):
        # email inválido dispara ValidationError do Pydantic
        resp = client.post("/auth/register", json={
            "name": "João",
            "email": "email_invalido",
            "password": "Banana@123",
        })

        assert resp.status_code == 400
        data = resp.get_json()
        assert "errors" in data
        assert len(data["errors"]) > 0

    @patch("routes.auth.auth_routes.AuthenticationService.register")
    def test_register_email_already_exists(self, mock_register, client):
        # service lança ValueError quando email já existe
        mock_register.side_effect = ValueError("Email ja cadastrado")

        resp = client.post("/auth/register", json={
            "name": "João",
            "email": "joao@banana.com",
            "password": "Banana@123",
        })

        assert resp.status_code == 401
        data = resp.get_json()
        assert data["errors"][0]["msg"] == "Email ja cadastrado"

    def test_register_missing_field(self, client):
        resp = client.post("/auth/register", json={
            "email": "joao@banana.com",
            # name e password faltando
        })

        assert resp.status_code == 400


# ─── LOGIN ────────────────────────────────────────────────────────────────────
class TestLogin:

    @patch("routes.auth.auth_routes.AuthenticationService.login")
    def test_login_success(self, mock_login, client):
        mock_login.return_value = ("access.token", "refresh.token")

        resp = client.post("/auth/login", json={
            "email": "joao@banana.com",
            "password": "Banana@123",
        })

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["access_token"] == "access.token"
        assert data["refresh_token"] == "refresh.token"
        assert data["message"] == "Login bem-sucedido"

    @patch("routes.auth.auth_routes.AuthenticationService.login")
    def test_login_invalid_credentials(self, mock_login, client):
        mock_login.side_effect = ValueError("Credenciais invalidas")

        resp = client.post("/auth/login", json={
            "email": "joao@banana.com",
            "password": "senha_errada",
        })

        assert resp.status_code == 401
        data = resp.get_json()
        assert "errors" in data

    def test_login_validation_error(self, client):
        resp = client.post("/auth/login", json={
            "email": "nao_eh_email",
            "password": "qualquer",
        })

        assert resp.status_code == 400
        data = resp.get_json()
        assert "errors" in data


class TestMe:
 
    @patch("routes.auth.auth_routes.AuthenticationService.me")
    def test_me_success(self, mock_me, app, client):
        # ARRANGE — gera token válido e mocka a busca do usuário
        mock_me.return_value = fake_user()
        with app.app_context():
            token = create_access_token(identity="abc123")
 
        # ACT
        resp = client.get("/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        print(resp.get_json())
        # ASSERT
        assert resp.status_code == 200
        data = resp.get_json()
        
        assert data["user_id"] == "abc123"
        assert data["name"] == "João"
        assert data["email"] == "joao@banana.com"
 
    def test_me_without_token(self, client):
        # sem header Authorization → 401
        resp = client.get("/auth/me")
        assert resp.status_code == 401
 
    def test_me_with_invalid_token(self, client):
        # token malformado → 401/422
        resp = client.get("/auth/me", headers={
            "Authorization": "Bearer token_invalido"
        })
        assert resp.status_code in (401, 422)
 
 
# ─── POST /refresh ──────────────────────────────────────────────────────────
class TestRefresh:
 
    def test_refresh_success(self, app, client):
        # ARRANGE — refresh token válido
        with app.app_context():
            refresh = create_refresh_token(identity="abc123")
 
        # ACT
        resp = client.post("/auth/refresh", headers={
            "Authorization": f"Bearer {refresh}"
        })
 
        # ASSERT — retorna um novo access_token
        assert resp.status_code == 200
        data = resp.get_json()
        assert "access_token" in data
        assert data["access_token"]  # não vazio
 
    def test_refresh_with_access_token_fails(self, app, client):
        # usar access_token onde se espera refresh → 422
        with app.app_context():
            access = create_access_token(identity="abc123")
 
        resp = client.post("/auth/refresh", headers={
            "Authorization": f"Bearer {access}"
        })
        assert resp.status_code == 422
 
    def test_refresh_without_token(self, client):
        resp = client.post("/auth/refresh")
        assert resp.status_code == 401



# ─── EDGE CASES ─────────────────────────────────────────────────────────────
class TestEdgeCases:

    def test_register_empty_body(self, client):
        resp = client.post("/auth/register", json={})
        assert resp.status_code == 400

    def test_login_empty_body(self, client):
        resp = client.post("/auth/login", json={})
        assert resp.status_code == 400


