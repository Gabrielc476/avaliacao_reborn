# tests/routes/test_auth_routes.py
import pytest
from fastapi.testclient import TestClient
import json
from unittest.mock import patch

from database.models.user import User


def test_register_success(test_client):
    """Testa o registro de um novo usuário com sucesso"""
    # Dados para um novo usuário
    user_data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "newpassword"
    }

    # Faz a requisição de registro
    response = test_client.post("/api/auth/register", json=user_data)

    # Verifica a resposta
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "is_active" in data
    assert data["is_active"] is True


def test_register_username_exists(test_client, test_user):
    """Testa o registro com nome de usuário já existente"""
    # Dados com nome de usuário já existente
    user_data = {
        "username": "testuser",  # Nome já existente
        "email": "another@example.com",
        "password": "password123"
    }

    # Faz a requisição de registro
    response = test_client.post("/api/auth/register", json=user_data)

    # Verifica a resposta de erro
    assert response.status_code == 400
    data = response.json()
    assert "Nome de usuário já em uso" in data["detail"]


def test_register_email_exists(test_client, test_user):
    """Testa o registro com email já existente"""
    # Dados com email já existente
    user_data = {
        "username": "anotheruser",
        "email": "test@example.com",  # Email já existente
        "password": "password123"
    }

    # Faz a requisição de registro
    response = test_client.post("/api/auth/register", json=user_data)

    # Verifica a resposta de erro
    assert response.status_code == 400
    data = response.json()
    assert "Email já em uso" in data["detail"]


def test_login_success(test_client, test_user):
    """Testa o login com sucesso"""
    # Faz a requisição de login
    response = test_client.post(
        "/api/auth/login",
        params={"username": "testuser", "password": "testpassword"}
    )

    # Verifica a resposta
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_username(test_client):
    """Testa o login com nome de usuário incorreto"""
    # Faz a requisição de login com nome de usuário incorreto
    response = test_client.post(
        "/api/auth/login",
        params={"username": "wronguser", "password": "testpassword"}
    )

    # Verifica a resposta de erro
    assert response.status_code == 401
    data = response.json()
    assert "Credenciais inválidas" in data["detail"]


def test_login_wrong_password(test_client, test_user):
    """Testa o login com senha incorreta"""
    # Faz a requisição de login com senha incorreta
    response = test_client.post(
        "/api/auth/login",
        params={"username": "testuser", "password": "wrongpassword"}
    )

    # Verifica a resposta de erro
    assert response.status_code == 401
    data = response.json()
    assert "Credenciais inválidas" in data["detail"]


def test_login_with_email(test_client, test_user):
    """Testa o login usando email"""
    # Faz a requisição de login com email
    response = test_client.post(
        "/api/auth/login",
        params={"username": "test@example.com", "password": "testpassword"}
    )

    # Verifica a resposta
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_token_success(test_client, test_user_token):
    """Testa a atualização do token com sucesso"""
    # Obtém o token de atualização
    refresh_token = test_user_token["refresh_token"]

    # Faz a requisição de atualização
    response = test_client.post(
        "/api/auth/refresh",
        params={"refresh_token": refresh_token}
    )

    # Verifica a resposta
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_token_invalid(test_client):
    """Testa a atualização com token inválido"""
    # Faz a requisição de atualização com token inválido
    response = test_client.post(
        "/api/auth/refresh",
        params={"refresh_token": "invalid_token"}
    )

    # Verifica a resposta de erro
    assert response.status_code == 401
    data = response.json()
    assert "Credenciais inválidas" in data["detail"]


def test_get_current_user_success(test_client, test_user_token):
    """Testa a obtenção do usuário atual com sucesso"""
    # Obtém o token de acesso
    access_token = test_user_token["access_token"]

    # Faz a requisição para obter o usuário atual
    response = test_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Verifica a resposta
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert data["is_active"] is True


def test_get_current_user_no_token(test_client):
    """Testa a obtenção do usuário sem token"""
    # Faz a requisição sem token
    response = test_client.get("/api/auth/me")

    # Verifica a resposta de erro
    assert response.status_code == 401
    data = response.json()
    assert "Token de autenticação ausente ou inválido" in data["detail"]


def test_get_current_user_invalid_token(test_client):
    """Testa a obtenção do usuário com token inválido"""
    # Faz a requisição com token inválido
    response = test_client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )

    # Verifica a resposta de erro
    assert response.status_code == 401
    data = response.json()
    assert "Credenciais inválidas" in data["detail"]


def test_get_current_user_wrong_prefix(test_client, test_user_token):
    """Testa a obtenção do usuário com prefixo incorreto"""
    # Obtém o token de acesso
    access_token = test_user_token["access_token"]

    # Faz a requisição com prefixo incorreto
    response = test_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Basic {access_token}"}  # Prefixo incorreto
    )

    # Verifica a resposta de erro
    assert response.status_code == 401
    data = response.json()
    assert "Token de autenticação ausente ou inválido" in data["detail"]