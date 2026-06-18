# 💰 Shared Finance API

> API REST para planejamento financeiro **compartilhado** — múltiplos usuários (um casal, uma família) dividem um mesmo orçamento, com controle de transações, contas a pagar e categorias.

Construída com **Flask**, arquitetura em camadas, autenticação **JWT** e validação rigorosa com **Pydantic v2**.

---

## ✨ Funcionalidades

- 🔐 **Autenticação JWT** — registro, login, refresh token e rota de perfil (`/me`)
- 👥 **Planejamentos compartilhados** — múltiplos membros por planning (relação muitos-para-muitos)
- 💸 **Transações** — receitas e despesas com categorização e contas a pagar
- 📅 **Contas a pagar** — status derivado de datas (pendente / vencida / paga)
- 🏷️ **Categorias** — globais (do sistema) ou específicas de cada planning
- 🗑️ **Soft delete** — registros nunca são destruídos, preservando o histórico financeiro
- 📄 **Paginação** — listagens paginadas e reutilizáveis
- 🛡️ **Autorização por pertencimento** — cada usuário só acessa os plannings de que é membro

---

## 🏗️ Arquitetura

Organização em camadas, com responsabilidades bem separadas:

```
Request → Route → Service → Model → Database
            │        │
           DTO    regra de
        (validação) negócio
```

| Camada | Responsabilidade |
|--------|------------------|
| **Routes** | Recebe HTTP, valida entrada, monta resposta |
| **Services** | Regra de negócio e autorização (não conhecem HTTP) |
| **Models** | Entidades e persistência (SQLAlchemy) |
| **DTOs / Schemas** | Validação de entrada e formatação de saída (Pydantic) |

**Princípio central:** os services lançam exceções tipadas; handlers globais as traduzem em status codes HTTP.

---

## 🧱 Stack

| Tecnologia | Uso |
|------------|-----|
| **Flask** | Framework web |
| **SQLAlchemy** | ORM |
| **Pydantic v2** | Validação e serialização |
| **flask-jwt-extended** | Autenticação JWT |
| **bcrypt** | Hash de senhas |
| **Flask-Migrate** | Migrations do banco |
| **PostgreSQL** | Banco de dados |
| **pytest** | Testes |

---

## 🚀 Como rodar

```bash
# 1. clonar e entrar no projeto
git clone git@github.com:<seu-usuario>/shared-finance-api.git
cd shared-finance-api

# 2. ambiente virtual
python -m venv .venv
source .venv/bin/activate

# 3. dependências
pip install -r requirements.txt

# 4. variáveis de ambiente (veja .env.example)
cp .env.example .env
# edite o .env com suas chaves e a URL do banco

# 5. migrations
flask db upgrade

# 6. rodar
flask run
```

### Variáveis de ambiente

```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/finance
SECRET_KEY=<openssl rand -hex 16>
JWT_SECRET_KEY=<openssl rand -hex 16>
```

---

## 📡 Endpoints principais

### Autenticação

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/auth/register` | Cria conta |
| `POST` | `/auth/login` | Login (retorna tokens) |
| `POST` | `/auth/refresh` | Renova o access token |
| `GET` | `/auth/me` | Dados do usuário autenticado |

### Plannings

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/plannings` | Cria um planning |
| `GET` | `/plannings` | Lista os plannings do usuário (paginado) |
| `GET` | `/plannings/<id>` | Detalhes de um planning |
| `PATCH` | `/plannings/<id>` | Atualiza |
| `DELETE` | `/plannings/<id>` | Remove (soft delete) |

### Transações

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/plannings/<id>/transactions` | Cria transação |
| `GET` | `/plannings/<id>/transactions` | Lista transações (paginado) |
| `PATCH` | `/transactions/<id>` | Atualiza |
| `DELETE` | `/transactions/<id>` | Remove (soft delete) |

### Categorias

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/plannings/<id>/categories` | Cria categoria |
| `GET` | `/plannings/<id>/categories` | Lista categorias (do planning + globais) |
| `PATCH` | `/plannings/<id>/categories/<id>` | Atualiza |
| `DELETE` | `/plannings/<id>/categories/<id>` | Remove (soft delete) |

---

## 📦 Formato das respostas

Todas as respostas seguem um envelope padronizado:

```json
{
  "message": "Operação realizada com sucesso",
  "data": { }
}
```

Listagens incluem metadados de paginação:

```json
{
  "message": "Plannings encontrados",
  "data": [ ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 42,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## 🧪 Testes

```bash
pytest -v
```

Testes isolados com banco SQLite em memória — não tocam o banco de desenvolvimento.

---

## 🗺️ Roadmap

- [ ] Frontend em React
- [ ] Service de e-mail (confirmação de cadastro, recuperação de senha)
- [ ] Fluxo de convite por e-mail para entrar num planning
- [ ] Endpoints de agregação para dashboards (gastos por dia / categoria)
- [ ] Recorrência de contas

---

## 📄 Licença

Projeto de estudo e portfólio.