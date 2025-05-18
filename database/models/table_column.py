# raiz/database/models/table_column.py
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from .enums import DataType

# Isso será importado do connect.py na implementação real
Base = declarative_base()


class TableColumn(Base):
    """
    Modelo para colunas de tabelas personalizadas
    Define o nome, tipo de dados e validações para cada coluna de uma tabela personalizada
    """
    __tablename__ = "table_columns"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("custom_tables.id"))
    name = Column(String)  # Nome da coluna (ex: "sexo", "curso", "profissão")
    description = Column(Text, nullable=True)
    data_type = Column(Enum(DataType), nullable=False)  # Tipo de dados usando enumeração
    is_required = Column(Boolean, default=False)
    options = Column(JSON, nullable=True)  # Para colunas do tipo seleção
    order = Column(Integer)  # Ordem de exibição

    # Campos para validação específica de cada tipo de dado
    validation = Column(JSON, nullable=True)  # Regras de validação específicas do tipo

    # Relacionamentos
    table = relationship("CustomTable", back_populates="columns")
    cell_values = relationship("CellValue", back_populates="column")