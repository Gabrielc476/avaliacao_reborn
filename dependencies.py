# dependencies.py
from sqlalchemy.orm import Session
from fastapi import Depends, Request, HTTPException, status

from database.connect import db_connection
from database.models.user import User
from services.auth_service import auth_service


# Dependências comuns para as rotas da API

def get_db():
    """
    Dependência para obter uma sessão do banco de dados

    Yields:
        Sessão do banco de dados
    """
    db = db_connection.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
        request: Request,
        db: Session = Depends(get_db)
) -> User:
    """
    Dependência para obter o usuário autenticado atual

    Args:
        request: Requisição HTTP contendo o cabeçalho de autenticação
        db: Sessão do banco de dados

    Returns:
        Usuário autenticado

    Raises:
        HTTPException: Se o token for inválido ou usuário não for encontrado
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação ausente ou inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extrair token do cabeçalho
    token = auth_header.split(" ")[1]
    return await auth_service.get_current_user(db, token)