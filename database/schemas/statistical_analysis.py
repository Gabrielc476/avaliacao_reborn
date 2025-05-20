# database/schemas/statistical_analysis.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class AnalysisType(str, Enum):
    """Tipos de análise estatística disponíveis"""
    DESCRIPTIVE = "descriptive"
    RELIABILITY = "reliability"
    COMPARATIVE = "comparative"
    CORRELATION = "correlation"
    LONGITUDINAL = "longitudinal"
    MANOVA = "manova"


class StatisticalAnalysisCreate(BaseModel):
    """Esquema para criação de uma análise estatística"""
    name: str
    description: Optional[str] = None
    analysis_type: AnalysisType
    instrument_code: str
    scales: List[str]
    primary_dataset_id: int
    secondary_dataset_id: Optional[int] = None
    parameters: Dict[str, Any]


class StatisticalAnalysisUpdate(BaseModel):
    """Esquema para atualização de uma análise estatística"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_archived: Optional[bool] = None
    parameters: Optional[Dict[str, Any]] = None


class StatisticalAnalysisResponse(BaseModel):
    """Esquema para resposta básica de análise estatística"""
    id: int
    name: str
    description: Optional[str]
    analysis_type: str
    instrument_code: str
    scales: List[str]
    primary_dataset_id: int
    secondary_dataset_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    owner_id: int
    is_archived: bool
    parameters: Dict[str, Any]

    class Config:
        from_attributes = True  # Para Pydantic v2


class StatisticalAnalysisDetail(StatisticalAnalysisResponse):
    """Esquema para resposta detalhada de análise estatística, incluindo resultados"""
    results: Dict[str, Any]

    class Config:
        from_attributes = True  # Para Pydantic v2


# Esquemas específicos para diferentes tipos de análise

class DescriptiveAnalysisParameters(BaseModel):
    """Parâmetros para análise descritiva"""
    scale: str
    include_categories: Optional[bool] = True
    include_distribution: Optional[bool] = True


class ReliabilityAnalysisParameters(BaseModel):
    """Parâmetros para análise de confiabilidade"""
    include_item_correlations: Optional[bool] = True


class ComparativeAnalysisParameters(BaseModel):
    """Parâmetros para análise comparativa"""
    scale: str
    group_field: str
    group_values: List[Any]


class ManovaAnalysisParameters(BaseModel):
    """Parâmetros para análise MANOVA"""
    scales: List[str]
    group_field: Optional[str] = None


class CorrelationAnalysisParameters(BaseModel):
    """Parâmetros para análise correlacional"""
    scales: List[str]
    secondary_instrument_code: Optional[str] = None
    secondary_scale: Optional[str] = None


class LongitudinalAnalysisParameters(BaseModel):
    """Parâmetros para análise longitudinal"""
    scale: str
    time_points: Optional[List[str]] = None  # Para rotular pontos de tempo
    secondary_dataset_id: int