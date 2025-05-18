# raiz/database/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Isso será importado do connect.py na implementação real
Base = declarative_base()


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

    # Relacionamentos
    custom_tables = relationship("CustomTable", back_populates="owner")
    questionnaires = relationship("Questionnaire", back_populates="owner")