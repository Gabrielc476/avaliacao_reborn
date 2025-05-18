# raiz/database/models/custom_table.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connect import Base


class CustomTable(Base):
    """
    Modelo para tabelas personalizadas criadas pelos usuários
    Cada tabela pode ter diferentes conjuntos de colunas definidas pelo usuário
    """
    __tablename__ = "custom_tables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relacionamentos - usar string para evitar circular imports
    owner = relationship("database.models.user.User", back_populates="custom_tables")
    columns = relationship("database.models.table_column.TableColumn", back_populates="table")
    rows = relationship("database.models.table_row.TableRow", back_populates="table")
    table_questionnaires = relationship("TableQuestionnaire", back_populates="table")


class TableQuestionnaire(Base):
    """
    Modelo de relacionamento entre tabelas personalizadas e questionários
    Uma tabela pode incluir múltiplos questionários e um questionário pode
    ser usado em múltiplas tabelas
    """
    __tablename__ = "table_questionnaires"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("custom_tables.id"))
    questionnaire_id = Column(Integer, ForeignKey("questionnaires.id"))

    # Relacionamentos - usar string para evitar circular imports
    table = relationship("CustomTable", back_populates="table_questionnaires")
    questionnaire = relationship("database.models.questionnaire.Questionnaire", back_populates="table_questionnaires")