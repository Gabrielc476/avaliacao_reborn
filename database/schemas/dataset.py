# database/schemas/dataset.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class CustomColumn(BaseModel):
    """Definição de uma coluna personalizada"""
    name: str
    data_type: str
    description: Optional[str] = None
    required: bool = False


class DatasetCreate(BaseModel):
    """Esquema para criação de um conjunto de dados"""
    name: str
    description: Optional[str] = None
    custom_columns: List[CustomColumn]
    instrument_codes: List[str]  # Códigos dos instrumentos incluídos
    data: List[Dict[str, Any]]  # Dados brutos


class InstrumentInfo(BaseModel):
    """Informações básicas sobre um instrumento"""
    id: int
    code: str
    name: str
    version: str


class DatasetResponse(BaseModel):
    """Resposta com informações do conjunto de dados"""
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    owner_id: int
    custom_columns: List[CustomColumn]
    instruments: List[InstrumentInfo]
    row_count: int

    class Config:
        orm_mode = True


class DatasetDetail(DatasetResponse):
    """Resposta detalhada incluindo os dados"""
    data: List[Dict[str, Any]]

    class Config:
        orm_mode = True


class InstrumentResultsResponse(BaseModel):
    """Resposta com resultados de um instrumento"""
    instrument_code: str
    instrument_name: str
    processed_at: Optional[datetime] = None
    results: List[Dict[str, Any]]

    class Config:
        orm_mode = True