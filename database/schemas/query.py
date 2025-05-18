# raiz/database/schemas/query.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from .row import TableRowDetail

# Esquemas para consultas e relatórios
class TableDataFilter(BaseModel):
    column_id: int
    operator: str  # "eq", "neq", "gt", "lt", "contains", "between", etc.
    value: Any
    value2: Optional[Any] = None  # Para operadores como "between"

class TableDataQuery(BaseModel):
    table_id: int
    filters: Optional[List[TableDataFilter]] = None
    sort_by: Optional[List[Dict[str, str]]] = None  # [{column_id: 1, direction: "asc"}]
    page: int = 1
    page_size: int = 50

class TableDataResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[TableRowDetail]

# Esquema para exportação de dados
class ExportTableDataRequest(BaseModel):
    table_id: int
    filters: Optional[List[TableDataFilter]] = None
    format: str = "csv"  # "csv", "excel", "json"
    columns: Optional[List[int]] = None  # IDs das colunas a serem exportadas