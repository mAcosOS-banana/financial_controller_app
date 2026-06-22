
from utils.exceptions import NotFoundError, ForbiddenError, ConflictError, BadRequestError
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

# ---------- factories ----------

def fake_user(id="user123", name="Marcos"):
    u = MagicMock()
    u.id = id
    u.name = name
    return u




def fake_transaction(id="trans123", title="Mercado", value="130.50", type="despesa"):
    t = MagicMock()
    t.id = id
    t.title = title
    t.description = "Compras"
    t.value = value
    t.type = type
    t.due_date = "2026-06-20"
    t.paid_at = None
    t.creator = fake_user()
    t.updater = None
    return t


def auth_header(app, user_id="user123"):
    with app.app_context():
        token = create_access_token(identity=user_id)
    return {"Authorization": f"Bearer {token}"}


ROUTE = "routes.business.transactions.transactions_routes.TransactionsService"


# ---------- CREATE ----------

class TestCreateTransaction:

    @patch(f"{ROUTE}.create")
    def test_create_success(self, mock_create, app, client):
        mock_create.return_value = fake_transaction()
        resp = client.post(
            "/plannings/plan1/transactions",
            json={"title": "Mercado", "value": "130.50", "type": "despesa",
                  "due_date": "2026-06-20", "category_id": "cat1", "is_paid": False},
            headers=auth_header(app),
        )
        assert resp.status_code == 201
        assert resp.get_json()["data"]["id"] == "trans123"

    def test_create_without_token(self, client):
        resp = client.post("/plannings/plan1/transactions", json={"title": "X"})
        assert resp.status_code == 401

    @patch(f"{ROUTE}.create")
    def test_create_invalid_type(self, mock_create, app, client):
        # type fora do Literal["despesa","receita"] -> ValidationError -> 400
        resp = client.post(
            "/plannings/plan1/transactions",
            json={"title": "X", "value": "10", "type": "outro",
                  "due_date": "2026-06-20", "category_id": "cat1"},
            headers=auth_header(app),
        )
        assert resp.status_code == 400
        mock_create.assert_not_called()

    @patch(f"{ROUTE}.create")
    def test_create_negative_value(self, mock_create, app, client):
        # se o schema usa gt=0, valor negativo -> 400
        resp = client.post(
            "/plannings/plan1/transactions",
            json={"title": "X", "value": "-50", "type": "despesa",
                  "due_date": "2026-06-20", "category_id": "cat1"},
            headers=auth_header(app),
        )
        assert resp.status_code == 400

    @patch(f"{ROUTE}.create")
    def test_create_planning_not_found(self, mock_create, app, client):
        mock_create.side_effect = NotFoundError("Planning não encontrado.")
        resp = client.post(
            "/plannings/inexistente/transactions",
            json={"title": "Xix", "value": "10", "type": "despesa",
                  "due_date": "2026-06-30", "category_id": "cat1", "is_paid": "false"},
            headers=auth_header(app),
        )
        assert resp.status_code == 404

    @patch(f"{ROUTE}.create")
    def test_create_forbidden(self, mock_create, app, client):
        mock_create.side_effect = ForbiddenError("Sem acesso ao planning")
        resp = client.post(
            "/plannings/plan1/transactions",
            json={"title": "Xix", "value": "10", "type": "despesa",
                  "due_date": "2026-06-20", "category_id": "cat1"},
            headers=auth_header(app),
        )
        assert resp.status_code == 403

    @patch(f"{ROUTE}.create")
    def test_create_category_invalid(self, mock_create, app, client):
        mock_create.side_effect = NotFoundError("Categoria não encontrada")
        resp = client.post(
            "/plannings/plan1/transactions",
            json={"title": "Xix", "value": "10", "type": "despesa",
                  "due_date": "2026-06-20", "category_id": "fake"},
            headers=auth_header(app),
        )
        assert resp.status_code == 404


# ---------- UPDATE ----------

class TestUpdateTransaction:

    @patch(f"{ROUTE}.update")
    def test_update_success(self, mock_update, app, client):
        mock_update.return_value = fake_transaction(value="175.00")
        resp = client.patch(
            "/plannings/transactions/trans123",
            json={"value": "175.00"},
            headers=auth_header(app),
        )
        assert resp.status_code == 200
        assert resp.get_json()["data"]["value"] == "175.00"

    @patch(f"{ROUTE}.update")
    def test_update_not_found(self, mock_update, app, client):
        mock_update.side_effect = NotFoundError("Transação não encontrada")
        resp = client.patch("/plannings/transactions/x", json={"value": "1"},
                            headers=auth_header(app))
        assert resp.status_code == 404

    @patch(f"{ROUTE}.update")
    def test_update_forbidden(self, mock_update, app, client):
        mock_update.side_effect = ForbiddenError("Sem acesso")
        resp = client.patch("/plannings/transactions/trans123", json={"value": "1"},
                            headers=auth_header(app))
        assert resp.status_code == 403

    @patch(f"{ROUTE}.update")
    def test_update_empty_body(self, mock_update, app, client):
        # PATCH sem campos: exclude_unset deixa tudo de fora — service decide
        mock_update.return_value = fake_transaction()
        resp = client.patch("/plannings/transactions/trans123", json={},
                            headers=auth_header(app))
        assert resp.status_code == 200


