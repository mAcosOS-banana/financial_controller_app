from unittest.mock import patch, MagicMock
from flask_jwt_extended import create_access_token
from app import create_app
from server.extensions import db
import pytest

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


# ---------- helpers / factories ----------

def fake_planning(id="plan123", name="Casa", description="desc", members = None):
    p = MagicMock()
    p.id = id
    p.name = name
    p.description = description
    p.members = members or []
    return p

def fake_member(id="id123", name="Maria"):
    m = MagicMock()
    m.id = id
    m.name = name
    return m


def auth_header(app, user_id="user123"):
    with app.app_context():
        token = create_access_token(identity=user_id)
    return {"Authorization": f"Bearer {token}"}


# ---------- CREATE ----------

class TestCreatePlanning:

    @patch("routes.business.planning.planning_routes.PlanningService.create")
    def test_create_success(self, mock_create, app, client):
        mock_create.return_value = fake_planning()
        resp = client.post(
            "/plannings",
            json={"name": "Casa", "description": "desc", "members": []},
            headers=auth_header(app),
        )

        print(resp.get_json())
        assert resp.status_code == 201
        assert resp.get_json()["data"]["id"] == "plan123"
        mock_create.assert_called_once()

    @patch("routes.business.planning.planning_routes.PlanningService.create")
    def test_create_success_with_members(self, mock_create, app, client):
        mock_create.return_value = fake_planning(members=[fake_member(id="id123", name="Marcos")])

        resp = client.post(
            "/plannings",
            json={"name": "Casa", "description": "desc", "members": []},
            headers=auth_header(app),
        )

        print(resp.get_json())
        assert resp.status_code == 201
        assert resp.get_json()["data"]["id"] == "plan123"
        assert resp.get_json()["data"]["members"][0]["id"] == "id123"
        mock_create.assert_called_once()

    def test_create_without_token(self, client):
        resp = client.post("/plannings", json={"name": "Casa"})
        assert resp.status_code == 401

    @patch("routes.business.planning.planning_routes.PlanningService.create")
    def test_create_invalid_body(self, mock_create, app, client):
        # name com menos de 2 chars -> ValidationError -> 400 (handler global)
        resp = client.post("/plannings", json={"name": "A"}, headers=auth_header(app))
        assert resp.status_code == 400
        mock_create.assert_not_called()


# ---------- GET ----------

class TestGetPlanning:

    @patch("routes.business.planning.planning_routes.PlanningService.get")
    def test_get_success(self, mock_get, app, client):
        mock_get.return_value = fake_planning()
        resp = client.get("/plannings/plan123", headers=auth_header(app))
        assert resp.status_code == 200
        assert resp.get_json()["data"]["id"] == "plan123"
        mock_get.assert_called_once_with(planning_id="plan123", user_id="user123")

    @patch("routes.business.planning.planning_routes.PlanningService.get")
    def test_get_not_found(self, mock_get, app, client):
        from utils.exceptions import NotFoundError
        mock_get.side_effect = NotFoundError("Planning não encontrado")
        resp = client.get("/plannings/inexistente", headers=auth_header(app))
        assert resp.status_code == 404

    @patch("routes.business.planning.planning_routes.PlanningService.get")
    def test_get_forbidden(self, mock_get, app, client):
        from utils.exceptions import ForbiddenError
        mock_get.side_effect = ForbiddenError("Sem acesso")
        resp = client.get("/plannings/plan123", headers=auth_header(app))
        assert resp.status_code == 403


# ---------- UPDATE ----------

class TestUpdatePlanning:

    @patch("routes.business.planning.planning_routes.PlanningService.update")
    def test_update_success(self, mock_update, app, client):
        mock_update.return_value = fake_planning(name="Novo nome")
        resp = client.patch(
            "/plannings/plan123",
            json={"name": "Novo nome"},
            headers=auth_header(app),
        )
        assert resp.status_code == 200
        assert resp.get_json()["data"]["name"] == "Novo nome"

    @patch("routes.business.planning.planning_routes.PlanningService.update")
    def test_update_not_found(self, mock_update, app, client):
        from utils.exceptions import NotFoundError
        mock_update.side_effect = NotFoundError("Planning não encontrado")
        resp = client.patch(
            "/plannings/x", json={"name": "Novo"}, headers=auth_header(app)
        )
        assert resp.status_code == 404


# ---------- DELETE ----------

class TestDeletePlanning:

    @patch("routes.business.planning.planning_routes.PlanningService.delete")
    def test_delete_success(self, mock_delete, app, client):
        mock_delete.return_value = fake_planning()
        resp = client.delete("/plannings/plan123", headers=auth_header(app))
        assert resp.status_code == 200
        mock_delete.assert_called_once_with(planning_id="plan123", updater_id="user123")

    @patch("routes.business.planning.planning_routes.PlanningService.delete")
    def test_delete_already_deleted(self, mock_delete, app, client):
        from utils.exceptions import ConflictError
        mock_delete.side_effect = ConflictError("Planning já foi excluído")
        resp = client.delete("/plannings/plan123", headers=auth_header(app))
        assert resp.status_code == 409


# ---------- LIST (paginado) ----------

class TestListPlanning:

    @patch("routes.business.planning.planning_routes.PlanningService.list_plannings")
    def test_list_success(self, mock_list, app, client):
        pagination = MagicMock()
        pagination.items = [fake_planning(id="p1"), fake_planning(id="p2")]
        pagination.page = 1
        pagination.total = 2
        pagination.pages = 1
        pagination.has_next = False
        pagination.has_prev = False
        mock_list.return_value = pagination

        resp = client.get("/plannings?page=1&per_page=20", headers=auth_header(app))
        assert resp.status_code == 200
        body = resp.get_json()
        assert len(body["data"]) == 2
        assert body["pagination"]["total"] == 2
        assert body["pagination"]["has_next"] is False

    def test_list_without_token(self, client):
        resp = client.get("/plannings")
        assert resp.status_code == 401