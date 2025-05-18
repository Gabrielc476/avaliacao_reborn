# raiz/database/schemas/response.py
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

# Esquemas para Respostas de Questionário
class QuestionnaireResponseBase(BaseModel):
    responses: Dict[str, Any]
    scores: Optional[Dict[str, Any]] = None

class QuestionnaireResponseCreate(QuestionnaireResponseBase):
    questionnaire_id: int
    row_id: int

class QuestionnaireResponse(QuestionnaireResponseBase):
    id: int
    row_id: int
    questionnaire_id: int
    created_at: datetime

    class Config:
        orm_mode = True