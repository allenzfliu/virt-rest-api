from main import app

from fastapi.testclient import TestClient
import config

client = TestClient(app)

print(client.get("/").json())