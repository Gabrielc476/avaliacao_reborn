# database/models/instrument.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connect import Base


class Instrument(Base):
    """
    Modelo para instrumentos de avaliação psicológica
    """
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)  # Ex: "DASS21", "IHS2"
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    structure = Column(JSON)  # Estrutura do instrumento (perguntas, escalas, etc.)
    version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relacionamentos
    owner = relationship("User", back_populates="instruments")
    datasets = relationship("InstrumentDataset", back_populates="instrument")