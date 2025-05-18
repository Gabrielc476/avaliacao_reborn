# tests/services/test_auth_service.py
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from jose import jwt
import os
from datetime import datetime, timedelta

from database.models.user import User
from database.schemas.user import UserCreate
from services.auth_service import AuthService, Token
from repositories.user_repository import UserRepository
from utils.password import PasswordUtils
from utils.jwt import JWTUtils


# Fixture para o serviço de autenticação com repositório mockado
@pytest.fixture
def auth_service_with_mock():
    mock_repository = MagicMock(spec=UserRepository)
    service = AuthService(mock_repository)
    return service, mock_repository


# Testes unitários para o serviço de autenticação
@pytest.mark.asyncio
async def test_authenticate_user_success(auth_service_with_mock, test_db, test_user):
    """Testa autenticação de usuário com sucesso"""
    service, mock_repo = auth_service_with_mock

    # Configura o mock para retornar o usuário de teste
    mock_repo.get_by_username.return_value = test_user

    # Tenta autenticar com as credenciais corretas
    authenticated_user = await service.authenticate_user(test_db, "testuser", "testpassword")

    # Verifica se o usuário foi autenticado corretamente
    assert authenticated_user is not None
    assert authenticated_user.id == test_user.id
    assert authenticated_user.username == test_user.username

    # Verifica se o repositório foi chamado corretamente
    mock_repo.get_by_username.assert_called_once_with(test_db, "testuser")


@pytest.mark.asyncio
async def test_authenticate_user_by_email(auth_service_with_mock, test_db, test_user):
    """Testa autenticação de usuário com email"""
    service, mock_repo = auth_service_with_mock

    # Configura o mock para retornar o usuário de teste
    mock_repo.get_by_email.return_value = test_user

    # Tenta autenticar com as credenciais corretas
    authenticated_user = await service.authenticate_user(test_db, "test@example.com", "testpassword")

    # Verifica se o usuário foi autenticado corretamente
    assert authenticated_user is not None
    assert authenticated_user.id == test_user.id
    assert authenticated_user.email == test_user.email

    # Verifica se o repositório foi chamado corretamente
    mock_repo.get_by_email.assert_called_once_with(test_db, "test@example.com")


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(auth_service_with_mock, test_db, test_user):
    """Testa autenticação de usuário com senha incorreta"""
    service, mock_repo = auth_service_with_mock

    # Configura o mock para retornar o usuário de teste
    mock_repo.get_by_username.return_value = test_user

    # Tenta autenticar com senha incorreta
    authenticated_user = await service.authenticate_user(test_db, "testuser", "wrongpassword")

    # Verifica que a autenticação falhou
    assert authenticated_user is None

    # Verifica se o repositório foi chamado corretamente
    mock_repo.get_by_username.assert_called_once_with(test_db, "testuser")


@pytest.mark.asyncio
async def test_authenticate_user_not_found(auth_service_with_mock, test_db):
    """Testa autenticação de usuário inexistente"""
    service, mock_repo = auth_service_with_mock

    # Configura o mock para retornar None (usuário não encontrado)
    mock_repo.get_by_username.return_value = None

    # Tenta autenticar um usuário inexistente
    authenticated_user = await service.authenticate_user(test_db, "nonexistent", "password")

    # Verifica que a autenticação falhou
    assert authenticated_user is None

    # Verifica se o repositório foi chamado corretamente
    mock_repo.get_by_username.assert_called_once_with(test_db, "nonexistent")


