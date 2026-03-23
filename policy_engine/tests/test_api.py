from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_auth_invalid_credentials():
    payload = {
        "username": "unknown_user",
        "password": "wrong_password",
        "mac_address": "AA-BB-CC-DD-EE-FF",
        "nas_ip": "10.0.0.1"
    }
    response = client.post("/auth", json=payload)
    # The expected behavior for a missing user is 401 Unauthorized
    assert response.status_code == 401
    assert "detail" in response.json()

def test_accounting_start():
    payload = {
        "status_type": "Start",
        "session_id": "test-session-12345",
        "username": "testuser",
        "nas_ip": "10.0.0.1",
        "mac_address": "AA-BB-CC-DD-EE-FF",
        "input_octets": 0,
        "output_octets": 0,
        "session_time": 0
    }
    response = client.post("/accounting", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Accounting recorded"}
