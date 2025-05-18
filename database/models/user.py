# database/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connect import Base


class User(Base):
    """
    Modelo para usuários do sistema
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    questionnaires = relationship("Questionnaire", back_populates="owner")
    datasets = relationship("Dataset", back_populates="owner")
    instruments = relationship("Instrument", back_populates="owner")