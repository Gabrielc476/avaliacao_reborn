# tests/repositories/test_user_repository.py
import pytest
from sqlalchemy.orm import Session

from database.models.user import User
from database.schemas.user import UserCreate
from repositories.user_repository import UserRepository
from utils.password import PasswordUtils


def test_get_by_id(test_db: Session, test_user: User):
    """Testa a busca de um usuário por ID"""
    # Busca o usuário pelo ID
    found_user = UserRepository.get_by_id(test_db, test_user.id)

    # Verifica se o usuário foi encontrado
    assert found_user is not None
    assert found_user.id == test_user.id
    assert found_user.username == test_user.username
    assert found_user.email == test_user.email


def test_get_by_id_not_found(test_db: Session):
    """Testa a busca de um usuário por ID inexistente"""
    # Busca um usuário com ID inexistente
    found_user = UserRepository.get_by_id(test_db, 999)

    # Verifica que o usuário não foi encontrado
    assert found_user is None


def test_get_by_username(test_db: Session, test_user: User):
    """Testa a busca de um usuário por nome de usuário"""
    # Busca o usuário pelo nome de usuário
    found_user = UserRepository.get_by_username(test_db, test_user.username)

    # Verifica se o usuário foi encontrado
    assert found_user is not None
    assert found_user.id == test_user.id
    assert found_user.username == test_user.username


def test_get_by_username_not_found(test_db: Session):
    """Testa a busca de um usuário por nome de usuário inexistente"""
    # Busca um usuário com nome inexistente
    found_user = UserRepository.get_by_username(test_db, "nonexistent")

    # Verifica que o usuário não foi encontrado
    assert found_user is None


def test_get_by_email(test_db: Session, test_user: User):
    """Testa a busca de um usuário por email"""
    # Busca o usuário pelo email
    found_user = UserRepository.get_by_email(test_db, test_user.email)

    # Verifica se o usuário foi encontrado
    assert found_user is not None
    assert found_user.id == test_user.id
    assert found_user.email == test_user.email


def test_get_by_email_not_found(test_db: Session):
    """Testa a busca de um usuário por email inexistente"""
    # Busca um usuário com email inexistente
    found_user = UserRepository.get_by_email(test_db, "nonexistent@example.com")

    # Verifica que o usuário não foi encontrado
    assert found_user is None


def test_get_all(test_db: Session, test_user: User):
    """Testa a busca de todos os usuários"""
    # Cria mais um usuário para testar a busca múltipla
    second_user = User(
        username="anotheruser",
        email="another@example.com",
        hashed_password=PasswordUtils.get_password_hash("password"),
        is_active=True
    )
    test_db.add(second_user)
    test_db.commit()

    # Busca todos os usuários
    users = UserRepository.get_all(test_db)

    # Verifica se ambos os usuários foram encontrados
    assert len(users) == 2
    assert any(u.username == "testuser" for u in users)
    assert any(u.username == "anotheruser" for u in users)


def test_create(test_db: Session):
    """Testa a criação de um novo usuário"""
    # Dados para criação do usuário
    user_data = UserCreate(
        username="newuser",
        email="new@example.com",
        password="newpassword"
    )

    # Cria o usuário
    hashed_password = PasswordUtils.get_password_hash(user_data.password)
    created_user = UserRepository.create(test_db, user_data, hashed_password)

    # Verifica se o usuário foi criado corretamente
    assert created_user is not None
    assert created_user.username == user_data.username
    assert created_user.email == user_data.email
    assert created_user.is_active is True

    # Verifica se o usuário foi realmente persistido no banco
    found_user = UserRepository.get_by_username(test_db, user_data.username)
    assert found_user is not None
    assert found_user.id == created_user.id


def test_update_active_status(test_db: Session, test_user: User):
    """Testa a atualização do status de ativo de um usuário"""
    # Verifica o status inicial
    assert test_user.is_active is True

    # Atualiza o status para False
    updated_user = UserRepository.update_active_status(test_db, test_user.id, False)

    # Verifica se o status foi atualizado
    assert updated_user is not None
    assert updated_user.is_active is False

    # Busca o usuário para confirmar a atualização no banco
    found_user = UserRepository.get_by_id(test_db, test_user.id)
    assert found_user.is_active is False


def test_update_active_status_not_found(test_db: Session):
    """Testa a atualização do status de um usuário inexistente"""
    # Tenta atualizar um usuário inexistente
    updated_user = UserRepository.update_active_status(test_db, 999, False)

    # Verifica que nenhum usuário foi atualizado
    assert updated_user is None


def test_delete(test_db: Session, test_user: User):
    """Testa a exclusão de um usuário"""
    # Exclui o usuário
    result = UserRepository.delete(test_db, test_user.id)

    # Verifica se a exclusão foi bem-sucedida
    assert result is True

    # Verifica se o usuário foi realmente excluído do banco
    found_user = UserRepository.get_by_id(test_db, test_user.id)
    assert found_user is None


def test_delete_not_found(test_db: Session):
    """Testa a exclusão de um usuário inexistente"""
    # Tenta excluir um usuário inexistente
    result = UserRepository.delete(test_db, 999)

    # Verifica que a exclusão falhou
    assert result is False