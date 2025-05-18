# raiz/database/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connect import Base


class User(Base):
    """
    Modelo para usuários do sistema (administradores) que podem criar
    tabelas e questionários
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos - usar string para evitar circular imports
    custom_tables = relationship("database.models.custom_table.CustomTable", back_populates="owner")
    questionnaires = relationship("database.models.questionnaire.Questionnaire", back_populates="owner")