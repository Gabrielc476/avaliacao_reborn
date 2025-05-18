# raiz/database/models/questionnaire.py
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Isso será importado do connect.py na implementação real
Base = declarative_base()


class Questionnaire(Base):
    """
    Modelo para questionários psicológicos (como DASS-21)
    A estrutura do questionário (perguntas, escalas, etc.) é armazenada em JSON
    """
    __tablename__ = "questionnaires"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    structure = Column(JSON)  # Estrutura do questionário (perguntas, escalas, etc.)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relacionamentos
    owner = relationship("User", back_populates="questionnaires")
    table_questionnaires = relationship("TableQuestionnaire", back_populates="questionnaire")