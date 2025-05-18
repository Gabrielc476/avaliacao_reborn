# services/auth_service.py
from typing import Optional, Dict, Any
from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.models.user import User
from database.schemas.user import UserCreate
from repositories.user_repository import UserRepository
from utils.password import PasswordUtils
from utils.jwt import JWTUtils, TokenData


# Modelos Pydantic para tokens
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class AuthService:
    """
    Serviço para operações de autenticação
    Implementa a lógica de negócios de autenticação
    """

    def __init__(self, user_repository: UserRepository):
        """
        Inicializa o serviço com suas dependências

        Args:
            user_repository: Repositório de usuários
        """
        self.user_repository = user_repository

    async def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """
        Autentica um usuário pelo nome de usuário/email e senha

        Args:
            db: Sessão do banco de dados
            username: Nome de usuário ou email
            password: Senha em texto plano

        Returns:
            Usuário autenticado ou None se autenticação falhar
        """
        # Determina se é email ou username
        if '@' in username:
            user = self.user_repository.get_by_email(db, username)
        else:
            user = self.user_repository.get_by_username(db, username)

        if not user:
            return None

        if not PasswordUtils.verify_password(password, user.hashed_password):
            return None

        return user

    async def create_user(self, db: Session, user_data: UserCreate) -> User:
        """
        Cria um novo usuário

        Args:
            db: Sessão do banco de dados
            user_data: Dados do usuário a ser criado

        Returns:
            Usuário criado

        Raises:
            HTTPException: Se o nome de usuário ou email já estiver em uso
        """
        # Verificar se o username já existe
        if self.user_repository.get_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome de usuário já em uso"
            )

        # Verificar se o email já existe
        if self.user_repository.get_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já em uso"
            )

        # Criar hash da senha
        hashed_password = PasswordUtils.get_password_hash(user_data.password)

        # Criar usuário via repositório
        return self.user_repository.create(db, user_data, hashed_password)

    async def create_tokens(self, user: User) -> Token:
        """
        Cria tokens de acesso e atualização para um usuário

        Args:
            user: Usuário para o qual criar tokens

        Returns:
            Tokens de acesso e atualização
        """
        # Dados a serem incluídos no token
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        }

        # Criar token de acesso
        access_token = JWTUtils.create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=30)
        )

        # Criar token de atualização
        refresh_token = JWTUtils.create_refresh_token(data=token_data)

        # Retornar tokens formatados
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    async def get_current_user(self, db: Session, token: str) -> User:
        """
        Obtém o usuário atual a partir do token de acesso

        Args:
            db: Sessão do banco de dados
            token: Token JWT de acesso

        Returns:
            Usuário autenticado

        Raises:
            HTTPException: Se o token for inválido ou o usuário não for encontrado
        """
        # Verificar e decodificar o token
        token_data = JWTUtils.verify_token(token)

        # Buscar usuário no banco de dados
        user = self.user_repository.get_by_id(db, token_data.user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inativo",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    async def refresh_access_token(self, db: Session, refresh_token: str) -> Token:
        """
        Atualiza o token de acesso usando um token de atualização

        Args:
            db: Sessão do banco de dados
            refresh_token: Token de atualização

        Returns:
            Novos tokens de acesso e atualização

        Raises:
            HTTPException: Se o token de atualização for inválido
        """
        # Verificar e decodificar o token de atualização
        token_data = JWTUtils.verify_token(refresh_token)

        # Buscar usuário no banco de dados
        user = self.user_repository.get_by_id(db, token_data.user_id)

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado ou inativo",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Criar novos tokens
        return await self.create_tokens(user)


# Instância compartilhada do serviço de autenticação
# Não é um singleton verdadeiro, apenas uma instância global para conveniência
auth_service = AuthService(UserRepository())