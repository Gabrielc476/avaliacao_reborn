# repositories/instrument_repository.py
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from database.models.instrument import Instrument
from utils.instrument_plugins import InstrumentRegistry


class InstrumentRepository:
    """
    Repositório para operações relacionadas a instrumentos
    """

    @staticmethod
    def get_by_id(db: Session, instrument_id: int) -> Optional[Instrument]:
        """Busca um instrumento pelo ID"""
        return db.query(Instrument).filter(Instrument.id == instrument_id).first()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Instrument]:
        """Busca um instrumento pelo código"""
        return db.query(Instrument).filter(Instrument.code == code).first()

    @staticmethod
    def create_from_processor(db: Session, code: str, owner_id: int) -> Instrument:
        """
        Cria um instrumento a partir de um processador registrado

        Args:
            db: Sessão do banco de dados
            code: Código do instrumento
            owner_id: ID do proprietário

        Returns:
            Instrumento criado

        Raises:
            ValueError: Se o processador não for encontrado
        """
        # Obter o processador
        processor = InstrumentRegistry.get(code)

        # Criar o instrumento
        instrument = Instrument(
            code=processor.code,
            name=processor.name,
            description=processor.description,
            structure=processor.structure,
            version=processor.version,
            is_active=True,
            owner_id=owner_id
        )

        db.add(instrument)
        db.commit()
        db.refresh(instrument)

        return instrument

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Instrument]:
        """Busca todos os instrumentos"""
        return db.query(Instrument).offset(skip).limit(limit).all()

    @staticmethod
    def get_or_create(db: Session, code: str, owner_id: int) -> Instrument:
        """
        Busca um instrumento pelo código ou cria se não existir
        """
        instrument = InstrumentRepository.get_by_code(db, code)

        if not instrument:
            instrument = InstrumentRepository.create_from_processor(db, code, owner_id)

        return instrument