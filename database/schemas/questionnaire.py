# database/schemas/questionnaire.py
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class QuestionItem(BaseModel):
    """Item de questão de um questionário"""
    id: str  # Identificador único para a questão
    text: str  # Texto da questão
    type: str  # Tipo de questão (text, number, select_one, etc.)
    required: bool = True
    options: Optional[List[Dict[str, Any]]] = None  # Opções para tipos select


class QuestionnaireStructure(BaseModel):
    """Estrutura de um questionário"""
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    questions: List[QuestionItem]
    sections: Optional[List[Dict[str, Any]]] = None  # Seções opcionais para agrupar questões


class QuestionnaireBase(BaseModel):
    """Base para schemas de questionário"""
    name: str
    description: Optional[str] = None


class QuestionnaireCreate(QuestionnaireBase):
    """Schema para criação de questionário"""
    structure: Dict[str, Any]  # Estrutura do questionário (perguntas, escalas, etc.)


class Questionnaire(QuestionnaireBase):
    """Schema para resposta completa de questionário"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    owner_id: int
    structure: Dict[str, Any]

    class Config:
        from_attributes = True  # Updated from orm_mode=True for Pydantic v2



class QuestionnaireUpdate(BaseModel):
    """Schema para atualização de questionário"""
    name: Optional[str] = None
    description: Optional[str] = None
    structure: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class QuestionnaireResponse(BaseModel):
    """Schema para respostas a um questionário"""
    questionnaire_id: int
    responses: Dict[str, Any]  # Respostas para as questões (id_questão: resposta)
    metadata: Optional[Dict[str, Any]] = None  # Metadados adicionais


class QuestionnaireResponseResult(QuestionnaireResponse):
    """Schema para resultado de resposta a questionário"""
    id: int
    created_at: datetime
    respondent_id: Optional[int] = None  # ID do respondente se autenticado

    class Config:
        from_attributes = True  # Updated from orm_mode=True for Pydantic v2