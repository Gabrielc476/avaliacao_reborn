# routes/dataset_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from database.connect import db_connection
from database.models import Dataset
from database.schemas.dataset import DatasetCreate, DatasetResponse, DatasetDetail, InstrumentResultsResponse
from services.dataset_service import dataset_service
from dependencies import get_current_user
from database.models.user import User

# Criação do router para conjuntos de dados
router = APIRouter(
    prefix="/datasets",
    tags=["datasets"],
    responses={401: {"description": "Não autorizado"}},
)

def format_dataset_response(dataset: Dataset) -> DatasetResponse:
    """Formata um objeto Dataset para o modelo de resposta esperado"""
    return DatasetResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
        owner_id=dataset.owner_id,
        custom_columns=dataset.custom_columns,
        row_count=len(dataset.data) if dataset.data else 0,
        instruments=[
            {
                "id": instr.instrument.id,
                "code": instr.instrument.code,
                "name": instr.instrument.name,
                "version": instr.instrument.version
            }
            for instr in dataset.instruments
        ]
    )

def format_dataset_detail(dataset: Dataset) -> DatasetDetail:
    """Formata um objeto Dataset para o modelo de resposta DatasetDetail"""
    response = format_dataset_response(dataset)
    return DatasetDetail(
        **response.dict(),
        data=dataset.data
    )
@router.get("/instruments", response_model=List[Dict[str, str]])
async def list_available_instruments():
    """
    Lista todos os instrumentos psicológicos disponíveis

    Returns:
        Lista de instrumentos disponíveis
    """
    return await dataset_service.list_available_instruments()


@router.post("/", response_model=DatasetResponse)
async def create_dataset(
        dataset_data: DatasetCreate,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Cria um novo conjunto de dados

    Args:
        dataset_data: Dados do conjunto de dados
        db: Sessão do banco de dados
        current_user: Usuário autenticado atual

    Returns:
        Conjunto de dados criado
    """
    dataset = await dataset_service.create_dataset(db, dataset_data, current_user)
    return format_dataset_response(dataset)


@router.get("/", response_model=List[DatasetResponse])
async def get_datasets(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtém todos os conjuntos de dados do usuário atual

    Args:
        skip: Número de registros a serem pulados
        limit: Número máximo de registros a serem retornados
        db: Sessão do banco de dados
        current_user: Usuário autenticado atual

    Returns:
        Lista de conjuntos de dados
    """
    return await dataset_service.get_user_datasets(db, current_user, skip, limit)


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
        dataset_id: int,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtém informações básicas de um conjunto de dados pelo ID

    Args:
        dataset_id: ID do conjunto de dados
        db: Sessão do banco de dados
        current_user: Usuário autenticado atual

    Returns:
        Conjunto de dados encontrado
    """
    dataset = await dataset_service.get_dataset(db, dataset_id, current_user)
    # Formatar a resposta
    return format_dataset_response(dataset)


@router.get("/{dataset_id}/detail", response_model=DatasetDetail)
async def get_dataset_detail(
        dataset_id: int,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtém detalhes completos de um conjunto de dados, incluindo os dados

    Args:
        dataset_id: ID do conjunto de dados
        db: Sessão do banco de dados
        current_user: Usuário autenticado atual

    Returns:
        Conjunto de dados com detalhes completos
    """
    dataset = await dataset_service.get_dataset(db, dataset_id, current_user)
    return format_dataset_detail(dataset)


@router.get("/{dataset_id}/instruments/{instrument_code}/results", response_model=InstrumentResultsResponse)
async def get_instrument_results(
        dataset_id: int,
        instrument_code: str,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtém os resultados processados de um instrumento específico

    Args:
        dataset_id: ID do conjunto de dados
        instrument_code: Código do instrumento (ex: "DASS21")
        db: Sessão do banco de dados
        current_user: Usuário autenticado atual

    Returns:
        Resultados processados do instrumento
    """
    return await dataset_service.get_instrument_results(db, dataset_id, instrument_code, current_user)


@router.put("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
        dataset_id: int,
        dataset_data: DatasetCreate,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Atualiza um conjunto de dados existente

    Args:
        dataset_id: ID do conjunto de dados
        dataset_data: Novos dados
        db: Sessão do banco de dados
        current_user: Usuário autenticado atual

    Returns:
        Conjunto de dados atualizado
    """
    # Converter para dict e atualizar
    update_data = dataset_data.dict()
    dataset = await dataset_service.update_dataset(db, dataset_id, update_data, current_user)

    return format_dataset_response(dataset)


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
        dataset_id: int,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Remove um conjunto de dados

    Args:
        dataset_id: ID do conjunto de dados
        db: Sessão do banco de dados
        current_user: Usuário autenticado atual
    """
    await dataset_service.delete_dataset(db, dataset_id, current_user)
    return None