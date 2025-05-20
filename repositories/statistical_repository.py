# repositories/statistical_repository.py
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database.models.statistical_analysis import StatisticalAnalysis
from database.schemas.statistical_analysis import StatisticalAnalysisCreate, StatisticalAnalysisUpdate


class StatisticalRepository:
    """
    Repositório para operações relacionadas a análises estatísticas
    """

    @staticmethod
    def create(db: Session, analysis_data: StatisticalAnalysisCreate, owner_id: int,
               results: Dict[str, Any]) -> StatisticalAnalysis:
        """
        Cria uma nova análise estatística

        Args:
            db: Sessão do banco de dados
            analysis_data: Dados da análise
            owner_id: ID do usuário proprietário
            results: Resultados da análise estatística

        Returns:
            Análise estatística criada
        """
        # Converter Pydantic model para dict
        analysis_dict = analysis_data.dict()

        # Criar objeto de análise estatística
        db_analysis = StatisticalAnalysis(
            name=analysis_dict["name"],
            description=analysis_dict["description"],
            analysis_type=analysis_dict["analysis_type"],
            instrument_code=analysis_dict["instrument_code"],
            scales=analysis_dict["scales"],
            primary_dataset_id=analysis_dict["primary_dataset_id"],
            secondary_dataset_id=analysis_dict.get("secondary_dataset_id"),
            parameters=analysis_dict["parameters"],
            results=results,
            owner_id=owner_id,
            is_archived=False
        )

        # Adicionar ao banco de dados
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)

        return db_analysis

    @staticmethod
    def get_by_id(db: Session, analysis_id: int) -> Optional[StatisticalAnalysis]:
        """
        Busca uma análise estatística pelo ID

        Args:
            db: Sessão do banco de dados
            analysis_id: ID da análise

        Returns:
            Análise estatística encontrada ou None
        """
        return db.query(StatisticalAnalysis).filter(StatisticalAnalysis.id == analysis_id).first()

    @staticmethod
    def get_all_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100,
                         include_archived: bool = False) -> List[StatisticalAnalysis]:
        """
        Busca todas as análises estatísticas de um usuário

        Args:
            db: Sessão do banco de dados
            owner_id: ID do usuário proprietário
            skip: Número de registros a pular (para paginação)
            limit: Número máximo de registros a retornar
            include_archived: Se True, inclui análises arquivadas

        Returns:
            Lista de análises estatísticas
        """
        query = db.query(StatisticalAnalysis).filter(StatisticalAnalysis.owner_id == owner_id)

        if not include_archived:
            query = query.filter(StatisticalAnalysis.is_archived == False)

        return query.order_by(StatisticalAnalysis.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_dataset(db: Session, dataset_id: int, skip: int = 0, limit: int = 100,
                       include_archived: bool = False) -> List[StatisticalAnalysis]:
        """
        Busca todas as análises estatísticas associadas a um dataset

        Args:
            db: Sessão do banco de dados
            dataset_id: ID do dataset
            skip: Número de registros a pular (para paginação)
            limit: Número máximo de registros a retornar
            include_archived: Se True, inclui análises arquivadas

        Returns:
            Lista de análises estatísticas
        """
        query = db.query(StatisticalAnalysis).filter(
            or_(
                StatisticalAnalysis.primary_dataset_id == dataset_id,
                StatisticalAnalysis.secondary_dataset_id == dataset_id
            )
        )

        if not include_archived:
            query = query.filter(StatisticalAnalysis.is_archived == False)

        return query.order_by(StatisticalAnalysis.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_type(db: Session, owner_id: int, analysis_type: str, skip: int = 0, limit: int = 100,
                    include_archived: bool = False) -> List[StatisticalAnalysis]:
        """
        Busca análises estatísticas por tipo

        Args:
            db: Sessão do banco de dados
            owner_id: ID do usuário proprietário
            analysis_type: Tipo de análise
            skip: Número de registros a pular (para paginação)
            limit: Número máximo de registros a retornar
            include_archived: Se True, inclui análises arquivadas

        Returns:
            Lista de análises estatísticas
        """
        query = db.query(StatisticalAnalysis).filter(
            StatisticalAnalysis.owner_id == owner_id,
            StatisticalAnalysis.analysis_type == analysis_type
        )

        if not include_archived:
            query = query.filter(StatisticalAnalysis.is_archived == False)

        return query.order_by(StatisticalAnalysis.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_instrument_code(db: Session, owner_id: int, instrument_code: str, skip: int = 0, limit: int = 100,
                               include_archived: bool = False) -> List[StatisticalAnalysis]:
        """
        Busca análises estatísticas por código de instrumento

        Args:
            db: Sessão do banco de dados
            owner_id: ID do usuário proprietário
            instrument_code: Código do instrumento (ex: "DASS21")
            skip: Número de registros a pular (para paginação)
            limit: Número máximo de registros a retornar
            include_archived: Se True, inclui análises arquivadas

        Returns:
            Lista de análises estatísticas
        """
        query = db.query(StatisticalAnalysis).filter(
            StatisticalAnalysis.owner_id == owner_id,
            StatisticalAnalysis.instrument_code == instrument_code
        )

        if not include_archived:
            query = query.filter(StatisticalAnalysis.is_archived == False)

        return query.order_by(StatisticalAnalysis.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, analysis_id: int, update_data: StatisticalAnalysisUpdate) -> Optional[StatisticalAnalysis]:
        """
        Atualiza uma análise estatística

        Args:
            db: Sessão do banco de dados
            analysis_id: ID da análise
            update_data: Dados a serem atualizados

        Returns:
            Análise estatística atualizada ou None
        """
        db_analysis = StatisticalRepository.get_by_id(db, analysis_id)

        if db_analysis:
            # Atualizar apenas campos não nulos do objeto de atualização
            update_dict = update_data.dict(exclude_unset=True)

            for key, value in update_dict.items():
                setattr(db_analysis, key, value)

            db.commit()
            db.refresh(db_analysis)

        return db_analysis

    @staticmethod
    def archive(db: Session, analysis_id: int) -> bool:
        """
        Arquiva uma análise estatística (exclusão lógica)

        Args:
            db: Sessão do banco de dados
            analysis_id: ID da análise

        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        db_analysis = StatisticalRepository.get_by_id(db, analysis_id)

        if db_analysis:
            db_analysis.is_archived = True
            db.commit()
            return True

        return False

    @staticmethod
    def delete(db: Session, analysis_id: int) -> bool:
        """
        Remove permanentemente uma análise estatística

        Args:
            db: Sessão do banco de dados
            analysis_id: ID da análise

        Returns:
            True se a operação foi bem-sucedida, False caso contrário
        """
        db_analysis = StatisticalRepository.get_by_id(db, analysis_id)

        if db_analysis:
            db.delete(db_analysis)
            db.commit()
            return True

        return False