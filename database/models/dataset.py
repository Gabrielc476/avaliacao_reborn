# database/models/dataset.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connect import Base


class Dataset(Base):
    """
    Modelo para conjuntos de dados com instrumentos integrados
    """
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Metadados sobre as colunas personalizadas
    custom_columns = Column(JSON)

    # Os dados brutos em formato JSON (array de objetos)
    data = Column(JSON)

    # Relacionamentos
    owner = relationship("User", back_populates="datasets")
    instruments = relationship("InstrumentDataset", back_populates="dataset")


class InstrumentDataset(Base):
    """
    Modelo para relacionamento entre instrumentos e datasets
    com armazenamento dos resultados processados
    """
    __tablename__ = "instrument_datasets"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    instrument_id = Column(Integer, ForeignKey("instruments.id"))

    # Resultados do instrumento após correção
    results = Column(JSON, nullable=True)

    # Timestamp da última correção
    processed_at = Column(DateTime, nullable=True)

    # Relacionamentos
    dataset = relationship("Dataset", back_populates="instruments")
    instrument = relationship("Instrument", back_populates="datasets")