@pytest.mark.asyncio
async def test_create_user_success(auth_service_with_mock, test_db):
    """Testa criação de usuário com sucesso"""
    service, mock_repo = auth_service_with_mock

    # Configura o mock para simular usuário não existente
    mock_repo.get_by_username.return_value = None
    mock_repo.get_by_email.return_value = None

    # Configura o mock para retornar um novo usuário na criação
    new_user = User(id=1, username="newuser", email="new@example.com", is_active=True)
    mock_repo.create.return_value = new_user

    # Dados para criação do usuário
    user_data = UserCreate(
        username="newuser",
        email="new@example.com",
        password="password123"
    )

    # Cria o usuário
    created_user = await service.create_user(test_db, user_data)

    # Verifica se o usuário foi criado corretamente
    assert created_user is not None
    assert created_user.id == 1
    assert created_user.username == "newuser"
    assert created_user.email == "new@example.com"

    # Verifica se o repositório foi chamado corretamente
    mock_repo.get_by_username.assert_called_once_with(test_db, "newuser")
    mock_repo.get_by_email.assert_called_once_with(test_db, "new@example.com")
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_username_exists(auth_service_with_mock, test_db, test_user):
    """Testa criação de usuário com nome de usuário já existente"""
    service, mock_repo = auth_service_with_mock

    # Configura o mock para simular usuário já existente
    mock_repo.get_by_username.return_value = test_user

    # Dados para criação do usuário
    user_data = UserCreate(
        username="testuser",  # Nome já existente
        email="new@example.com",
        password="password123"
    )

    # Tenta criar o usuário e verifica se lança a exceção correta
    with pytest.raises(HTTPException) as excinfo:
        await service.create_user(test_db, user_data)

    # Verifica a exceção
    assert excinfo.value.status_code == 400
    assert "Nome de usuário já em uso" in excinfo.value.detail

    # Verifica se o repositório foi chamado corretamente
    mock_repo.get_by_username.assert_called_once_with(test_db, "testuser")
    mock_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_user_email_exists(auth_service_with_mock, test_db, test_user):
    """Testa criação de usuário com email já existente"""
    service, mock_repo = auth_service_with_mock

    # Configura o mock para simular email já existente
    mock_repo.get_by_username.return_value = None
    mock_repo.get_by_email.return_value = test_user

    # Dados para criação do usuário
    user_data = UserCreate(
        username="newuser",
        email="test@example.com",  # Email já existente
        password="password123"
    )

    # Tenta criar o usuário e verifica se lança a exceção correta
    with pytest.raises(HTTPException) as excinfo:
        await service.create_user(test_db, user_data)

    # Verifica a exceção
    assert excinfo.value.status_code == 400
    assert "Email já em uso" in excinfo.value.detail

    # Verifica se o repositório foi chamado corretamente
    mock_repo.get_by_username.assert_called_once_with(test_db, "newuser")
    mock_repo.get_by_email.assert_called_once_with(test_db, "test@example.com")
    mock_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_tokens(auth_service_with_mock, test_user):
    """Testa criação de tokens de acesso e atualização"""
    service, _ = auth_service_with_mock

    # Cria tokens para o usuário de teste
    tokens = await service.create_tokens(test_user)

    # Verifica se os tokens foram criados corretamente
    assert isinstance(tokens, Token)
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    assert tokens.token_type == "bearer"

    # Verifica se os tokens contêm as informações corretas
    access_payload = jwt.decode(
        tokens.access_token,
        os.getenv("JWT_SECRET_KEY"),
        algorithms=[os.getenv("JWT_ALGORITHM", "HS256")]
    )
    assert access_payload["user_id"] == test_user.id
    assert access_payload["username"] == test_user.username
    assert access_payload["email"] == test_user.email

    refresh_payload = jwt.decode(
        tokens.refresh_token,
        os.getenv("JWT_SECRET_KEY"),
        algorithms=[os.getenv("JWT_ALGORITHM", "HS256")]
    )
    assert refresh_payload["user_id"] == test_user.id
    assert refresh_payload["username"] == test_user.username
    assert refresh_payload["email"] == test_user.email


@pytest.mark.asyncio
async def test_get_current_user_success(auth_service_with_mock, test_db, test_user):
    """Testa obtenção do usuário atual a partir do token"""
    service, mock_repo = auth_service_with_mock

    # Cria um token válido
    token_data = {
        "user_id": test_user.id,
        "username": test_user.username,
        "email": test_user.email
    }
    access_token = JWTUtils.create_access_token(data=token_data)

    # Configura o mock para retornar o usuário de teste
    mock_repo.get_by_id.return_value = test_user

    # Obtém o usuário a partir do token
    user = await service.get_current_user(test_db, access_token)

    # Verifica se o usuário foi encontrado corretamente
    assert user is not None
    assert user.id == test_user.id
    assert user.username == test_user.username

    # Verifica se o repositório foi chamado corretamente
    mock_repo.get_by_id.assert_called_once_with(test_db, test_user.id)


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(auth_service_with_mock, test_db):
    """Testa obtenção do usuário com token inválido"""
    service, mock_repo = auth_service_with_mock

    # Tenta obter o usuário com um token inválido
    with pytest.raises(HTTPException) as excinfo:
        await service.get_current_user(test_db, "invalid_token")

    # Verifica a exceção
    assert excinfo.value.status_code == 401
    assert "Credenciais inválidas" in excinfo.value.detail

    # Verifica que o repositório não foi chamado
    mock_repo.get_by_id.assert_not_called()


