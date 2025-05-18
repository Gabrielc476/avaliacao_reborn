# repositories/dataset_repository.py
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from database.models.dataset import Dataset, InstrumentDataset
from database.models.instrument import Instrument
from database.schemas.dataset import DatasetCreate, CustomColumn
from repositories.instrument_repository import InstrumentRepository
from utils.instrument_plugins import InstrumentRegistry


class DatasetRepository:
    """
    Repositório para operações relacionadas a datasets
    """

    @staticmethod
    def get_by_id(db: Session, dataset_id: int) -> Optional[Dataset]:
        """Busca um dataset pelo ID"""
        return db.query(Dataset).filter(Dataset.id == dataset_id).first()

    @staticmethod
    def get_all_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Dataset]:
        """Busca todos os datasets de um proprietário"""
        return db.query(Dataset).filter(
            Dataset.owner_id == owner_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, dataset_data: DatasetCreate, owner_id: int) -> Dataset:
        """
        Cria um novo dataset e processa os instrumentos

        Args:
            db: Sessão do banco de dados
            dataset_data: Dados do dataset
            owner_id: ID do proprietário

        Returns:
            Dataset criado
        """
        # Criar o dataset básico
        db_dataset = Dataset(
            name=dataset_data.name,
            description=dataset_data.description,
            owner_id=owner_id,
            custom_columns=[col.dict() for col in dataset_data.custom_columns],
            data=dataset_data.data
        )

        db.add(db_dataset)
        db.commit()
        db.refresh(db_dataset)

        # Adicionar e processar instrumentos
        for code in dataset_data.instrument_codes:
            # Obter ou criar o instrumento
            instrument = InstrumentRepository.get_or_create(db, code, owner_id)

            # Obter o processador
            processor = InstrumentRegistry.get(code)

            # Extrair respostas
            responses = processor.extract_responses(dataset_data.data)

            # Processar as respostas
            results = processor.process(responses)

            # Criar a relação e armazenar os resultados
            instrument_dataset = InstrumentDataset(
                dataset_id=db_dataset.id,
                instrument_id=instrument.id,
                results=results,
                processed_at=datetime.utcnow()
            )

            db.add(instrument_dataset)

        db.commit()
        db.refresh(db_dataset)

        return db_dataset

    @staticmethod
    def update(db: Session, dataset_id: int, data: Dict[str, Any]) -> Optional[Dataset]:
        """Atualiza um dataset existente"""
        db_dataset = DatasetRepository.get_by_id(db, dataset_id)

        if db_dataset:
            # Atualizar os campos básicos
            for key, value in data.items():
                if key not in ['id', 'instruments'] and hasattr(db_dataset, key):
                    setattr(db_dataset, key, value)

            db.commit()
            db.refresh(db_dataset)

            # Se os dados foram atualizados, reprocessar os instrumentos
            if 'data' in data:
                DatasetRepository.reprocess_instruments(db, db_dataset)

        return db_dataset

    @staticmethod
    def reprocess_instruments(db: Session, dataset: Dataset) -> None:
        """
        Reprocessa os instrumentos de um dataset

        Args:
            db: Sessão do banco de dados
            dataset: Dataset a ser reprocessado
        """
        for instrument_dataset in dataset.instruments:
            # Obter o instrumento
            instrument = instrument_dataset.instrument

            # Obter o processador
            processor = InstrumentRegistry.get(instrument.code)

            # Extrair respostas
            responses = processor.extract_responses(dataset.data)

            # Processar as respostas
            results = processor.process(responses)

            # Atualizar os resultados
            instrument_dataset.results = results
            instrument_dataset.processed_at = datetime.utcnow()

        db.commit()

    @staticmethod
    def get_instrument_results(db: Session, dataset_id: int, instrument_code: str) -> Optional[Dict[str, Any]]:
        """
        Obtém os resultados de um instrumento específico

        Args:
            db: Sessão do banco de dados
            dataset_id: ID do dataset
            instrument_code: Código do instrumento

        Returns:
            Resultados do instrumento ou None se não encontrado
        """
        # Buscar o instrumento pelo código
        instrument = db.query(Instrument).filter(Instrument.code == instrument_code).first()

        if not instrument:
            return None

        # Buscar a relação entre o dataset e o instrumento
        instrument_dataset = db.query(InstrumentDataset).filter(
            InstrumentDataset.dataset_id == dataset_id,
            InstrumentDataset.instrument_id == instrument.id
        ).first()

        if not instrument_dataset:
            return None

        return {
            "instrument_code": instrument.code,
            "instrument_name": instrument.name,
            "processed_at": instrument_dataset.processed_at,
            "results": instrument_dataset.results
        }

    @staticmethod
    def delete(db: Session, dataset_id: int) -> bool:
        """Remove um dataset"""
        db_dataset = DatasetRepository.get_by_id(db, dataset_id)

        if db_dataset:
            db.delete(db_dataset)
            db.commit()
            return True

        return False