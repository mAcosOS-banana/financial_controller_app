# 💰 Financial Controller App — API de planejamento financeiro compartilhado

![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-psycopg2-4169E1?logo=postgresql&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Status](https://img.shields.io/badge/status-em%20evolução-yellow)

> API REST para planejamento financeiro **compartilhado**. Vários usuários (um casal, uma família, um grupo de amigos) dividem o mesmo planejamento e registram nele receitas, despesas e categorias, com autenticação JWT, validação com Pydantic e histórico preservado por *soft delete*. Um front-end em React está em início de desenvolvimento.

📄 [English version](README.en.md)

---

## 📑 Sumário

1. [O que a API faz](#-o-que-a-api-faz)
2. [Status de implementação](#-status-de-implementação)
3. [Arquitetura](#️-arquitetura)
4. [Stack](#-stack)
5. [Estrutura do repositório](#️-estrutura-do-repositório)
6. [Modelo de dados](#️-modelo-de-dados)
7. [Regras de negócio](#-regras-de-negócio)
8. [Validações de entrada](#-validações-de-entrada)
9. [Endpoints](#-endpoints)
10. [Formato das respostas e dos erros](#-formato-das-respostas-e-dos-erros)
11. [Como executar](#️-como-executar)
12. [Front-end](#️-front-end)
13. [Testes](#-testes)
14. [Limitações conhecidas](#️-limitações-conhecidas)
15. [Roadmap](#️-roadmap)
16. [Licença](#-licença)

---

## ✨ O que a API faz

- 🔐 **Autenticação com JWT:** cadastro, login, renovação do *access token* com *refresh token* e consulta do usuário autenticado (`/auth/me`).
- 🔑 **Senhas protegidas:** as senhas são armazenadas apenas como hash **bcrypt**, e o cadastro exige uma senha forte.
- 👥 **Planejamentos compartilhados (*plannings*):** cada planejamento tem vários membros (relação muitos-para-muitos entre usuários e plannings). O criador é sempre incluído como membro.
- 🛡️ **Autorização por pertencimento:** um usuário só consegue ver, alterar ou remover plannings, transações e categorias dos plannings dos quais é membro.
- 💸 **Transações:** receitas e despesas com título, descrição, valor, categoria, data de vencimento e data de pagamento. A resposta informa se a conta está paga (`is_paid`).
- 🏷️ **Categorias:** cada planning tem suas próprias categorias, com cor, e também pode usar categorias **globais**, compartilhadas por todos.
- 🔎 **Busca:** as listagens de plannings e de transações aceitam o parâmetro `search`, que procura o termo no nome, no título ou na descrição, sem diferenciar maiúsculas de minúsculas.
- 📄 **Paginação:** as listagens de plannings e de transações são paginadas (`page` e `per_page`) e devolvem os metadados da paginação.
- 🕵️ **Auditoria:** plannings, transações e categorias guardam quem criou (`created_by`), quem alterou por último (`updated_by`) e quando (`created_at`, `updated_at`, `deleted_at`).
- 🗑️ **Soft delete:** os registros removidos são apenas marcados com `is_deleted = true` e `deleted_at`. Nada é apagado de fato, o que preserva o histórico financeiro.
- 📦 **Respostas padronizadas:** as respostas passam por schemas Pydantic e os erros seguem um formato único, traduzido de exceções tipadas para códigos HTTP.

---

## 🚦 Status de implementação

| Recurso | Model | Service | Rota HTTP |
|---|:-:|:-:|:-:|
| Cadastro, login, refresh e `/me` | ✅ | ✅ | ✅ |
| Plannings: criar, detalhar, listar com busca, atualizar e remover | ✅ | ✅ | ✅ |
| Transações: criar, detalhar, listar com busca, atualizar e remover | ✅ | ✅ | ✅ |
| Categorias do planning: criar, detalhar, atualizar e remover | ✅ | ✅ | ✅ |
| Categorias: listar | ✅ | ✅ | ⚠️ a rota existe, mas responde 500 |
| Categorias globais: criar, alterar e remover pela API | ✅ | — | ❌ só direto no banco |
| Plannings: alterar a lista de membros | ✅ | ✅ | ⚠️ o schema não bate com o service |
| Remoção de usuário | colunas de soft delete existem | ❌ | ❌ |

O front-end em React está no início (veja [Front-end](#️-front-end)).

---

## 🏗️ Arquitetura

A aplicação segue uma **arquitetura em camadas**, montada com o padrão *application factory* do Flask (`create_app` em `app.py`).

```mermaid
flowchart LR
    C[Cliente HTTP] --> R[Routes<br/>Blueprints Flask]
    R -->|valida a entrada| V[Validators<br/>schemas Pydantic]
    R --> S[Services<br/>regras de negócio e autorização]
    S --> M[Models<br/>SQLAlchemy]
    M --> DB[(PostgreSQL)]
    S -. lança exceções tipadas .-> H[Error handlers globais]
    H -->|status HTTP + JSON| C
```

| Camada | Pasta | Responsabilidade |
|---|---|---|
| **Routes** | `routes/` | Recebem a requisição, exigem o JWT, validam o corpo com Pydantic, chamam o service e montam a resposta. |
| **Validators** | `validators/` | Schemas Pydantic de entrada (regras de campos) e de saída (formato das respostas). |
| **Services** | `services/` | Regras de negócio e verificação de acesso. Não dependem de HTTP e lançam exceções tipadas (`NotFoundError`, `ForbiddenError` etc.). |
| **Models** | `models/` | Entidades e relacionamentos com SQLAlchemy. |
| **Server** | `server/` | Instâncias das extensões (`db`, `bcrypt`, `jwt_manager`, `migrate`) e handlers globais de erro. |
| **Utils** | `utils/` | Exceções de domínio, formato de erro, metadados de paginação e o context manager de transação do banco. |

**Princípios do desenho:**

- **Os services não conhecem HTTP.** Eles lançam exceções de `utils/exceptions.py`, e cada uma carrega seu `status_code`. O handler global em `server/errors_handllers.py` converte a exceção em resposta JSON.
- **Transações de banco explícitas.** Toda escrita acontece dentro de `db_transaction()` (`utils/context_manager.py`), que faz `commit` no sucesso e `rollback` em qualquer erro.
- **Saída sempre validada.** As rotas montam a resposta com um schema Pydantic antes de serializar. Com isso, campos sensíveis (como `password_hash`) nunca saem na resposta.

---

## 🧱 Stack

| Tecnologia | Uso |
|---|---|
| **Python 3.14** | Linguagem (`.python-version` e `requires-python >= 3.14`) |
| **Flask 3.1** | Framework web e blueprints |
| **Flask-SQLAlchemy / SQLAlchemy 2.0** | ORM |
| **PostgreSQL + psycopg2-binary** | Banco de dados |
| **Flask-Migrate (Alembic)** | Migrations do banco |
| **Pydantic v2** (+ `email-validator`) | Validação de entrada e formatação da saída |
| **Flask-JWT-Extended** | Access token e refresh token |
| **Flask-Bcrypt** | Hash de senhas |
| **python-dotenv** | Leitura do arquivo `.env` |
| **pytest** | Testes |
| **uv** | Gerenciamento do ambiente (`pyproject.toml` e `uv.lock`) |
| **React 19 + TypeScript + Vite + Tailwind CSS** | Front-end (em início) |

---

## 🗂️ Estrutura do repositório

```
financial_controller_app/
├── app.py                         # create_app(): configuração, extensões, handlers e blueprints
├── server/
│   ├── extensions.py              # db, bcrypt, jwt_manager, migrate
│   └── errors_handllers.py        # tradução de exceções em respostas JSON
├── models/
│   ├── auth_models/user_models/user_model.py                 # User
│   └── buisness_models/
│       ├── planning_models/planning.py                       # Planning + tabela planning_users
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
├── validators/                    # schemas Pydantic de entrada e de resposta
│   ├── auth/ (register, login, getter, error)
│   └── buisness/ (planning, categories, transactions)
├── utils/
│   ├── exceptions.py              # AppException e subclasses com status HTTP
│   ├── error.py                   # AppError: formato padronizado de erro
│   ├── context_manager.py         # db_transaction(): commit / rollback
│   └── schemas/pagination.py      # PaginationMeta
├── migrations/                    # Alembic (Flask-Migrate)
├── tests/
│   ├── auth/auth_test.py
│   └── business/
│       ├── planning_test.py
│       └── transactions_test.py
├── static/
│   └── fin-point-pen-front-end/   # front-end em React + Vite (em início)
├── pyproject.toml / uv.lock       # dependências (uv)
├── requirements.txt               # dependências (pip)
└── pytest.ini
```

---

## 🗄️ Modelo de dados

Todas as chaves primárias são **UUID4 em formato hexadecimal** (`String(32)`), geradas pela aplicação.

```mermaid
erDiagram
    users ||--o{ planning_users : "participa"
    plannings ||--o{ planning_users : "tem membros"
    plannings ||--o{ transactions : "contém"
    plannings |o--o{ categories : "categorias próprias"
    categories ||--o{ transactions : "classifica"
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
        string planning_id FK "nulo = categoria global"
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
        string type "despesa ou receita"
        numeric value "NUMERIC(20,2)"
        date due_date
        date paid_at "nulo = não paga"
        string planning_id FK
        string created_by FK
        string updated_by FK
        bool is_deleted
        timestamptz created_at
        timestamptz updated_at
        timestamptz deleted_at
    }
```

| Tabela | Descrição |
|---|---|
| `users` | Usuários da aplicação. O e-mail é único. A senha fica apenas como hash bcrypt. |
| `plannings` | Planejamentos financeiros compartilhados. |
| `planning_users` | Tabela de associação entre usuários e plannings, com chave primária composta. |
| `categories` | Categorias de transação. Com `planning_id` nulo, a categoria é **global**. A combinação `(name, planning_id)` é única (`uq_category_name_planning`). |
| `transactions` | Receitas e despesas de um planning. O valor usa `NUMERIC(20,2)`, o que evita erros de ponto flutuante. |

---

## 📐 Regras de negócio

### Autenticação

- O cadastro recusa e-mails já cadastrados (**409 Conflict**).
- O login com e-mail inexistente ou senha errada devolve a mesma mensagem, `Credenciais Inválidas.` (**401**), sem revelar qual dos dois falhou.
- O *access token* expira em **1 hora**, e o *refresh token* em **30 dias**. A identidade do token é o `id` do usuário.
- `POST /auth/refresh` só aceita o *refresh token*. Com um *access token*, a resposta é **422**.

### Plannings

- **Criação:** `members` é uma lista de IDs de usuários. Se algum ID não existir, a resposta é **404**. O criador é adicionado como membro automaticamente.
- **Acesso:** antes de detalhar, alterar ou remover, o service verifica, nesta ordem:
  1. o planning existe (senão, **404**);
  2. o planning não foi removido (senão, **409**);
  3. o usuário é membro (senão, **403**).
- **Atualização:** parcial (`PATCH`). Só os campos enviados são alterados, e `updated_by` passa a ser o usuário da requisição.
- **Remoção:** *soft delete*. O service marca `is_deleted`, `deleted_at` e `updated_by`.
- **Listagem:** devolve apenas os plannings não removidos dos quais o usuário é membro, do mais recente para o mais antigo, com paginação (`page` padrão 1, `per_page` padrão 20). O parâmetro `search` filtra por nome ou descrição.
- **Resposta:** inclui os membros, o criador (`creator`) e o último usuário que alterou o planning (`updater`).

### Transações

- O usuário precisa ser membro do planning da transação.
- A categoria precisa existir e ser **global** ou **do mesmo planning**. Caso contrário, a resposta é **404** (categoria inexistente) ou **401** (categoria de outro planning).
- `type` aceita apenas `despesa` ou `receita`, e `value` precisa ser maior que zero, com até 2 casas decimais.
- **Pagamento:** a conta paga é a que tem `paid_at` preenchido. Na criação, `is_paid` e `paid_at` precisam ser coerentes, e uma combinação incoerente devolve **409**. O `is_paid` enviado não é gravado. Na resposta, `is_paid` é calculado a partir de `paid_at`.
- **Atualização:** parcial. Se `category_id` mudar, a nova categoria passa pelas mesmas verificações.
- **Remoção:** *soft delete*. Remover de novo uma transação já removida devolve **409**.
- **Listagem:** devolve as transações não removidas do planning, da data de vencimento mais distante para a mais próxima, com paginação. O parâmetro `search` filtra por título ou descrição.

### Categorias

- **Criação:** a categoria é sempre criada dentro do planning informado na URL. O nome é único dentro do planning (**409** se repetir).
- **Detalhe:** devolve a categoria se ela for global ou do planning e não tiver sido removida. Caso contrário, **404**.
- **Atualização:** parcial e só para categorias do próprio planning. Uma categoria global ou de outro planning devolve **401**, e um nome repetido devolve **409**.
- **Remoção:** *soft delete* e só para categorias do próprio planning (**404** se for global ou de outro planning). Remover de novo devolve **409**.
- **Listagem (service):** junta as categorias **globais** e as **do planning**, ordenadas por nome, com filtro opcional por nome. A rota correspondente ainda falha (veja as [limitações](#️-limitações-conhecidas)).
- **Categorias globais** (`planning_id` nulo) não podem ser criadas, alteradas ou removidas pela API. Elas são inseridas direto no banco.

---

## ✅ Validações de entrada

| Schema | Regras |
|---|---|
| **Cadastro** (`RegisterSchema`) | `name`: 2 a 50 caracteres, apenas letras (com acento) e espaços. Espaços extras são removidos e o nome é salvo em *Title Case* (`ana  silva` → `Ana Silva`). `email`: e-mail válido, até 100 caracteres. `password`: mínimo de 8 caracteres, com pelo menos uma letra maiúscula, uma minúscula, um número e um caractere especial. |
| **Login** (`LoginSchema`) | `email` válido e `password` com pelo menos 8 caracteres. |
| **Criar planning** | `name`: 2 a 80 caracteres. `description`: até 250, opcional. `members`: lista de IDs, opcional. |
| **Atualizar planning** | `name` (até 80) e `description` (até 250), ambos opcionais. |
| **Criar transação** | `title`: 2 a 80 caracteres. `description`: até 250, opcional. `category_id`: obrigatório. `value`: decimal maior que 0, até 2 casas. `type`: `despesa` ou `receita`. `due_date`: data obrigatória. `is_paid`: padrão `false`. `paid_at`: obrigatório se `is_paid = true` e proibido se `is_paid = false`. |
| **Atualizar transação** | Todos os campos são opcionais. Se `is_paid = true`, `paid_at` é obrigatório. |
| **Criar categoria** | `name`: obrigatório, até 50 caracteres. `color`: obrigatório, de 2 a 7 caracteres (por exemplo `#4CAF50`). O formato hexadecimal não é validado. |
| **Atualizar categoria** | `name` e `color`, ambos opcionais. |

Os schemas de planning, transação e categoria removem os espaços no início e no fim dos textos.

---

## 📡 Endpoints

Todas as rotas, exceto `register` e `login`, exigem o cabeçalho:

```
Authorization: Bearer <access_token>
```

### Autenticação — `/auth`

| Método | Rota | Descrição | Sucesso |
|---|---|---|---|
| `POST` | `/auth/register` | Cria a conta e devolve `user_id` e `access_token` | 201 |
| `POST` | `/auth/login` | Devolve `access_token` e `refresh_token` | 200 |
| `POST` | `/auth/refresh` | Gera um novo `access_token` (exige o **refresh token**) | 200 |
| `GET` | `/auth/me` | Dados do usuário autenticado | 200 |

<details>
<summary>Exemplos</summary>

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

`POST /auth/refresh` responde `{ "access_token": "eyJ..." }`.

`GET /auth/me` responde `{ "user_id": "...", "name": "Ana Silva", "email": "ana@email.com" }`.

</details>

### Plannings — `/plannings`

| Método | Rota | Descrição | Sucesso |
|---|---|---|---|
| `POST` | `/plannings` | Cria um planning | 201 |
| `GET` | `/plannings?page=1&per_page=20&search=casa` | Lista os plannings do usuário (paginado, com busca) | 200 |
| `GET` | `/plannings/<planning_id>` | Detalha um planning | 200 |
| `PATCH` | `/plannings/<planning_id>` | Atualiza nome e/ou descrição | 200 |
| `DELETE` | `/plannings/<planning_id>` | Remove (soft delete) | 200 |

<details>
<summary>Exemplos</summary>

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

A listagem (`GET /plannings`) devolve `data` como lista e acrescenta `pagination`:

```json
{
  "message": "Plannings encontrados:",
  "data": [ { "id": "...", "name": "Casa", "description": "Gastos da casa", "members": [ ], "creator": { }, "updater": { } } ],
  "pagination": { "page": 1, "per_page": 20, "total": 1, "pages": 1, "has_next": false, "has_prev": false }
}
```

</details>

### Categorias — `/plannings/<planning_id>/categories`

| Método | Rota | Descrição | Sucesso |
|---|---|---|---|
| `POST` | `/plannings/<planning_id>/categories` | Cria uma categoria no planning | 201 |
| `GET` | `/plannings/<planning_id>/categories` | Lista as categorias globais e do planning (⚠️ hoje responde 500) | 200 |
| `GET` | `/plannings/<planning_id>/categories/<category_id>` | Detalha uma categoria | 200 |
| `PATCH` | `/plannings/<planning_id>/categories/<category_id>` | Atualiza nome e/ou cor | 200 |
| `DELETE` | `/plannings/<planning_id>/categories/<category_id>` | Remove (soft delete) | 200 |

<details>
<summary>Exemplos</summary>

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

### Transações

| Método | Rota | Descrição | Sucesso |
|---|---|---|---|
| `POST` | `/plannings/<planning_id>/transactions` | Cria uma transação no planning | 201 |
| `GET` | `/plannings/<planning_id>/transactions?page=1&per_page=20&search=mercado` | Lista as transações do planning (paginado, com busca) | 200 |
| `GET` | `/plannings/transactions/<transaction_id>` | Detalha uma transação | 200 |
| `PATCH` | `/plannings/transactions/<transaction_id>` | Atualiza uma transação | 200 |
| `DELETE` | `/plannings/transactions/<transaction_id>` | Remove (soft delete) | 200 |

> As rotas de detalhe, atualização e remoção ficam sob `/plannings/transactions/...` porque o blueprint de transações usa o prefixo `/plannings`.

<details>
<summary>Exemplos</summary>

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

Para marcar como paga:

```http
PATCH /plannings/transactions/7dc1c3c95b5d49f0a3fb115de13645c7
Content-Type: application/json

{ "is_paid": true, "paid_at": "2026-11-18" }
```

A listagem devolve `data` como lista e acrescenta `pagination`, no mesmo formato da listagem de plannings.

</details>

---

## 📦 Formato das respostas e dos erros

**Sucesso:** a maioria das rotas responde com um envelope `message` + `data`. As listagens de plannings e de transações acrescentam `pagination`. As exceções são `POST /auth/refresh` e `GET /auth/me`, que respondem com o objeto direto.

Na serialização atual:
- `value` sai como **string** (`"250.90"`), o que preserva a precisão do decimal;
- as datas saem no formato HTTP (RFC 1123), por exemplo `"Fri, 20 Nov 2026 00:00:00 GMT"`.

**Erro:** todas as falhas tratadas seguem o mesmo formato:

```json
{
  "message": "Credenciais Inválidas.",
  "errors": [ { "type": "value_error", "loc": [], "msg": "Credenciais Inválidas.", "input": null } ]
}
```

Nos erros de validação (400), `errors` traz a lista detalhada do Pydantic, com `type`, `loc`, `msg`, `input` e `ctx` de cada campo inválido.

| Exceção / origem | Status |
|---|---|
| `ValidationError` (Pydantic) e `BadRequestError` | 400 |
| `UnauthorizedError` e token ausente ou inválido | 401 |
| `ForbiddenError` | 403 |
| `NotFoundError` | 404 |
| `ConflictError` (inclui `is_paid` e `paid_at` incoerentes) | 409 |
| Token do tipo errado (ex.: access token no `/refresh`) | 422 |
| Qualquer outra exceção | 500 (`"Erro interno do servidor"`, com o erro registrado no log) |

---

## ▶️ Como executar

### Pré-requisitos

- Python **3.14**
- PostgreSQL
- [uv](https://docs.astral.sh/uv/) (recomendado) ou `pip`

### 1. Clonar o repositório

```bash
git clone https://github.com/mAcosOS-banana/financial_controller_app.git
cd financial_controller_app
```

### 2. Instalar as dependências

Com **uv**:

```bash
uv sync
```

Ou com **pip**:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt Flask-Migrate pytest
```

> ⚠️ O `Flask-Migrate` já está no `pyproject.toml`, mas ainda não está no `requirements.txt`. Por isso ele aparece no comando do pip. Sem ele, a aplicação e os testes não iniciam.

### 3. Configurar as variáveis de ambiente

Crie um arquivo `.env` na raiz (ele já está no `.gitignore`):

```env
DATABASE_URI=postgresql://usuario:senha@localhost:5432/finance
SECRET_KEY=<gere com: openssl rand -hex 32>
JWT_SECRET_KEY=<gere com: openssl rand -hex 32>
```

> A variável do banco se chama **`DATABASE_URI`**, e não `DATABASE_URL`. Use chaves de pelo menos 32 bytes: chaves menores geram um aviso de segurança do PyJWT.

### 4. Criar as tabelas

Em um banco **vazio**, o `flask db upgrade` ainda falha: a primeira migration da cadeia (`f3b590e20915`) altera tabelas que só são criadas em uma migration posterior (`222f675a9320`). Até a cadeia ser corrigida, crie as tabelas a partir dos models e marque as migrations como aplicadas:

```bash
python -c "from app import create_app; from server.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
flask --app app db stamp head
```

Em um banco que já está na versão mais recente, as próximas migrations seguem o fluxo normal (`flask --app app db migrate` / `flask --app app db upgrade`).

### 5. Subir a API

```bash
flask --app app run --debug
# ou
python app.py
```

A API fica disponível em `http://127.0.0.1:5000`.

### 6. Primeiros passos

1. Cadastre-se (`POST /auth/register`) e faça login (`POST /auth/login`).
2. Crie um planning (`POST /plannings`).
3. Crie uma categoria no planning (`POST /plannings/<planning_id>/categories`).
4. Registre transações (`POST /plannings/<planning_id>/transactions`).

Para criar uma categoria **global**, disponível em todos os plannings, insira-a direto no banco:

```sql
INSERT INTO categories (id, name, color, planning_id, is_deleted, created_by, updated_by, created_at, updated_at)
VALUES (md5(random()::text), 'Mercado', '#4CAF50', NULL, false, '<user_id>', '<user_id>', now(), now());
```

---

## 🖥️ Front-end

O front-end fica em `static/fin-point-pen-front-end/` e está no início do desenvolvimento.

- **Stack:** React 19, TypeScript, Vite, Tailwind CSS e React Compiler.
- **Estado atual:** `App.tsx` monta uma tela com barra de navegação, campos de entrada e uma lista de exemplo. A tela ainda não chama a API.
- **Componentes faltando:** `App.tsx` importa componentes de `src/components/` (`NavigationBar`, `InputBox`, `InputTasks`, `GroupTasks`, `TasksList` e `Tasks`), mas essa pasta ainda não está no repositório. Sem ela, o projeto não compila.

Quando os componentes estiverem no repositório:

```bash
cd static/fin-point-pen-front-end
npm install
npm run dev
```

---

## 🧪 Testes

```bash
pytest -v
```

- **50 testes** em `tests/auth/auth_test.py` (15), `tests/business/planning_test.py` (13) e `tests/business/transactions_test.py` (22).
- **Autenticação:** sucesso, erros de validação, e-mail já cadastrado, credenciais inválidas e token ausente, inválido ou do tipo errado.
- **Plannings:** criação, detalhe, atualização, remoção e listagem, incluindo recurso não encontrado, acesso negado e planning já removido.
- **Transações:** criação (tipo inválido, valor negativo, planning inexistente, acesso negado, categoria inválida), atualização, remoção, detalhe e listagem (com busca e parâmetros de paginação).
- São testes da camada HTTP. Os services são substituídos por *mocks* (`unittest.mock.patch`), e a aplicação sobe com **SQLite em memória**, sem tocar no banco de desenvolvimento.
- **Resultado atual:** os 50 testes passam.
- Ainda não há testes para categorias nem testes de integração dos services.

---

## ⚠️ Limitações conhecidas

O projeto está em evolução. Estes são os pontos em que o comportamento atual ainda difere do esperado:

- **Listagem de categorias responde 500.** A rota recebe uma lista do service, mas tenta ler `pagination.item`. Ela também lê `page`, `per_page` e `search` sem repassá-los ao service.
- **Remover uma categoria inexistente responde 500, não 404.** O service lê `category.planning_id` antes de verificar se a categoria existe.
- **Categorias globais só pelo banco.** A API não cria, altera nem remove categorias sem planning.
- **Atualização de membros do planning.** O `UpdatePlanningSchema` espera `members` como um único objeto (`id`, `name`, `email`), mas o service espera uma lista de IDs. Uma lista é recusada com 400. Hoje, na prática, o `PATCH` só altera nome e descrição.
- **Conta vencida.** A API informa se a conta está paga (`is_paid`), mas não calcula se está vencida. O cliente pode comparar `due_date` com a data atual.
- **O refresh token não volta no cadastro.** O `register` gera o refresh token, mas responde só com o access token. Para obter o refresh token, faça login.
- **Erros HTTP do Flask viram 500.** O handler genérico de `Exception` também captura 404 (rota inexistente), 405 e 415 (corpo sem `Content-Type: application/json`), que acabam respondendo `500 Erro interno do servidor`.
- **Erros de banco viram 500.** O `db_transaction()` converte qualquer falha de escrita em `RuntimeError`.
- **Planning removido responde 409, não 404,** em detalhe, atualização e remoção. Remover um planning também não marca as transações dele como removidas.
- **Dependências e migrations.** O `Flask-Migrate` falta no `requirements.txt`, e a cadeia de migrations não funciona em banco vazio (veja [Como executar](#️-como-executar)).
- **Front-end incompleto.** Os componentes importados pelo `App.tsx` ainda não estão no repositório.

---

## 🗺️ Roadmap

- [ ] Corrigir a listagem de categorias e a remoção de categoria inexistente
- [ ] Corrigir a atualização de membros do planning
- [ ] Criar testes para categorias
- [ ] Adicionar o `Flask-Migrate` ao `requirements.txt` e reorganizar a cadeia de migrations
- [ ] Concluir o front-end em React e conectá-lo à API
- [ ] Serviço de e-mail (confirmação de cadastro e recuperação de senha)
- [ ] Convite por e-mail para entrar em um planning
- [ ] Endpoints de agregação para dashboards (gastos por dia e por categoria)
- [ ] Contas recorrentes

---

## 📄 Licença

Projeto de estudo e portfólio.
