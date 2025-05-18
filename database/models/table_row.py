# raiz/database/models/table_row.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Isso será importado do connect.py na implementação real
Base = declarative_base()


class TableRow(Base):
    """
    Modelo para linhas de tabelas personalizadas
    Cada linha representa um registro de dados na tabela
    """
    __tablename__ = "table_rows"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("custom_tables.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    table = relationship("CustomTable", back_populates="rows")
    cell_values = relationship("CellValue", back_populates="row")
    questionnaire_responses = relationship("QuestionnaireResponse", back_populates="row")


class CellValue(Base):
    """
    Modelo para valores de células
    Armazena o valor de cada célula (interseção de linha e coluna) na tabela
    """
    __tablename__ = "cell_values"

    id = Column(Integer, primary_key=True, index=True)
    row_id = Column(Integer, ForeignKey("table_rows.id"))
    column_id = Column(Integer, ForeignKey("table_columns.id"))
    value = Column(String)  # Valor armazenado como string, convertido conforme o tipo

    # Relacionamentos
    row = relationship("TableRow", back_populates="cell_values")
    column = relationship("TableColumn", back_populates="cell_values")


class QuestionnaireResponse(Base):
    """
    Modelo para respostas de questionário
    Armazena as respostas e pontuações de um questionário para cada linha da tabela
    """
    __tablename__ = "questionnaire_responses"

    id = Column(Integer, primary_key=True, index=True)
    row_id = Column(Integer, ForeignKey("table_rows.id"))
    questionnaire_id = Column(Integer, ForeignKey("questionnaires.id"))
    responses = Column(JSON)  # Respostas armazenadas em formato JSON
    scores = Column(JSON)  # Pontuações calculadas em formato JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    row = relationship("TableRow", back_populates="questionnaire_responses")