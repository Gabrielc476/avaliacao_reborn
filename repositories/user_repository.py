# repositories/user_repository.py
from typing import Optional, List
from sqlalchemy.orm import Session
from database.models.user import User
from database.schemas.user import UserCreate


class UserRepository:
    """
    Repositório para operações de acesso a dados relacionadas a usuários
    Segue o padrão Repository para encapsular a lógica de acesso a dados
    """

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Busca um usuário pelo ID

        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário a ser buscado

        Returns:
            Usuário encontrado ou None
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """
        Busca um usuário pelo nome de usuário

        Args:
            db: Sessão do banco de dados
            username: Nome de usuário a ser buscado

        Returns:
            Usuário encontrado ou None
        """
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """
        Busca um usuário pelo email

        Args:
            db: Sessão do banco de dados
            email: Email a ser buscado

        Returns:
            Usuário encontrado ou None
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Busca todos os usuários com paginação

        Args:
            db: Sessão do banco de dados
            skip: Número de registros a serem pulados (para paginação)
            limit: Número máximo de registros a serem retornados

        Returns:
            Lista de usuários
        """
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, user_data: UserCreate, hashed_password: str) -> User:
        """
        Cria um novo usuário

        Args:
            db: Sessão do banco de dados
            user_data: Dados do usuário a ser criado
            hashed_password: Senha já com hash

        Returns:
            Usuário criado
        """
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def update_active_status(db: Session, user_id: int, is_active: bool) -> Optional[User]:
        """
        Atualiza o status de ativo de um usuário

        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário a ser atualizado
            is_active: Novo status de ativo

        Returns:
            Usuário atualizado ou None se não encontrado
        """
        db_user = UserRepository.get_by_id(db, user_id)

        if db_user:
            db_user.is_active = is_active
            db.commit()
            db.refresh(db_user)

        return db_user

    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        """
        Remove um usuário do banco de dados

        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário a ser removido

        Returns:
            True se o usuário foi removido, False caso contrário
        """
        db_user = UserRepository.get_by_id(db, user_id)

        if db_user:
            db.delete(db_user)
            db.commit()
            return True

        return False