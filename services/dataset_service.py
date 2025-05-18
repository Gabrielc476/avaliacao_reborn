# services/dataset_service.py
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from database.models.user import User
from database.models.dataset import Dataset
from database.schemas.dataset import DatasetCreate, DatasetResponse, DatasetDetail, InstrumentResultsResponse
from repositories.dataset_repository import DatasetRepository
from utils.instrument_plugins import InstrumentRegistry


class DatasetService:
    """
    Serviço para operações relacionadas a conjuntos de dados
    """

    def __init__(self, dataset_repository: DatasetRepository):
        """Inicializa o serviço com suas dependências"""
        self.dataset_repository = dataset_repository

    async def create_dataset(self, db: Session, dataset_data: DatasetCreate, current_user: User) -> Dataset:
        """
        Cria um novo conjunto de dados e processa os instrumentos

        Args:
            db: Sessão do banco de dados
            dataset_data: Dados do conjunto de dados
            current_user: Usuário atual

        Returns:
            Conjunto de dados criado
        """
        # Validar códigos de instrumentos
        for code in dataset_data.instrument_codes:
            try:
                InstrumentRegistry.get(code)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )

        # Criar o dataset
        return self.dataset_repository.create(db, dataset_data, current_user.id)

    async def get_dataset(self, db: Session, dataset_id: int, current_user: User) -> Dataset:
        """Obtém um conjunto de dados pelo ID"""
        dataset = self.dataset_repository.get_by_id(db, dataset_id)

        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conjunto de dados não encontrado"
            )

        if dataset.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar este conjunto de dados"
            )

        return dataset

    async def get_instrument_results(self, db: Session, dataset_id: int, instrument_code: str,
                                     current_user: User) -> InstrumentResultsResponse:
        """
        Obtém os resultados processados de um instrumento específico

        Args:
            db: Sessão do banco de dados
            dataset_id: ID do conjunto de dados
            instrument_code: Código do instrumento
            current_user: Usuário atual

        Returns:
            Resultados processados do instrumento

        Raises:
            HTTPException: Se o dataset não for encontrado ou o instrumento não estiver incluído
        """
        # Verificar se o dataset existe e pertence ao usuário
        await self.get_dataset(db, dataset_id, current_user)

        # Obter os resultados
        results = self.dataset_repository.get_instrument_results(db, dataset_id, instrument_code)

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resultados para o instrumento '{instrument_code}' não encontrados"
            )

        return InstrumentResultsResponse(**results)

    async def get_user_datasets(self, db: Session, current_user: User, skip: int = 0, limit: int = 100) -> List[
        Dataset]:
        """Obtém todos os conjuntos de dados de um usuário"""
        return self.dataset_repository.get_all_by_owner(db, current_user.id, skip, limit)

    async def update_dataset(self, db: Session, dataset_id: int, data: Dict[str, Any], current_user: User) -> Dataset:
        """Atualiza um conjunto de dados existente"""
        # Verificar se o dataset existe e pertence ao usuário
        await self.get_dataset(db, dataset_id, current_user)

        # Atualizar o dataset
        updated_dataset = self.dataset_repository.update(db, dataset_id, data)

        if not updated_dataset:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar conjunto de dados"
            )

        return updated_dataset

    async def delete_dataset(self, db: Session, dataset_id: int, current_user: User) -> bool:
        """Remove um conjunto de dados"""
        # Verificar se o dataset existe e pertence ao usuário
        await self.get_dataset(db, dataset_id, current_user)

        # Remover o dataset
        if not self.dataset_repository.delete(db, dataset_id):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao remover conjunto de dados"
            )

        return True

    async def list_available_instruments(self) -> List[Dict[str, str]]:
        """Lista todos os instrumentos disponíveis"""
        return InstrumentRegistry.list_all()


# Instância compartilhada do serviço
dataset_service = DatasetService(DatasetRepository())