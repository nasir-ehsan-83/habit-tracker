from fastapi.testclient import TestClient;
from  app.main import app;

client = TestClient(app);

def test_root():
    res = client.get("/");

    print(res.json());
    print(res.status_code);

    assert res.json().get("message") == "hello world";
    assert res.status_code == 200;
