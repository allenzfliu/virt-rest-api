from fastapi.testclient import TestClient
from rest_api.rest_api import app
# This tester only works on my machine with my hypervisor.

def test_root():
    print("Starting tester!")
    client = TestClient(app)
    request = client.get("/")
    assert request.status_code == 200
    assert request.json() == {"host": "lgd"}