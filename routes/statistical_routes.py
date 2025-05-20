# routes/statistical_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from database.connect import db_connection
from database.models.user import User
from database.schemas.statistical_analysis import (
    StatisticalAnalysisCreate, StatisticalAnalysisUpdate,
    StatisticalAnalysisResponse, StatisticalAnalysisDetail,
    DescriptiveAnalysisParameters, ReliabilityAnalysisParameters,
    ComparativeAnalysisParameters, ManovaAnalysisParameters,
    CorrelationAnalysisParameters, LongitudinalAnalysisParameters,
    AnalysisType
)
from dependencies import get_current_user
from services.statistical_service import statistical_service
from repositories.statistical_repository import StatisticalRepository
from repositories.dataset_repository import DatasetRepository

router = APIRouter(
    prefix="/statistical",
    tags=["statistical_analysis"],
    responses={401: {"description": "Não autorizado"}}
)


# ---------- Rotas para análises descritivas ----------

@router.post("/descriptive", response_model=StatisticalAnalysisResponse)
async def create_descriptive_analysis(
        analysis: StatisticalAnalysisCreate,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Cria uma análise estatística descritiva para uma escala específica
    """
    # Verificar se o tipo de análise está correto
    if analysis.analysis_type != AnalysisType.DESCRIPTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de análise incorreto. Deve ser 'descriptive'."
        )

    # Validar parâmetros
    if "scale" not in analysis.parameters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O parâmetro 'scale' é obrigatório para análise descritiva."
        )

    # Verificar se o dataset existe e pertence ao usuário
    dataset_repo = DatasetRepository()
    dataset = dataset_repo.get_by_id(db, analysis.primary_dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset não encontrado."
        )

    if dataset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este dataset."
        )

    try:
        # Calcular estatísticas descritivas
        scale = analysis.parameters["scale"]
        results = {
            "descriptive_stats": statistical_service.descriptive_statistics(
                db, analysis.primary_dataset_id, analysis.instrument_code, scale
            )
        }

        # Se solicitado, incluir distribuição de categorias
        if analysis.parameters.get("include_categories", True):
            try:
                results["category_distribution"] = statistical_service.category_analysis(
                    db, analysis.primary_dataset_id, analysis.instrument_code, scale
                )
            except Exception as e:
                # Se houver erro na análise de categoria, apenas ignorar
                results["category_distribution_error"] = str(e)

        # Se solicitado, incluir distribuição de pontuações
        if analysis.parameters.get("include_distribution", True):
            try:
                results["score_distribution"] = statistical_service.score_distribution(
                    db, analysis.primary_dataset_id, analysis.instrument_code, scale
                )
            except Exception as e:
                # Se houver erro na distribuição, apenas ignorar
                results["score_distribution_error"] = str(e)

        # Criar registro da análise no banco de dados
        stat_repo = StatisticalRepository()
        db_analysis = stat_repo.create(db, analysis, current_user.id, results)

        return db_analysis

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular estatísticas descritivas: {str(e)}"
        )


# ---------- Rotas para análise de confiabilidade ----------

@router.post("/reliability", response_model=StatisticalAnalysisResponse)
async def create_reliability_analysis(
        analysis: StatisticalAnalysisCreate,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Cria uma análise de confiabilidade para um instrumento
    """
    # Verificar se o tipo de análise está correto
    if analysis.analysis_type != AnalysisType.RELIABILITY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de análise incorreto. Deve ser 'reliability'."
        )

    # Verificar se o dataset existe e pertence ao usuário
    dataset_repo = DatasetRepository()
    dataset = dataset_repo.get_by_id(db, analysis.primary_dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset não encontrado."
        )

    if dataset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este dataset."
        )

    try:
        # Calcular estatísticas de confiabilidade
        results = statistical_service.reliability_analysis(
            db, analysis.primary_dataset_id, analysis.instrument_code
        )

        # Criar registro da análise no banco de dados
        stat_repo = StatisticalRepository()
        db_analysis = stat_repo.create(db, analysis, current_user.id, results)

        return db_analysis

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular análise de confiabilidade: {str(e)}"
        )


# ---------- Rotas para análise comparativa ----------

