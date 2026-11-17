# 💰 Financial Controller App — Shared financial planning API

![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-psycopg2-4169E1?logo=postgresql&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Status](https://img.shields.io/badge/status-in%20progress-yellow)

> A REST API for **shared** financial planning. Several users (a couple, a family, a group of friends) share the same plan and record income, expenses and categories in it, with JWT authentication, Pydantic validation and history preserved through *soft delete*. A React front-end is in early development.

📄 [Versão em português](README.md)

---

## 📑 Table of contents

1. [What the API does](#-what-the-api-does)
2. [Implementation status](#-implementation-status)
3. [Architecture](#️-architecture)
4. [Tech stack](#-tech-stack)
5. [Repository structure](#️-repository-structure)
6. [Data model](#️-data-model)
7. [Business rules](#-business-rules)
8. [Input validation](#-input-validation)
9. [Endpoints](#-endpoints)
10. [Response and error format](#-response-and-error-format)
11. [How to run](#️-how-to-run)
12. [Front-end](#️-front-end)
13. [Tests](#-tests)
14. [Known limitations](#️-known-limitations)
15. [Roadmap](#️-roadmap)
16. [License](#-license)

---

## ✨ What the API does

- 🔐 **JWT authentication:** sign-up, login, renewing the *access token* with a *refresh token*, and fetching the authenticated user (`/auth/me`).
- 🔑 **Protected passwords:** passwords are stored only as a **bcrypt** hash, and sign-up requires a strong password.
- 👥 **Shared plans (*plannings*):** each planning has several members (a many-to-many relationship between users and plannings). The creator is always added as a member.
- 🛡️ **Membership-based authorization:** a user can only view, change or remove plannings, transactions and categories of plannings they are a member of.
- 💸 **Transactions:** income and expenses with title, description, amount, category, due date and payment date. The response tells whether the bill is paid (`is_paid`).
- 🏷️ **Categories:** each planning has its own categories, with a color, and can also use **global** categories shared by everyone.
- 🔎 **Search:** the planning and transaction lists accept a `search` parameter, which looks for the term in the name, title or description, case-insensitively.
- 📄 **Pagination:** the planning and transaction lists are paginated (`page` and `per_page`) and return pagination metadata.
- 🕵️ **Audit trail:** plannings, transactions and categories record who created them (`created_by`), who changed them last (`updated_by`) and when (`created_at`, `updated_at`, `deleted_at`).
- 🗑️ **Soft delete:** removed records are only flagged with `is_deleted = true` and `deleted_at`. Nothing is actually deleted, which preserves the financial history.
- 📦 **Standardized responses:** responses go through Pydantic schemas, and errors follow a single format, translated from typed exceptions into HTTP status codes.

---

## 🚦 Implementation status

| Feature | Model | Service | HTTP route |
|---|:-:|:-:|:-:|
| Sign-up, login, refresh and `/me` | ✅ | ✅ | ✅ |
| Plannings: create, get, list with search, update and remove | ✅ | ✅ | ✅ |
| Transactions: create, get, list with search, update and remove | ✅ | ✅ | ✅ |
| Planning categories: create, get, update and remove | ✅ | ✅ | ✅ |
| Categories: list | ✅ | ✅ | ⚠️ the route exists but returns 500 |
| Global categories: create, change and remove through the API | ✅ | — | ❌ database only |
| Plannings: change the member list | ✅ | ✅ | ⚠️ the schema does not match the service |
| User removal | soft delete columns exist | ❌ | ❌ |

The React front-end is in its early stages (see [Front-end](#️-front-end)).

---

## 🏗️ Architecture

The application follows a **layered architecture**, built with Flask's *application factory* pattern (`create_app` in `app.py`).

```mermaid
flowchart LR
    C[HTTP client] --> R[Routes<br/>Flask blueprints]
    R -->|validates input| V[Validators<br/>Pydantic schemas]
    R --> S[Services<br/>business rules and authorization]
    S --> M[Models<br/>SQLAlchemy]
    M --> DB[(PostgreSQL)]
    S -. raise typed exceptions .-> H[Global error handlers]
    H -->|HTTP status + JSON| C
```

| Layer | Folder | Responsibility |
|---|---|---|
| **Routes** | `routes/` | Receive the request, require the JWT, validate the body with Pydantic, call the service and build the response. |
| **Validators** | `validators/` | Pydantic schemas for input (field rules) and output (response format). |
| **Services** | `services/` | Business rules and access checks. They do not depend on HTTP and raise typed exceptions (`NotFoundError`, `ForbiddenError` and so on). |
| **Models** | `models/` | Entities and relationships with SQLAlchemy. |
| **Server** | `server/` | Extension instances (`db`, `bcrypt`, `jwt_manager`, `migrate`) and global error handlers. |
| **Utils** | `utils/` | Domain exceptions, error format, pagination metadata and the database transaction context manager. |

**Design principles:**

- **Services know nothing about HTTP.** They raise exceptions from `utils/exceptions.py`, and each one carries its `status_code`. The global handler in `server/errors_handllers.py` turns the exception into a JSON response.
- **Explicit database transactions.** Every write runs inside `db_transaction()` (`utils/context_manager.py`), which commits on success and rolls back on any error.
- **Output is always validated.** Routes build the response with a Pydantic schema before serializing it. Because of that, sensitive fields (such as `password_hash`) never leave in a response.

---

## 🧱 Tech stack

| Technology | Use |
|---|---|
| **Python 3.14** | Language (`.python-version` and `requires-python >= 3.14`) |
| **Flask 3.1** | Web framework and blueprints |
| **Flask-SQLAlchemy / SQLAlchemy 2.0** | ORM |
| **PostgreSQL + psycopg2-binary** | Database |
| **Flask-Migrate (Alembic)** | Database migrations |
| **Pydantic v2** (+ `email-validator`) | Input validation and output formatting |
| **Flask-JWT-Extended** | Access and refresh tokens |
| **Flask-Bcrypt** | Password hashing |
| **python-dotenv** | Loading the `.env` file |
| **pytest** | Tests |
| **uv** | Environment management (`pyproject.toml` and `uv.lock`) |
| **React 19 + TypeScript + Vite + Tailwind CSS** | Front-end (early stage) |

---

## 🗂️ Repository structure

```
financial_controller_app/
├── app.py                         # create_app(): configuration, extensions, handlers and blueprints
├── server/
│   ├── extensions.py              # db, bcrypt, jwt_manager, migrate
│   └── errors_handllers.py        # turns exceptions into JSON responses
├── models/
│   ├── auth_models/user_models/user_model.py                 # User
│   └── buisness_models/
│       ├── planning_models/planning.py                       # Planning + planning_users table
│       ├── categories_models/categories.py                   # Category
│       └── transactions_models/transactions.py               # Transaction
├── routes/
│   ├── auth/auth_routes.py                                   # /auth/*
│   └── business/
│       ├── planning/planning_routes.py                       # /plannings
│       ├── categories/categories_routes.py                   # /plannings/<id>/categories
│       └── transactions/transactions_routes.py               # /plannings/.../transactions
├── services/
│   ├── auth/auth_service.py
│   └── business/
│       ├── planning/planning_service.py
│       ├── categories/categories_service.py
│       └── transactions/transactions_service.py
├── validators/                    # Pydantic input and response schemas
│   ├── auth/ (register, login, getter, error)
│   └── buisness/ (planning, categories, transactions)
├── utils/
│   ├── exceptions.py              # AppException and subclasses with HTTP status
│   ├── error.py                   # AppError: standard error format
│   ├── context_manager.py         # db_transaction(): commit / rollback
│   └── schemas/pagination.py      # PaginationMeta
├── migrations/                    # Alembic (Flask-Migrate)
├── tests/
│   ├── auth/auth_test.py
│   └── business/
│       ├── planning_test.py
│       └── transactions_test.py
├── static/
│   └── fin-point-pen-front-end/   # React + Vite front-end (early stage)
├── pyproject.toml / uv.lock       # dependencies (uv)
├── requirements.txt               # dependencies (pip)
└── pytest.ini
```

---

## 🗄️ Data model

All primary keys are **UUID4 values in hexadecimal format** (`String(32)`), generated by the application.

```mermaid
erDiagram
    users ||--o{ planning_users : "belongs to"
    plannings ||--o{ planning_users : "has members"
    plannings ||--o{ transactions : "contains"
    plannings |o--o{ categories : "own categories"
    categories ||--o{ transactions : "classifies"
    users ||--o{ transactions : "created_by / updated_by"

    users {
        string id PK
        string name
        string email UK
        string password_hash
        bool is_deleted
        timestamptz deleted_at
    }
    plannings {
        string id PK
        string name
        string description
        string created_by FK
        string updated_by FK
        bool is_deleted
        timestamptz created_at
        timestamptz updated_at
        timestamptz deleted_at
    }
    planning_users {
        string user_id PK
        string planning_id PK
    }
    categories {
        string id PK
        string name
        string color
        string planning_id FK "null = global category"
        string created_by FK
        string updated_by FK
        bool is_deleted
        timestamptz created_at
        timestamptz updated_at
        timestamptz deleted_at
    }
    transactions {
        string id PK
        string title
        string description
        string category_id FK
        string type "despesa or receita"
        numeric value "NUMERIC(20,2)"
        date due_date
        date paid_at "null = not paid"
        string planning_id FK
        string created_by FK
        string updated_by FK
        bool is_deleted
        timestamptz created_at
        timestamptz updated_at
        timestamptz deleted_at
    }
```

| Table | Description |
|---|---|
| `users` | Application users. The email is unique. The password is stored only as a bcrypt hash. |
| `plannings` | Shared financial plans. |
| `planning_users` | Association table between users and plannings, with a composite primary key. |
| `categories` | Transaction categories. With a null `planning_id`, the category is **global**. The `(name, planning_id)` pair is unique (`uq_category_name_planning`). |
| `transactions` | Income and expenses of a planning. The amount uses `NUMERIC(20,2)`, which avoids floating-point errors. |

---

## 📐 Business rules

### Authentication

- Sign-up rejects emails that are already registered (**409 Conflict**).
- Login with an unknown email or a wrong password returns the same message, `Credenciais Inválidas.` (**401**), without revealing which one failed.
- The *access token* expires in **1 hour** and the *refresh token* in **30 days**. The token identity is the user's `id`.
- `POST /auth/refresh` only accepts the *refresh token*. With an *access token*, the response is **422**.

### Plannings

- **Creation:** `members` is a list of user IDs. If any ID does not exist, the response is **404**. The creator is added as a member automatically.
- **Access:** before getting, changing or removing a planning, the service checks, in this order, that:
  1. the planning exists (otherwise **404**);
  2. the planning has not been removed (otherwise **409**);
  3. the user is a member (otherwise **403**).
- **Update:** partial (`PATCH`). Only the fields sent are changed, and `updated_by` becomes the requesting user.
- **Removal:** *soft delete*. The service sets `is_deleted`, `deleted_at` and `updated_by`.
- **Listing:** returns only the non-removed plannings the user is a member of, newest first, with pagination (`page` defaults to 1, `per_page` defaults to 20). The `search` parameter filters by name or description.
- **Response:** includes the members, the creator (`creator`) and the user who last changed the planning (`updater`).

### Transactions

- The user must be a member of the transaction's planning.
- The category must exist and be either **global** or **from the same planning**. Otherwise the response is **404** (unknown category) or **401** (category from another planning).
- `type` only accepts `despesa` (expense) or `receita` (income), and `value` must be greater than zero, with up to 2 decimal places.
- **Payment:** a bill is paid when `paid_at` is set. On creation, `is_paid` and `paid_at` must be consistent, and an inconsistent pair returns **409**. The `is_paid` value sent is not stored. In the response, `is_paid` is computed from `paid_at`.
- **Update:** partial. If `category_id` changes, the new category goes through the same checks.
- **Removal:** *soft delete*. Removing a transaction that was already removed returns **409**.
- **Listing:** returns the planning's non-removed transactions, latest due date first, with pagination. The `search` parameter filters by title or description.

### Categories

- **Creation:** a category is always created inside the planning given in the URL. The name is unique within the planning (**409** if repeated).
- **Get:** returns the category if it is global or belongs to the planning and has not been removed. Otherwise **404**.
- **Update:** partial, and only for the planning's own categories. A global category or one from another planning returns **401**, and a repeated name returns **409**.
- **Removal:** *soft delete*, only for the planning's own categories (**404** for a global category or one from another planning). Removing it again returns **409**.
- **Listing (service):** combines the **global** categories and the planning's **own** categories, sorted by name, with an optional name filter. The matching route still fails (see the [known limitations](#️-known-limitations)).
- **Global categories** (null `planning_id`) cannot be created, changed or removed through the API. They are inserted directly into the database.

---

## ✅ Input validation

| Schema | Rules |
|---|---|
| **Sign-up** (`RegisterSchema`) | `name`: 2 to 50 characters, letters (accented letters included) and spaces only. Extra spaces are removed and the name is stored in *Title Case* (`ana  silva` → `Ana Silva`). `email`: valid email, up to 100 characters. `password`: at least 8 characters, with at least one uppercase letter, one lowercase letter, one digit and one special character. |
| **Login** (`LoginSchema`) | Valid `email` and a `password` of at least 8 characters. |
| **Create planning** | `name`: 2 to 80 characters. `description`: up to 250, optional. `members`: list of IDs, optional. |
| **Update planning** | `name` (up to 80) and `description` (up to 250), both optional. |
| **Create transaction** | `title`: 2 to 80 characters. `description`: up to 250, optional. `category_id`: required. `value`: decimal greater than 0, up to 2 decimal places. `type`: `despesa` or `receita`. `due_date`: required date. `is_paid`: defaults to `false`. `paid_at`: required when `is_paid = true` and not allowed when `is_paid = false`. |
| **Update transaction** | All fields are optional. If `is_paid = true`, `paid_at` is required. |
| **Create category** | `name`: required, up to 50 characters. `color`: required, 2 to 7 characters (for example `#4CAF50`). The hexadecimal format is not validated. |
| **Update category** | `name` and `color`, both optional. |

The planning, transaction and category schemas strip leading and trailing spaces from text fields.

---

## 📡 Endpoints

Every route except `register` and `login` requires the header:

```
Authorization: Bearer <access_token>
```

> The API messages are in Portuguese.

### Authentication — `/auth`

| Method | Route | Description | Success |
|---|---|---|---|
| `POST` | `/auth/register` | Creates the account and returns `user_id` and `access_token` | 201 |
| `POST` | `/auth/login` | Returns `access_token` and `refresh_token` | 200 |
| `POST` | `/auth/refresh` | Issues a new `access_token` (requires the **refresh token**) | 200 |
| `GET` | `/auth/me` | Authenticated user's data | 200 |

<details>
<summary>Examples</summary>

```http
POST /auth/register
Content-Type: application/json

{ "name": "ana silva", "email": "ana@email.com", "password": "Banana@123" }
```

```json
{
  "message": "Usuário criado com sucesso!",
  "data": { "user_id": "f5f4c174334049f9a9f2a3f5f41f43f1", "access_token": "eyJ..." }
}
```

```http
POST /auth/login
Content-Type: application/json

{ "email": "ana@email.com", "password": "Banana@123" }
```

```json
{
  "message": "Login bem-sucedido",
  "data": { "access_token": "eyJ...", "refresh_token": "eyJ..." }
}
```

`POST /auth/refresh` returns `{ "access_token": "eyJ..." }`.

`GET /auth/me` returns `{ "user_id": "...", "name": "Ana Silva", "email": "ana@email.com" }`.

</details>

### Plannings — `/plannings`

| Method | Route | Description | Success |
|---|---|---|---|
| `POST` | `/plannings` | Creates a planning | 201 |
| `GET` | `/plannings?page=1&per_page=20&search=casa` | Lists the user's plannings (paginated, with search) | 200 |
| `GET` | `/plannings/<planning_id>` | Gets one planning | 200 |
| `PATCH` | `/plannings/<planning_id>` | Updates the name and/or description | 200 |
| `DELETE` | `/plannings/<planning_id>` | Removes it (soft delete) | 200 |

<details>
<summary>Examples</summary>

```http
POST /plannings
Authorization: Bearer <access_token>
Content-Type: application/json

{ "name": "Casa", "description": "Gastos da casa", "members": ["9630f7509cf14d949cc1af77a1d105d1"] }
```

```json
{
  "message": "Planning foi criado com sucesso.",
  "data": {
    "id": "0ab3185724644feca212f26701108d88",
    "name": "Casa",
    "description": "Gastos da casa",
    "members": [
      { "id": "f5f4c174334049f9a9f2a3f5f41f43f1", "name": "Ana Silva" },
      { "id": "9630f7509cf14d949cc1af77a1d105d1", "name": "Bob" }
    ],
    "creator": { "id": "f5f4c174334049f9a9f2a3f5f41f43f1", "name": "Ana Silva" },
    "updater": { "id": "f5f4c174334049f9a9f2a3f5f41f43f1", "name": "Ana Silva" }
  }
}
```

The list (`GET /plannings`) returns `data` as a list and adds `pagination`:

```json
{
  "message": "Plannings encontrados:",
  "data": [ { "id": "...", "name": "Casa", "description": "Gastos da casa", "members": [ ], "creator": { }, "updater": { } } ],
  "pagination": { "page": 1, "per_page": 20, "total": 1, "pages": 1, "has_next": false, "has_prev": false }
}
```

</details>

### Categories — `/plannings/<planning_id>/categories`

| Method | Route | Description | Success |
|---|---|---|---|
| `POST` | `/plannings/<planning_id>/categories` | Creates a category in the planning | 201 |
| `GET` | `/plannings/<planning_id>/categories` | Lists global and planning categories (⚠️ currently returns 500) | 200 |
| `GET` | `/plannings/<planning_id>/categories/<category_id>` | Gets one category | 200 |
| `PATCH` | `/plannings/<planning_id>/categories/<category_id>` | Updates the name and/or color | 200 |
| `DELETE` | `/plannings/<planning_id>/categories/<category_id>` | Removes it (soft delete) | 200 |

<details>
<summary>Examples</summary>

```http
POST /plannings/0ab3185724644feca212f26701108d88/categories
Authorization: Bearer <access_token>
Content-Type: application/json

{ "name": "Mercado", "color": "#4CAF50" }
```

```json
{
  "message": "Categoria criada com sucesso.",
  "data": { "id": "baa538e761d4440690b76e9453c556a4", "name": "Mercado", "color": "#4CAF50" }
}
```

</details>

### Transactions

| Method | Route | Description | Success |
|---|---|---|---|
| `POST` | `/plannings/<planning_id>/transactions` | Creates a transaction in the planning | 201 |
| `GET` | `/plannings/<planning_id>/transactions?page=1&per_page=20&search=mercado` | Lists the planning's transactions (paginated, with search) | 200 |
| `GET` | `/plannings/transactions/<transaction_id>` | Gets one transaction | 200 |
| `PATCH` | `/plannings/transactions/<transaction_id>` | Updates a transaction | 200 |
| `DELETE` | `/plannings/transactions/<transaction_id>` | Removes it (soft delete) | 200 |

> The get, update and removal routes live under `/plannings/transactions/...` because the transactions blueprint uses the `/plannings` prefix.

<details>
<summary>Examples</summary>

```http
POST /plannings/0ab3185724644feca212f26701108d88/transactions
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Supermercado",
  "category_id": "baa538e761d4440690b76e9453c556a4",
  "value": "250.90",
  "type": "despesa",
  "due_date": "2026-11-20",
  "is_paid": false
}
```

```json
{
  "message": "Transação criada com sucesso.",
  "data": {
    "id": "7dc1c3c95b5d49f0a3fb115de13645c7",
    "title": "Supermercado",
    "description": null,
    "value": "250.90",
    "type": "despesa",
    "due_date": "Fri, 20 Nov 2026 00:00:00 GMT",
    "paid_at": null,
    "is_paid": false,
    "creator": { "id": "f5f4c174334049f9a9f2a3f5f41f43f1", "name": "Ana Silva" },
    "updater": { "id": "f5f4c174334049f9a9f2a3f5f41f43f1", "name": "Ana Silva" }
  }
}
```

To mark it as paid:

```http
PATCH /plannings/transactions/7dc1c3c95b5d49f0a3fb115de13645c7
Content-Type: application/json

{ "is_paid": true, "paid_at": "2026-11-18" }
```

The list returns `data` as a list and adds `pagination`, in the same format as the planning list.

</details>

---

## 📦 Response and error format

**Success:** most routes respond with a `message` + `data` envelope. The planning and transaction lists add `pagination`. The exceptions are `POST /auth/refresh` and `GET /auth/me`, which return the object directly.

With the current serialization:
- `value` is returned as a **string** (`"250.90"`), which preserves the decimal precision;
- dates are returned in HTTP format (RFC 1123), for example `"Fri, 20 Nov 2026 00:00:00 GMT"`.

**Error:** every handled failure follows the same format:

```json
{
  "message": "Credenciais Inválidas.",
  "errors": [ { "type": "value_error", "loc": [], "msg": "Credenciais Inválidas.", "input": null } ]
}
```

For validation errors (400), `errors` holds Pydantic's detailed list, with the `type`, `loc`, `msg`, `input` and `ctx` of each invalid field.

| Exception / source | Status |
|---|---|
| `ValidationError` (Pydantic) and `BadRequestError` | 400 |
| `UnauthorizedError` and missing or invalid token | 401 |
| `ForbiddenError` | 403 |
| `NotFoundError` | 404 |
| `ConflictError` (includes inconsistent `is_paid` and `paid_at`) | 409 |
| Wrong token type (e.g. an access token on `/refresh`) | 422 |
| Any other exception | 500 (`"Erro interno do servidor"`, with the error written to the log) |

---

## ▶️ How to run

### Prerequisites

- Python **3.14**
- PostgreSQL
- [uv](https://docs.astral.sh/uv/) (recommended) or `pip`

### 1. Clone the repository

```bash
git clone https://github.com/mAcosOS-banana/financial_controller_app.git
cd financial_controller_app
```

### 2. Install the dependencies

With **uv**:

```bash
uv sync
```

Or with **pip**:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt Flask-Migrate pytest
```

> ⚠️ `Flask-Migrate` is already in `pyproject.toml` but not in `requirements.txt` yet, which is why it appears in the pip command. Without it, neither the application nor the tests start.

### 3. Set the environment variables

Create a `.env` file in the project root (it is already in `.gitignore`):

```env
DATABASE_URI=postgresql://user:password@localhost:5432/finance
SECRET_KEY=<generate with: openssl rand -hex 32>
JWT_SECRET_KEY=<generate with: openssl rand -hex 32>
```

> The database variable is named **`DATABASE_URI`**, not `DATABASE_URL`. Use keys of at least 32 bytes: shorter keys trigger a PyJWT security warning.

### 4. Create the tables

On an **empty** database, `flask db upgrade` still fails: the first migration in the chain (`f3b590e20915`) alters tables that are only created by a later migration (`222f675a9320`). Until the chain is fixed, create the tables from the models and mark the migrations as applied:

```bash
python -c "from app import create_app; from server.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
flask --app app db stamp head
```

On a database that is already at the latest revision, new migrations follow the normal flow (`flask --app app db migrate` / `flask --app app db upgrade`).

### 5. Start the API

```bash
flask --app app run --debug
# or
python app.py
```

The API is available at `http://127.0.0.1:5000`.

### 6. First steps

1. Sign up (`POST /auth/register`) and log in (`POST /auth/login`).
2. Create a planning (`POST /plannings`).
3. Create a category in the planning (`POST /plannings/<planning_id>/categories`).
4. Record transactions (`POST /plannings/<planning_id>/transactions`).

To create a **global** category, available in every planning, insert it directly into the database:

```sql
INSERT INTO categories (id, name, color, planning_id, is_deleted, created_by, updated_by, created_at, updated_at)
VALUES (md5(random()::text), 'Mercado', '#4CAF50', NULL, false, '<user_id>', '<user_id>', now(), now());
```

---

## 🖥️ Front-end

The front-end lives in `static/fin-point-pen-front-end/` and is in early development.

- **Stack:** React 19, TypeScript, Vite, Tailwind CSS and the React Compiler.
- **Current state:** `App.tsx` renders a screen with a navigation bar, input fields and a sample list. The screen does not call the API yet.
- **Missing components:** `App.tsx` imports components from `src/components/` (`NavigationBar`, `InputBox`, `InputTasks`, `GroupTasks`, `TasksList` and `Tasks`), but that folder is not in the repository yet. Without it, the project does not compile.

Once the components are in the repository:

```bash
cd static/fin-point-pen-front-end
npm install
npm run dev
```

---

## 🧪 Tests

```bash
pytest -v
```

- **50 tests** in `tests/auth/auth_test.py` (15), `tests/business/planning_test.py` (13) and `tests/business/transactions_test.py` (22).
- **Authentication:** success, validation errors, already-registered email, invalid credentials and missing, invalid or wrong-type token.
- **Plannings:** create, get, update, remove and list, including resource not found, access denied and already-removed planning.
- **Transactions:** create (invalid type, negative amount, unknown planning, access denied, invalid category), update, remove, get and list (with search and pagination parameters).
- They are HTTP-layer tests. The services are replaced with *mocks* (`unittest.mock.patch`), and the application runs on an **in-memory SQLite** database, without touching the development database.
- **Current result:** all 50 tests pass.
- There are no tests for categories or integration tests for the services yet.

---

## ⚠️ Known limitations

The project is in progress. These are the points where the current behavior still differs from what is expected:

- **The category list returns 500.** The route receives a list from the service but tries to read `pagination.item`. It also reads `page`, `per_page` and `search` without passing them to the service.
- **Removing a category that does not exist returns 500, not 404.** The service reads `category.planning_id` before checking that the category exists.
- **Global categories are database-only.** The API does not create, change or remove categories without a planning.
- **Updating planning members.** `UpdatePlanningSchema` expects `members` as a single object (`id`, `name`, `email`), but the service expects a list of IDs. A list is rejected with 400. In practice, `PATCH` currently only changes the name and description.
- **Overdue bills.** The API tells whether a bill is paid (`is_paid`) but does not compute whether it is overdue. Clients can compare `due_date` with the current date.
- **Sign-up does not return the refresh token.** `register` generates a refresh token but responds only with the access token. Log in to get a refresh token.
- **Flask HTTP errors become 500.** The generic `Exception` handler also catches 404 (unknown route), 405 and 415 (body without `Content-Type: application/json`), which end up as `500 Erro interno do servidor`.
- **Database errors become 500.** `db_transaction()` turns any write failure into a `RuntimeError`.
- **A removed planning returns 409, not 404,** on get, update and removal. Removing a planning also does not flag its transactions as removed.
- **Dependencies and migrations.** `Flask-Migrate` is missing from `requirements.txt`, and the migration chain does not work on an empty database (see [How to run](#️-how-to-run)).
- **Incomplete front-end.** The components imported by `App.tsx` are not in the repository yet.

---

## 🗺️ Roadmap

- [ ] Fix the category list and the removal of a category that does not exist
- [ ] Fix updating planning members
- [ ] Add tests for categories
- [ ] Add `Flask-Migrate` to `requirements.txt` and reorganize the migration chain
- [ ] Finish the React front-end and connect it to the API
- [ ] Email service (sign-up confirmation and password recovery)
- [ ] Email invitations to join a planning
- [ ] Aggregation endpoints for dashboards (spending by day and by category)
- [ ] Recurring bills

---

## 📄 License

Study and portfolio project.
