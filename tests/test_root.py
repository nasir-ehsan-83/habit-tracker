import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import UserCreate


def test_register() -> None:
    with TestClient(app) as client:
        uniq = uuid.uuid4().hex[:8]
        user = UserCreate(
            name = "Ahmad",
            username = f"Ahmadi_{uniq}",
            email = f"ahmad_{uniq}@example.com",
            password = "password",
        )
        res = client.post("/api/auth/register", json = user.model_dump())
        assert res.status_code == 201
        assert res.json()["name"] == "Ahmad"