# raiz/database/schemas/table.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from .questionnaire import Questionnaire
from .column import TableColumn

# Esquemas de Tabela Customizada
class CustomTableBase(BaseModel):
    name: str
    description: Optional[str] = None

class CustomTableCreate(CustomTableBase):
    owner_id: int
    questionnaire_ids: Optional[List[int]] = None

class CustomTable(CustomTableBase):
    id: int
    created_at: datetime
    updated_at: datetime
    owner_id: int

    class Config:
        orm_mode = True

class CustomTableDetail(CustomTable):
    columns: List[TableColumn]
    questionnaires: List[Questionnaire]

    class Config:
        orm_mode = True