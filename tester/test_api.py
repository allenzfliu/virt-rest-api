from fastapi.testclient import TestClient
from rest_api.rest_api import app
# This tester only works on my machine with my hypervisor.

client = TestClient(app)

def test_root():
    request = client.get("/")
    assert request.status_code == 200
    assert request.json() == {"host": "lgd"}

def test_vms_active():
    request = client.get("/vms?type=active")
    assert request.status_code == 200
    active_size = len(request.json()['vms'])
    assert 3 <= active_size <= 10
    
    request = client.get("/vms?type=1")
    assert request.status_code == 200
    assert len(request.json()['vms']) == active_size

def test_vms_inactive():
    request = client.get("/vms?type=inactive")
    assert request.status_code == 200
    inactive_size = len(request.json()['vms'])
    assert 10 <= inactive_size
    
    request = client.get("/vms?type=2")
    assert request.status_code == 200
    assert len(request.json()['vms']) == inactive_size

def test_vms_all():
    request = client.get("/vms?type=all")
    assert request.status_code == 200
    all_size = len(request.json()['vms'])
    assert 3 <= all_size <= 100
    
    request = client.get("/vms?type=0")
    assert request.status_code == 200
    assert len(request.json()['vms']) == all_size
    
    active_size = len(client.get("/vms?type=active").json()['vms'])
    inactive_size = len(client.get("/vms?type=inactive").json()['vms'])
    assert active_size + inactive_size == all_size