@pytest.mark.asyncio
async def test_get_current_user_not_found(auth_service_with_mock, test_db, test_user):
    """Testa obtenção de usuário não encontrado"""
    service, mock_repo = auth_service_with_mock

    # Cria um token válido
    token_data = {
        "user_id": 999,  # ID que não existe
        "username": "nonexistent",
        "email": "nonexistent@example.com"
    }
    access_token = JWTUtils.create_access_token(data=token_data)

    # Configura o mock para retornar None (usuário não encontrado)
    mock_repo.get_by_id.return_value = None

    # Tenta obter o usuário e verifica a exceção
    with pytest.raises(HTTPException) as excinfo:
        await service.get_current_user(test_db, access_token)

    # Verifica a exceção
    assert excinfo.value.status_code == 401
    assert "Usuário não encontrado" in excinfo.value.detail

    # Verifica se o repositório foi chamado corretamente
    mock_repo.get_by_id.assert_called_once_with(test_db, 999)


@pytest.mark.asyncio
async def test_get_current_user_inactive(auth_service_with_mock, test_db, test_user):
    """Testa obtenção de usuário inativo"""
    service, mock_repo = auth_service_with_mock

    # Torna o usuário inativo
    inactive_user = test_user
    inactive_user.is_active = False

    # Cria um token válido
    token_data = {
        "user_id": inactive_user.id,
        "username": inactive_user.username,
        "email": inactive_user.email
    }
    access_token = JWTUtils.create_access_token(data=token_data)

    # Configura o mock para retornar o usuário inativo
    mock_repo.get_by_id.return_value = inactive_user

    # Tenta obter o usuário e verifica a exceção
    with pytest.raises(HTTPException) as excinfo:
        await service.get_current_user(test_db, access_token)

    # Verifica a exceção
    assert excinfo.value.status_code == 401
    assert "Usuário inativo" in excinfo.value.detail

    # Verifica se o repositório foi chamado corretamente
    mock_repo.get_by_id.assert_called_once_with(test_db, inactive_user.id)


@pytest.mark.asyncio
async def test_refresh_access_token_success(auth_service_with_mock, test_db, test_user):
    """Testa atualização do token de acesso com sucesso"""
    service, mock_repo = auth_service_with_mock

    # Cria um token de atualização válido
    token_data = {
        "user_id": test_user.id,
        "username": test_user.username,
        "email": test_user.email
    }
    refresh_token = JWTUtils.create_refresh_token(data=token_data)

    # Configura o mock para retornar o usuário de teste
    mock_repo.get_by_id.return_value = test_user

    # Atualiza o token
    new_tokens = await service.refresh_access_token(test_db, refresh_token)

    # Verifica se os novos tokens foram criados corretamente
    assert isinstance(new_tokens, Token)
    assert new_tokens.access_token is not None
    assert new_tokens.refresh_token is not None
    assert new_tokens.token_type == "bearer"

    # Verifica se o repositório foi chamado corretamente
    mock_repo.get_by_id.assert_called_once_with(test_db, test_user.id)


@pytest.mark.asyncio
async def test_refresh_access_token_invalid_token(auth_service_with_mock, test_db):
    """Testa atualização com token inválido"""
    service, mock_repo = auth_service_with_mock

    # Tenta atualizar com um token inválido
    with pytest.raises(HTTPException) as excinfo:
        await service.refresh_access_token(test_db, "invalid_token")

    # Verifica a exceção
    assert excinfo.value.status_code == 401
    assert "Credenciais inválidas" in excinfo.value.detail

    # Verifica que o repositório não foi chamado
    mock_repo.get_by_id.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_access_token_user_not_found(auth_service_with_mock, test_db):
    """Testa atualização quando usuário não é encontrado"""
    service, mock_repo = auth_service_with_mock

    # Cria um token válido para um usuário que não existe
    token_data = {
        "user_id": 999,
        "username": "nonexistent",
        "email": "nonexistent@example.com"
    }
    refresh_token = JWTUtils.create_refresh_token(data=token_data)

    # Configura o mock para retornar None (usuário não encontrado)
    mock_repo.get_by_id.return_value = None

    # Tenta atualizar o token e verifica a exceção
    with pytest.raises(HTTPException) as excinfo:
        await service.refresh_access_token(test_db, refresh_token)

    # Verifica a exceção
    assert excinfo.value.status_code == 401
    assert "Usuário não encontrado ou inativo" in excinfo.value.detail

    # Verifica se o repositório foi chamado corretamente
    mock_repo.get_by_id.assert_called_once_with(test_db, 999)