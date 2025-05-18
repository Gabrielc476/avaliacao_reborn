# database/models/questionnaire.py
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connect import Base


class Questionnaire(Base):
    """
    Modelo para questionários psicológicos genéricos

    Este modelo permite definir questionários personalizados que não
    estão implementados como instrumentos no sistema de plugins.
    A estrutura do questionário (perguntas, escalas, etc.) é armazenada em JSON.

    Nota: Para instrumentos padronizados com regras de pontuação específicas,
    utilize o modelo Instrument e o sistema de plugins.
    """
    __tablename__ = "questionnaires"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    structure = Column(JSON)  # Estrutura do questionário (perguntas, escalas, etc.)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relacionamentos
    owner = relationship("User", back_populates="questionnaires")

    # Mapeamento para JSON
    def to_dict(self):
        """Converte o modelo para um dicionário"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "structure": self.structure,
            "owner_id": self.owner_id
        }