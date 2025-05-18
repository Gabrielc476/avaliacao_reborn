# raiz/database/schemas/row.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

# Esquemas para Valores de Células
class CellValueBase(BaseModel):
    value: str

class CellValueCreate(CellValueBase):
    column_id: int

class CellValue(CellValueBase):
    id: int
    row_id: int
    column_id: int

    class Config:
        orm_mode = True

# Esquemas para Linhas de Tabela
class TableRowBase(BaseModel):
    pass

class TableRowCreate(TableRowBase):
    table_id: int
    values: List[CellValueCreate]
    questionnaire_responses: Optional[Dict[int, Dict[str, Any]]] = None

class TableRow(TableRowBase):
    id: int
    table_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TableRowDetail(TableRow):
    values: List[CellValue]

    class Config:
        orm_mode = True