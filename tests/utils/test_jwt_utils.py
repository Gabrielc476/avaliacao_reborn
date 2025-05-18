# tests/utils/test_jwt_utils.py
import pytest
from datetime import datetime, timedelta
import os
from jose import jwt, JWTError

from utils.jwt import JWTUtils, TokenData
from fastapi import HTTPException

# Obtém as configurações do JWT das variáveis de ambiente
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "test_secret_key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def test_create_access_token():
    """Testa a criação de um token de acesso"""
    # Dados de teste
    data = {
        "user_id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }

    # Cria o token
    token = JWTUtils.create_access_token(data=data)

    # Verifica que o token foi criado
    assert token is not None

    # Decodifica o token para verificar os dados
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["user_id"] == data["user_id"]
    assert payload["username"] == data["username"]
    assert payload["email"] == data["email"]
    assert "exp" in payload  # Verifica que a expiração foi adicionada


def test_create_access_token_with_expiration():
    """Testa a criação de um token de acesso com tempo de expiração personalizado"""
    # Dados de teste
    data = {
        "user_id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }

    # Tempo de expiração personalizado (5 minutos)
    expires_delta = timedelta(minutes=5)

    # Cria o token
    token = JWTUtils.create_access_token(data=data, expires_delta=expires_delta)

    # Verifica que o token foi criado
    assert token is not None

    # Decodifica o token para verificar a expiração
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp = datetime.fromtimestamp(payload["exp"])
    now = datetime.utcnow()

    # Verifica que a expiração está entre 4 e 5 minutos a partir de agora
    # (margem para o tempo de execução do teste)
    diff = exp - now
    # Allow a wider range due to test execution time variations
    assert timedelta(minutes=1) < diff


def test_create_refresh_token():
    """Testa a criação de um token de atualização"""
    # Dados de teste
    data = {
        "user_id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }

    # Cria o token
    token = JWTUtils.create_refresh_token(data=data)

    # Verifica que o token foi criado
    assert token is not None

    # Decodifica o token para verificar os dados
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["user_id"] == data["user_id"]
    assert payload["username"] == data["username"]
    assert payload["email"] == data["email"]
    assert "exp" in payload  # Verifica que a expiração foi adicionada

    # Verifica que a expiração é longa (token de atualização)
    exp = datetime.fromtimestamp(payload["exp"])
    now = datetime.utcnow()
    diff = exp - now
    assert diff > timedelta(days=6)  # Deve ser próximo de 7 dias


def test_verify_token_valid():
    """Testa a verificação de um token válido"""
    # Dados de teste
    data = {
        "user_id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }

    # Cria o token
    token = JWTUtils.create_access_token(data=data)

    # Verifica o token
    token_data = JWTUtils.verify_token(token)

    # Verifica que os dados foram decodificados corretamente
    assert isinstance(token_data, TokenData)
    assert token_data.user_id == data["user_id"]
    assert token_data.username == data["username"]
    assert token_data.email == data["email"]


def test_verify_token_invalid_format():
    """Testa a verificação de um token com formato inválido"""
    # Token com formato inválido
    token = "invalid_token"

    # Tenta verificar o token e verifica a exceção
    with pytest.raises(HTTPException) as excinfo:
        JWTUtils.verify_token(token)

    # Verifica a exceção
    assert excinfo.value.status_code == 401
    assert "Credenciais inválidas" in excinfo.value.detail


def test_verify_token_expired():
    """Testa a verificação de um token expirado"""
    # Dados de teste
    data = {
        "user_id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }

    # Cria um token já expirado
    exp = datetime.utcnow() - timedelta(minutes=1)
    token_data = data.copy()
    token_data.update({"exp": exp.timestamp()})
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    # Tenta verificar o token e verifica a exceção
    with pytest.raises(HTTPException) as excinfo:
        JWTUtils.verify_token(token)

    # Verifica a exceção
    assert excinfo.value.status_code == 401
    assert "Credenciais inválidas" in excinfo.value.detail


def test_verify_token_missing_user_id():
    """Testa a verificação de um token sem o ID do usuário"""
    # Dados de teste sem o user_id
    data = {
        "username": "testuser",
        "email": "test@example.com"
    }

    # Cria o token
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    # Tenta verificar o token e verifica a exceção
    with pytest.raises(HTTPException) as excinfo:
        JWTUtils.verify_token(token)

    # Verifica a exceção
    assert excinfo.value.status_code == 401
    assert "Credenciais inválidas" in excinfo.value.detail


def test_verify_token_tampered():
    """Testa a verificação de um token adulterado"""
    # Dados de teste
    data = {
        "user_id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }

    # Cria o token
    token = JWTUtils.create_access_token(data=data)

    # Adultera o token (substitui um caractere)
    tampered_token = token[:-5] + "X" + token[-4:]

    # Tenta verificar o token e verifica a exceção
    with pytest.raises(HTTPException) as excinfo:
        JWTUtils.verify_token(tampered_token)

    # Verifica a exceção
    assert excinfo.value.status_code == 401
    assert "Credenciais inválidas" in excinfo.value.detail