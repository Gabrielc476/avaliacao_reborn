# raiz/database/models/custom_table.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Isso será importado do connect.py na implementação real
Base = declarative_base()


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

    # Relacionamentos
    owner = relationship("User", back_populates="custom_tables")
    columns = relationship("TableColumn", back_populates="table")
    rows = relationship("TableRow", back_populates="table")
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

    # Relacionamentos
    table = relationship("CustomTable", back_populates="table_questionnaires")
    questionnaire = relationship("Questionnaire", back_populates="table_questionnaires")