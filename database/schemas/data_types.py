# raiz/database/schemas/data_types.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

# Enumeração para tipos de dados
class DataType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    SELECT_ONE = "select_one"
    SELECT_MULTIPLE = "select_multiple"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    LONG_TEXT = "long_text"
    SCALE = "scale"

# Opção para os campos do tipo SELECT
class SelectOption(BaseModel):
    label: str
    value: str

# Validação para campos numéricos
class NumberValidation(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None

# Validação para campos de data
class DateValidation(BaseModel):
    min_date: Optional[datetime] = None
    max_date: Optional[datetime] = None
    format: Optional[str] = None

# Validação para campos de escala
class ScaleValidation(BaseModel):
    min: int
    max: int
    step: int = 1
    labels: Optional[Dict[int, str]] = None

# Validação agregada para todos os tipos de campos
class FieldValidation(BaseModel):
    number: Optional[NumberValidation] = None
    date: Optional[DateValidation] = None
    scale: Optional[ScaleValidation] = None
    text: Optional[Dict[str, Any]] = None  # Pode incluir regex, min_length, max_length
    select: Optional[Dict[str, Any]] = None  # Pode incluir min_selections, max_selections