@router.post("/comparative", response_model=StatisticalAnalysisResponse)
async def create_comparative_analysis(
        analysis: StatisticalAnalysisCreate,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Cria uma análise comparativa entre grupos
    """
    # Verificar se o tipo de análise está correto
    if analysis.analysis_type != AnalysisType.COMPARATIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de análise incorreto. Deve ser 'comparative'."
        )

    # Validar parâmetros
    required_params = ["scale", "group_field", "group_values"]
    for param in required_params:
        if param not in analysis.parameters:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O parâmetro '{param}' é obrigatório para análise comparativa."
            )

    # Verificar se o dataset existe e pertence ao usuário
    dataset_repo = DatasetRepository()
    dataset = dataset_repo.get_by_id(db, analysis.primary_dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset não encontrado."
        )

    if dataset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este dataset."
        )

    try:
        # Extrair parâmetros
        scale = analysis.parameters["scale"]
        group_field = analysis.parameters["group_field"]
        group_values = analysis.parameters["group_values"]

        # Realizar análise comparativa
        results = statistical_service.compare_groups(
            db, analysis.primary_dataset_id, analysis.instrument_code,
            scale, group_field, group_values
        )

        # Criar registro da análise no banco de dados
        stat_repo = StatisticalRepository()
        db_analysis = stat_repo.create(db, analysis, current_user.id, results)

        return db_analysis

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular análise comparativa: {str(e)}"
        )


# ---------- Rotas para análise MANOVA ----------

@router.post("/manova", response_model=StatisticalAnalysisResponse)
async def create_manova_analysis(
        analysis: StatisticalAnalysisCreate,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Cria uma análise MANOVA para múltiplas escalas
    """
    # Verificar se o tipo de análise está correto
    if analysis.analysis_type != AnalysisType.MANOVA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de análise incorreto. Deve ser 'manova'."
        )

    # Validar parâmetros (scales deve estar presente)
    if "scales" not in analysis.parameters or not analysis.parameters["scales"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O parâmetro 'scales' é obrigatório para análise MANOVA."
        )

    # Verificar se o dataset existe e pertence ao usuário
    dataset_repo = DatasetRepository()
    dataset = dataset_repo.get_by_id(db, analysis.primary_dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset não encontrado."
        )

    if dataset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este dataset."
        )

    try:
        # Extrair escalas dos parâmetros
        scales = analysis.parameters["scales"]

        # Realizar análise MANOVA
        results = statistical_service.compare_scales(
            db, analysis.primary_dataset_id, analysis.instrument_code, scales
        )

        # Criar registro da análise no banco de dados
        stat_repo = StatisticalRepository()
        db_analysis = stat_repo.create(db, analysis, current_user.id, results)

        return db_analysis

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular análise MANOVA: {str(e)}"
        )


# ---------- Rotas para análise correlacional ----------

