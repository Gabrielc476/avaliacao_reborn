# database/models/statistical_analysis.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connect import Base


class StatisticalAnalysis(Base):
    """
    Modelo para armazenar resultados de análises estatísticas realizadas em datasets.
    """
    __tablename__ = "statistical_analyses"

    id = Column(Integer, primary_key=True, index=True)

    # Tipo de análise (descritiva, correlação, comparativa, etc.)
    analysis_type = Column(String, index=True)

    # Código do instrumento analisado
    instrument_code = Column(String, index=True)

    # Nome da(s) escala(s) analisada(s)
    scales = Column(JSON)  # Lista de strings

    # Referências a datasets
    primary_dataset_id = Column(Integer, ForeignKey("datasets.id"), index=True)
    secondary_dataset_id = Column(Integer, nullable=True)  # Para análises longitudinais

    # Parâmetros da análise
    parameters = Column(JSON)  # Parâmetros específicos da análise (ex: grupo de comparação)

    # Resultados da análise
    results = Column(JSON)  # Resultados detalhados

    # Metadados
    name = Column(String)  # Nome da análise
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_archived = Column(Boolean, default=False)  # Para "excluir" logicamente

    # Relacionamentos
    owner = relationship("User", backref="statistical_analyses")
    primary_dataset = relationship("Dataset", foreign_keys=[primary_dataset_id])

    