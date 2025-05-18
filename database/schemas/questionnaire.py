# raiz/database/schemas/questionnaire.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# Esquemas de Questionário
class QuestionnaireBase(BaseModel):
    name: str
    description: Optional[str] = None

class QuestionnaireCreate(QuestionnaireBase):
    structure: Dict[str, Any]
    owner_id: int

class Questionnaire(QuestionnaireBase):
    id: int
    created_at: datetime
    is_active: bool
    owner_id: int
    structure: Dict[str, Any]

    class Config:
        orm_mode = True