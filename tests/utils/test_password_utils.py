# tests/utils/test_password_utils.py
import pytest
from utils.password import PasswordUtils


def test_password_hash():
    """Testa a geração de hash de senha"""
    # Senha de teste
    password = "testpassword"

    # Gera o hash
    hashed_password = PasswordUtils.get_password_hash(password)

    # Verifica que o hash foi gerado e é diferente da senha original
    assert hashed_password is not None
    assert hashed_password != password
    assert len(hashed_password) > 20  # Hash deve ser uma string longa


def test_verify_password_correct():
    """Testa a verificação de senha correta"""
    # Senha de teste
    password = "testpassword"

    # Gera o hash
    hashed_password = PasswordUtils.get_password_hash(password)

    # Verifica a senha correta
    assert PasswordUtils.verify_password(password, hashed_password) is True


def test_verify_password_incorrect():
    """Testa a verificação de senha incorreta"""
    # Senha de teste
    password = "testpassword"
    wrong_password = "wrongpassword"

    # Gera o hash
    hashed_password = PasswordUtils.get_password_hash(password)

    # Verifica a senha incorreta
    assert PasswordUtils.verify_password(wrong_password, hashed_password) is False


def test_different_passwords_generate_different_hashes():
    """Testa que senhas diferentes geram hashes diferentes"""
    # Senhas de teste
    password1 = "testpassword1"
    password2 = "testpassword2"

    # Gera os hashes
    hash1 = PasswordUtils.get_password_hash(password1)
    hash2 = PasswordUtils.get_password_hash(password2)

    # Verifica que os hashes são diferentes
    assert hash1 != hash2


def test_same_password_generates_different_hashes():
    """Testa que a mesma senha gera hashes diferentes (devido ao salt)"""
    # Senha de teste
    password = "testpassword"

    # Gera dois hashes para a mesma senha
    hash1 = PasswordUtils.get_password_hash(password)
    hash2 = PasswordUtils.get_password_hash(password)

    # Verifica que os hashes são diferentes, mas ambos funcionam para verificação
    assert hash1 != hash2
    assert PasswordUtils.verify_password(password, hash1) is True
    assert PasswordUtils.verify_password(password, hash2) is True