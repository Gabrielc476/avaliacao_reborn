# routes/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.connect import db_connection
from database.schemas.user import UserCreate, User as UserSchema
from services.auth_service import auth_service, Token

# Criação do router para autenticação
router = APIRouter(
    prefix="/auth",
    tags=["autenticação"],
    responses={401: {"description": "Não autorizado"}},
)


@router.post("/register", response_model=UserSchema)
async def register(
        user_data: UserCreate,
        db: Session = Depends(db_connection.get_db)
):
    """
    Registra um novo usuário no sistema

    Args:
        user_data: Dados do usuário a ser registrado
        db: Sessão do banco de dados

    Returns:
        Usuário criado

    Raises:
        HTTPException: Se o nome de usuário ou email já estiver em uso
    """
    return await auth_service.create_user(db, user_data)

class LoginCredentials(BaseModel):
    username: str
    password: str
@router.post("/login", response_model=Token)
async def login(
        credentials: LoginCredentials,  # Modificado aqui
        db: Session = Depends(db_connection.get_db)
):
    """
    Faz login e obtém tokens de acesso e atualização

    Args:
        credentials: Credenciais de login (username e password)
        db: Sessão do banco de dados

    Returns:
        Tokens de acesso e atualização
    """
    user = await auth_service.authenticate_user(db, credentials.username, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await auth_service.create_tokens(user)


@router.post("/refresh", response_model=Token)
async def refresh_token(
        refresh_token: str,
        db: Session = Depends(db_connection.get_db)
):
    """
    Atualiza o token de acesso usando um token de atualização

    Args:
        refresh_token: Token de atualização
        db: Sessão do banco de dados

    Returns:
        Novos tokens de acesso e atualização

    Raises:
        HTTPException: Se o token de atualização for inválido
    """
    return await auth_service.refresh_access_token(db, refresh_token)


@router.get("/me", response_model=UserSchema)
async def get_current_user(
        request: Request,
        db: Session = Depends(db_connection.get_db)
):
    """
    Obtém o usuário atual (autenticado)

    Args:
        request: Requisição HTTP contendo o cabeçalho de autenticação
        db: Sessão do banco de dados

    Returns:
        Dados do usuário atual

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