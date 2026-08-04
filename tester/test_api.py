from fastapi.testclient import TestClient
from rest_api.rest_api import app
# This tester only works on my machine with my hypervisor.
# Most of the test cases are based on my system.

client = TestClient(app)
GETTER_API_TEST_VM = "vspherer"
START_STOP_TEST_VM = "network-config-test"

def fetch_endpoint(url: str):
    request = client.get(url)
    data = request.json()
    # print(data)
    return (request, data)

def test_root():
    request, data = fetch_endpoint("/")
    assert request.status_code == 200
    assert request.json() == {"host": "lgd"}

def test_vms_active():
    request, data = fetch_endpoint("/vms?type=active")
    assert request.status_code == 200
    active_size = len(request.json()['vms'])
    assert 3 <= active_size <= 10
    
    request, data = fetch_endpoint("/vms?type=1")
    assert request.status_code == 200
    assert len(request.json()['vms']) == active_size

def test_vms_inactive():
    request, data = fetch_endpoint("/vms?type=inactive")
    assert request.status_code == 200
    inactive_size = len(request.json()['vms'])
    assert 10 <= inactive_size
    
    request, data = fetch_endpoint("/vms?type=2")
    assert request.status_code == 200
    assert len(request.json()['vms']) == inactive_size

def test_vms_all():
    request, data = fetch_endpoint("/vms?type=all")
    assert request.status_code == 200
    all_size = len(request.json()['vms'])
    assert 3 <= all_size <= 100
    
    request, data = fetch_endpoint("/vms?type=0")
    assert request.status_code == 200
    assert len(request.json()['vms']) == all_size
    
    active_size = len(client.get("/vms?type=active").json()['vms'])
    inactive_size = len(client.get("/vms?type=inactive").json()['vms'])
    assert active_size + inactive_size == all_size

def test_vm_info():
    request, data = fetch_endpoint("/vm_info?name=" + GETTER_API_TEST_VM)
    assert request.status_code == 200
    assert data['state'] == 1
    assert data['max_mem'] > 1000000
    assert data['cur_mem'] > 500000
    assert data['vcpu'] == 1
    assert data['cputime'] != 0

def test_vm_ip():
    request, data = fetch_endpoint("/vm_ip?name=" + GETTER_API_TEST_VM)
    assert request.status_code == 200
    assert "127.0.0.1/8" in data['ips']
    assert "192.168.9.243/24" in data['ips']

def test_vm_viewer():
    request, data = fetch_endpoint("/vm_ip?name=" + GETTER_API_TEST_VM)
    assert request.status_code == 200
    assert data['ip'] == "0.0.0.0"
    assert 5900 <= data['port'] <= 6000

def test_vm_start():
    post = client.post("/vm_start?name=" + START_STOP_TEST_VM)
    data = post.json()
    assert post.status_code == 200
    assert data['status'] == True

def test_vm_stop():
    post = client.post("/vm_stop?name=" + START_STOP_TEST_VM)
    data = post.json()
    assert post.status_code == 200
    assert data['status'] == False

# not gonna bother lmao
def test_vm_xmldesc():
    request, data = fetch_endpoint("/vm_xmldesc?name=" + GETTER_API_TEST_VM)
    assert request.status_code == 200
    assert request.json() != None