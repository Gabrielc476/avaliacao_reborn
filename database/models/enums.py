# raiz/database/models/enums.py
import enum
from sqlalchemy import Enum

# Enumeração para tipos de dados disponíveis
class DataType(enum.Enum):
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