# raiz/database/schemas/column.py
from pydantic import BaseModel
from typing import Optional, List
from .data_types import DataType, SelectOption, FieldValidation

# Esquemas de Coluna de Tabela
class TableColumnBase(BaseModel):
    name: str
    description: Optional[str] = None
    data_type: DataType
    is_required: bool = False
    options: Optional[List[SelectOption]] = None
    order: int
    validation: Optional[FieldValidation] = None

class TableColumnCreate(TableColumnBase):
    table_id: int

class TableColumn(TableColumnBase):
    id: int
    table_id: int

    class Config:
        orm_mode = True