import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app) as c:
        yield c


def auth_headers(client, email="a@example.com"):
    client.post("/auth/register", json={"email": email, "password": "password123"})
    r = client.post("/auth/login", data={"username": email, "password": "password123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_requires_auth(client):
    assert client.get("/items").status_code == 401


def test_crud_flow(client):
    h = auth_headers(client)
    r = client.post("/items", json={"name": "Laptop", "description": "14 inch"}, headers=h)
    assert r.status_code == 201
    item_id = r.json()["id"]

    assert client.get(f"/items/{item_id}", headers=h).json()["name"] == "Laptop"

    r = client.patch(f"/items/{item_id}", json={"in_stock": False}, headers=h)
    assert r.json()["in_stock"] is False and r.json()["name"] == "Laptop"

    r = client.get("/items?q=lap&in_stock=false", headers=h)
    assert r.json()["total"] == 1

    assert client.delete(f"/items/{item_id}", headers=h).status_code == 204
    assert client.get(f"/items/{item_id}", headers=h).status_code == 404


def test_users_cannot_see_each_others_items(client):
    h1 = auth_headers(client, "one@example.com")
    h2 = auth_headers(client, "two@example.com")
    item_id = client.post("/items", json={"name": "Secret"}, headers=h1).json()["id"]
    assert client.get(f"/items/{item_id}", headers=h2).status_code == 404
    assert client.get("/items", headers=h2).json()["total"] == 0
