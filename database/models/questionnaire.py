# raiz/database/models/questionnaire.py
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connect import Base


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

    # Relacionamentos - usar string para evitar circular imports
    owner = relationship("database.models.user.User", back_populates="questionnaires")
    table_questionnaires = relationship("database.models.custom_table.TableQuestionnaire", back_populates="questionnaire")