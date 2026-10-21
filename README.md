# FastAPI CRUD Items API

A small REST API for managing user-owned items. It uses FastAPI, SQLAlchemy, SQLite, and JWT bearer authentication.

## Features

- User registration and login
- JWT-protected item CRUD endpoints
- Per-user item isolation
- Item search, stock filtering, and pagination
- SQLite database by default
- Interactive OpenAPI documentation
- Automated API tests

## Requirements

- Python 3.10 or newer
- `pip`

## Run locally

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API is available at [http://127.0.0.1:8000](http://127.0.0.1:8000). FastAPI creates the SQLite database (`app.db`) and its tables at startup.

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- Health check: `GET /health`

## Configuration

Settings can be supplied through environment variables or a `.env` file in the project root.

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./app.db` | SQLAlchemy database connection URL |
| `SECRET_KEY` | `dev-secret-change-me` | Key used to sign JWTs; change this outside local development |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT lifetime in minutes |

Example `.env` file:

```env
SECRET_KEY=replace-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./app.db
```

## API workflow

### 1. Register a user

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"ada@example.com","password":"password123"}'
```

### 2. Log in

The login endpoint accepts form data. The email is sent as `username` to follow the OAuth2 password-flow convention.

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=ada@example.com&password=password123'
```

Save the returned `access_token` and send it as a bearer token with protected requests:

```bash
export TOKEN='<access_token>'
```

### 3. Create an item

```bash
curl -X POST http://127.0.0.1:8000/items \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Laptop","description":"14 inch","in_stock":true}'
```

## Endpoints

| Method | Path | Authentication | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | No | Service health check |
| `POST` | `/auth/register` | No | Create a user |
| `POST` | `/auth/login` | No | Exchange credentials for a JWT |
| `GET` | `/auth/me` | Bearer token | Get the authenticated user |
| `POST` | `/items` | Bearer token | Create an item |
| `GET` | `/items` | Bearer token | List the current user's items |
| `GET` | `/items/{item_id}` | Bearer token | Retrieve an item owned by the current user |
| `PATCH` | `/items/{item_id}` | Bearer token | Partially update an item |
| `DELETE` | `/items/{item_id}` | Bearer token | Delete an item |

`GET /items` accepts these optional query parameters:

| Parameter | Default | Constraints | Description |
| --- | --- | --- | --- |
| `q` | — | — | Case-insensitive name search |
| `in_stock` | — | Boolean | Filter by stock status |
| `limit` | `20` | `1`–`100` | Maximum items returned |
| `offset` | `0` | `0` or greater | Number of items to skip |

Example:

```bash
curl 'http://127.0.0.1:8000/items?q=lap&in_stock=true&limit=20&offset=0' \
  -H "Authorization: Bearer $TOKEN"
```

## Run tests

```bash
pytest
```

The test suite uses a separate SQLite database, `test.db`, and covers authentication, the CRUD flow, filtering, and user-level data isolation.

## Run with Docker

Build and start the container:

```bash
docker build -t fastapi-crud .
docker run --rm -p 8000:8000 \
  -e SECRET_KEY='replace-with-a-long-random-secret' \
  fastapi-crud
```

For a persistent SQLite database in Docker, mount a directory and point `DATABASE_URL` to that mounted location.

```bash
mkdir -p data
docker run --rm -p 8000:8000 \
  -v "$(pwd)/data:/data" \
  -e DATABASE_URL='sqlite:////data/app.db' \
  -e SECRET_KEY='replace-with-a-long-random-secret' \
  fastapi-crud
```