# ---------- DELETE ----------

class TestDeleteTransaction:

    @patch(f"{ROUTE}.delete")
    def test_delete_success(self, mock_delete, app, client):
        mock_delete.return_value = fake_transaction()
        resp = client.delete("/plannings/transactions/trans123", headers=auth_header(app))
        assert resp.status_code == 200

    @patch(f"{ROUTE}.delete")
    def test_delete_not_found(self, mock_delete, app, client):
        mock_delete.side_effect = NotFoundError("Transação não encontrada")
        resp = client.delete("/plannings/transactions/x", headers=auth_header(app))
        assert resp.status_code == 404

    @patch(f"{ROUTE}.delete")
    def test_delete_already_deleted(self, mock_delete, app, client):
        mock_delete.side_effect = ConflictError("Transação já foi excluída")
        resp = client.delete("/plannings/transactions/trans123", headers=auth_header(app))
        assert resp.status_code == 409


# ---------- GET ----------

class TestGetTransaction:

    @patch(f"{ROUTE}.get")
    def test_get_success(self, mock_get, app, client):
        mock_get.return_value = fake_transaction()
        resp = client.get("/plannings/transactions/trans123", headers=auth_header(app))
        assert resp.status_code == 200
        assert resp.get_json()["data"]["id"] == "trans123"

    @patch(f"{ROUTE}.get")
    def test_get_not_found(self, mock_get, app, client):
        mock_get.side_effect = NotFoundError("Transação não encontrada")
        resp = client.get("/plannings/transactions/x", headers=auth_header(app))
        assert resp.status_code == 404


# ---------- LIST (paginado + search) ----------

class TestListTransactions:

    def _fake_pagination(self, items, total=2):
        p = MagicMock()
        p.items = items
        p.page = 1
        p.total = total
        p.pages = 1
        p.has_next = False
        p.has_prev = False
        return p

    @patch(f"{ROUTE}.list_by_planning")
    def test_list_success(self, mock_list, app, client):
        mock_list.return_value = self._fake_pagination(
            [fake_transaction(id="t1"), fake_transaction(id="t2")]
        )
        resp = client.get("/plannings/plan1/transactions", headers=auth_header(app))
        assert resp.status_code == 200
        body = resp.get_json()
        assert len(body["data"]) == 2
        assert body["pagination"]["total"] == 2

    @patch(f"{ROUTE}.list_by_planning")
    def test_list_empty(self, mock_list, app, client):
        mock_list.return_value = self._fake_pagination([], total=0)
        resp = client.get("/plannings/plan1/transactions", headers=auth_header(app))
        assert resp.status_code == 200
        assert resp.get_json()["data"] == []

    @patch(f"{ROUTE}.list_by_planning")
    def test_list_with_search(self, mock_list, app, client):
        mock_list.return_value = self._fake_pagination([fake_transaction()])
        resp = client.get("/plannings/plan1/transactions?search=merc",
                         headers=auth_header(app))
        assert resp.status_code == 200
        # confirma que o search foi repassado ao service
        _, kwargs = mock_list.call_args
        assert kwargs["search"] == "merc"

    @patch(f"{ROUTE}.list_by_planning")
    def test_list_pagination_params(self, mock_list, app, client):
        mock_list.return_value = self._fake_pagination([])
        resp = client.get("/plannings/plan1/transactions?page=3&per_page=5",
                         headers=auth_header(app))
        assert resp.status_code == 200
        _, kwargs = mock_list.call_args
        assert kwargs["page"] == 3
        assert kwargs["per_page"] == 5

    @patch(f"{ROUTE}.list_by_planning")
    def test_list_forbidden(self, mock_list, app, client):
        mock_list.side_effect = ForbiddenError("Sem acesso")
        resp = client.get("/plannings/plan1/transactions", headers=auth_header(app))
        assert resp.status_code == 403

    def test_list_without_token(self, client):
        resp = client.get("/plannings/plan1/transactions")
        assert resp.status_code == 401