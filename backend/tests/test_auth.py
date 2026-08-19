import pytest
from app.core.security import verify_password
from tests.conftest import auth_headers_for


def test_login_success(client, user_a):
    response = client.post("/api/auth/login", json={
        "username": "usera",
        "password": "Password123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "csrf_token" in data
    assert "access_token" in response.cookies


def test_login_invalid_password(client, user_a):
    response = client.post("/api/auth/login", json={
        "username": "usera",
        "password": "WrongPassword!"
    })
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid username or password"


def test_login_nonexistent_user(client):
    response = client.post("/api/auth/login", json={
        "username": "nonexistent",
        "password": "Password123!"
    })
    assert response.status_code == 401
    # Generic message, does not reveal username nonexistence
    assert response.json()["error"]["message"] == "Invalid username or password"


def test_logout(client, user_a):
    headers = auth_headers_for(user_a)
    response = client.post("/api/auth/logout", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"


def test_delete_self_account(client, user_a):
    headers = auth_headers_for(user_a)
    res = client.request("DELETE", "/api/users/me", json={"password": "Password123!"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["message"] == "Account deleted successfully"