@router.post("/correlation", response_model=StatisticalAnalysisResponse)
async def create_correlation_analysis(
        analysis: StatisticalAnalysisCreate,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Cria uma análise correlacional entre escalas ou instrumentos
    """
    # Verificar se o tipo de análise está correto
    if analysis.analysis_type != AnalysisType.CORRELATION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de análise incorreto. Deve ser 'correlation'."
        )

    # Verificar se o dataset existe e pertence ao usuário
    dataset_repo = DatasetRepository()
    dataset = dataset_repo.get_by_id(db, analysis.primary_dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset não encontrado."
        )

    if dataset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este dataset."
        )

    try:
        results = {}

        # Determinar se é correlação entre escalas ou entre instrumentos
        if "scales" in analysis.parameters and len(analysis.parameters["scales"]) > 1:
            # Correlação entre múltiplas escalas do mesmo instrumento
            scales = analysis.parameters["scales"]
            results = statistical_service.correlate_scales(
                db, analysis.primary_dataset_id, analysis.instrument_code, scales
            )
        elif all(key in analysis.parameters for key in ["secondary_instrument_code", "secondary_scale"]):
            # Correlação entre dois instrumentos diferentes
            scale1 = analysis.parameters.get("scale", analysis.scales[0])
            instrument2 = analysis.parameters["secondary_instrument_code"]
            scale2 = analysis.parameters["secondary_scale"]

            results = statistical_service.correlate_instruments(
                db, analysis.primary_dataset_id,
                analysis.instrument_code, scale1,
                instrument2, scale2
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parâmetros inválidos para análise correlacional."
            )

        # Criar registro da análise no banco de dados
        stat_repo = StatisticalRepository()
        db_analysis = stat_repo.create(db, analysis, current_user.id, results)

        return db_analysis

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular análise correlacional: {str(e)}"
        )


# ---------- Rotas para análise longitudinal ----------

@router.post("/longitudinal", response_model=StatisticalAnalysisResponse)
async def create_longitudinal_analysis(
        analysis: StatisticalAnalysisCreate,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Cria uma análise longitudinal entre dois pontos de tempo
    """
    # Verificar se o tipo de análise está correto
    if analysis.analysis_type != AnalysisType.LONGITUDINAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de análise incorreto. Deve ser 'longitudinal'."
        )

    # Validar parâmetros
    if "scale" not in analysis.parameters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O parâmetro 'scale' é obrigatório para análise longitudinal."
        )

    # Verificar se é necessário um segundo dataset
    if analysis.secondary_dataset_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Um segundo dataset (secondary_dataset_id) é necessário para análise longitudinal."
        )

    # Verificar se os datasets existem e pertencem ao usuário
    dataset_repo = DatasetRepository()
    dataset1 = dataset_repo.get_by_id(db, analysis.primary_dataset_id)
    dataset2 = dataset_repo.get_by_id(db, analysis.secondary_dataset_id)

    if not dataset1 or not dataset2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Um ou mais datasets não foram encontrados."
        )

    if dataset1.owner_id != current_user.id or dataset2.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar um ou mais datasets."
        )

    try:
        # Extrair parâmetros
        scale = analysis.parameters["scale"]

        # Realizar análise longitudinal
        results = statistical_service.longitudinal_analysis(
            db, analysis.primary_dataset_id, analysis.secondary_dataset_id,
            analysis.instrument_code, scale
        )

        # Criar registro da análise no banco de dados
        stat_repo = StatisticalRepository()
        db_analysis = stat_repo.create(db, analysis, current_user.id, results)

        return db_analysis

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular análise longitudinal: {str(e)}"
        )


# ---------- Rotas para gerenciamento de análises ----------

@router.get("/", response_model=List[StatisticalAnalysisResponse])
async def list_analyses(
        skip: int = 0,
        limit: int = 100,
        analysis_type: Optional[str] = None,
        dataset_id: Optional[int] = None,
        include_archived: bool = False,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Lista todas as análises estatísticas do usuário atual
    """
    stat_repo = StatisticalRepository()

    # Filtrar por tipo de análise, se fornecido
    if analysis_type is not None:
        analyses = stat_repo.get_by_type(db, current_user.id, analysis_type, skip, limit, include_archived)
    # Filtrar por dataset, se fornecido
    elif dataset_id is not None:
        analyses = stat_repo.get_by_dataset(db, dataset_id, skip, limit, include_archived)
    # Caso contrário, listar todas as análises do usuário
    else:
        analyses = stat_repo.get_all_by_owner(db, current_user.id, skip, limit, include_archived)

    return analyses


@router.get("/{analysis_id}", response_model=StatisticalAnalysisDetail)
async def get_analysis(
        analysis_id: int,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtém detalhes de uma análise estatística específica
    """
    stat_repo = StatisticalRepository()
    analysis = stat_repo.get_by_id(db, analysis_id)

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise estatística não encontrada."
        )

    if analysis.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar esta análise."
        )

    return analysis


@router.put("/{analysis_id}", response_model=StatisticalAnalysisResponse)
async def update_analysis(
        analysis_id: int,
        update_data: StatisticalAnalysisUpdate,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Atualiza metadados de uma análise estatística
    """
    stat_repo = StatisticalRepository()
    analysis = stat_repo.get_by_id(db, analysis_id)

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise estatística não encontrada."
        )

    if analysis.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para modificar esta análise."
        )

    updated_analysis = stat_repo.update(db, analysis_id, update_data)

    if not updated_analysis:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar análise estatística."
        )

    return updated_analysis


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
        analysis_id: int,
        permanent: bool = False,
        db: Session = Depends(db_connection.get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Remove uma análise estatística (arquivo lógico por padrão, exclusão permanente se permanent=True)
    """
    stat_repo = StatisticalRepository()
    analysis = stat_repo.get_by_id(db, analysis_id)

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise estatística não encontrada."
        )

    if analysis.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para excluir esta análise."
        )

    # Exclusão permanente ou arquivamento
    if permanent:
        success = stat_repo.delete(db, analysis_id)
    else:
        success = stat_repo.archive(db, analysis_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir análise estatística."
        )

    return None