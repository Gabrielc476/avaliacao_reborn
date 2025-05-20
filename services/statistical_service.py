# services/statistical_service.py
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from utils.statistical_tests import (
    calculate_descriptive_stats, frequency_distribution, category_distribution,
    cronbach_alpha, item_total_correlations,
    independent_t_test, one_way_anova, manova,
    pearson_correlation, correlation_matrix,
    paired_t_test, repeated_measures_anova
)
from database.models.dataset import Dataset, InstrumentDataset
from database.models.instrument import Instrument
from repositories.dataset_repository import DatasetRepository


class StatisticalService:
    """
    Serviço para realização de análises estatísticas em dados de instrumentos psicológicos.
    """

    def __init__(self, dataset_repository: DatasetRepository):
        """
        Inicializa o serviço com suas dependências.

        Args:
            dataset_repository: Repositório de datasets
        """
        self.dataset_repository = dataset_repository

    def _extract_scale_data(self, dataset_id: int, instrument_code: str,
                            scale: str, db: Session) -> Tuple[np.ndarray, List[str]]:
        """
        Extrai dados de uma escala específica de um instrumento.

        Args:
            dataset_id: ID do dataset
            instrument_code: Código do instrumento (ex: "DASS21")
            scale: Nome da escala (ex: "depression", "anxiety", "stress")
            db: Sessão do banco de dados

        Returns:
            Tuple contendo array de pontuações e lista de IDs de participantes
        """
        # Obter resultados do instrumento
        results_data = self.dataset_repository.get_instrument_results(db, dataset_id, instrument_code)

        if not results_data or 'results' not in results_data:
            raise ValueError(f"Não foram encontrados resultados para o instrumento {instrument_code}")

        # Extrair pontuações da escala específica
        scores = []
        participant_ids = []

        for result in results_data['results']:
            if not result.get('complete', False):
                continue

            if 'scores' in result and scale in result['scores']:
                scores.append(result['scores'][scale])
                participant_ids.append(result.get('participant_id', ''))

        return np.array(scores), participant_ids

    def _extract_total_scores(self, dataset_id: int, instrument_code: str,
                              db: Session) -> Tuple[np.ndarray, List[str]]:
        """
        Extrai pontuações totais de um instrumento.

        Args:
            dataset_id: ID do dataset
            instrument_code: Código do instrumento
            db: Sessão do banco de dados

        Returns:
            Tuple contendo array de pontuações totais e lista de IDs de participantes
        """
        # Obter resultados do instrumento
        results_data = self.dataset_repository.get_instrument_results(db, dataset_id, instrument_code)

        if not results_data or 'results' not in results_data:
            raise ValueError(f"Não foram encontrados resultados para o instrumento {instrument_code}")

        # Extrair pontuações totais
        total_scores = []
        participant_ids = []

        for result in results_data['results']:
            if not result.get('complete', False):
                continue

            if 'scores' in result and 'total' in result['scores']:
                total_scores.append(result['scores']['total'])
                participant_ids.append(result.get('participant_id', ''))

        return np.array(total_scores), participant_ids

    def _extract_categories(self, dataset_id: int, instrument_code: str,
                            scale: str, db: Session) -> Tuple[List[str], List[str]]:
        """
        Extrai categorias de uma escala específica.

        Args:
            dataset_id: ID do dataset
            instrument_code: Código do instrumento
            scale: Nome da escala
            db: Sessão do banco de dados

        Returns:
            Tuple contendo lista de categorias e lista de IDs de participantes
        """
        # Obter resultados do instrumento
        results_data = self.dataset_repository.get_instrument_results(db, dataset_id, instrument_code)

        if not results_data or 'results' not in results_data:
            raise ValueError(f"Não foram encontrados resultados para o instrumento {instrument_code}")

        # Extrair categorias
        categories = []
        participant_ids = []

        for result in results_data['results']:
            if not result.get('complete', False):
                continue

            if 'categories' in result and scale in result['categories']:
                categories.append(result['categories'][scale])
                participant_ids.append(result.get('participant_id', ''))

        return categories, participant_ids

    def _extract_item_responses(self, dataset_id: int, instrument_code: str,
                                db: Session) -> Tuple[np.ndarray, List[str]]:
        """
        Extrai respostas por item para análise de confiabilidade.

        Args:
            dataset_id: ID do dataset
            instrument_code: Código do instrumento
            db: Sessão do banco de dados

        Returns:
            Tuple contendo matriz de respostas e lista de IDs de participantes
        """
        # Obter o dataset completo
        dataset = self.dataset_repository.get_by_id(db, dataset_id)

        if not dataset:
            raise ValueError(f"Dataset com ID {dataset_id} não encontrado")

        # Obter o instrumento
        instrument_query = db.query(Instrument).filter(Instrument.code == instrument_code).first()

        if not instrument_query:
            raise ValueError(f"Instrumento {instrument_code} não encontrado")

        # Obter a estrutura do instrumento
        structure = instrument_query.structure

        # Prefixo para questões do instrumento
        prefix = f"{instrument_code.lower()}_q"

        responses = []
        participant_ids = []

        # Extrair respostas item por item para cada participante
        for participant_data in dataset.data:
            # Verificar se contém respostas para este instrumento
            item_responses = []
            has_responses = False

            for i in range(1, 22):  # Para DASS21, assumindo 21 itens
                key = f"{prefix}{i}"
                if key in participant_data:
                    item_responses.append(participant_data[key])
                    has_responses = True
                else:
                    # Se algum item estiver faltando, pular este participante
                    has_responses = False
                    break

            if has_responses:
                responses.append(item_responses)
                participant_ids.append(participant_data.get('id', ''))

        return np.array(responses), participant_ids

    # ---------------------- MÉTODOS DE SERVIÇO PARA ANÁLISES DESCRITIVAS ----------------------

    def descriptive_statistics(self, db: Session, dataset_id: int,
                               instrument_code: str, scale: str) -> Dict[str, float]:
        """
        Calcula estatísticas descritivas para uma escala específica.

        Args:
            db: Sessão do banco de dados
            dataset_id: ID do dataset
            instrument_code: Código do instrumento (ex: "DASS21")
            scale: Nome da escala (ex: "depression", "anxiety", "stress")

        Returns:
            Dicionário com estatísticas descritivas
        """
        scores, _ = self._extract_scale_data(dataset_id, instrument_code, scale, db)
        return calculate_descriptive_stats(scores)

    def category_analysis(self, db: Session, dataset_id: int,
                          instrument_code: str, scale: str) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Analisa a distribuição de categorias de severidade.

        Args:
            db: Sessão do banco de dados
            dataset_id: ID do dataset
            instrument_code: Código do instrumento
            scale: Nome da escala

        Returns:
            Dicionário com distribuição de categorias
        """
        categories, _ = self._extract_categories(dataset_id, instrument_code, scale, db)
        return category_distribution(categories)

    def score_distribution(self, db: Session, dataset_id: int,
                           instrument_code: str, scale: str) -> Dict[str, List]:
        """
        Analisa a distribuição de pontuações.

        Args:
            db: Sessão do banco de dados
            dataset_id: ID do dataset
            instrument_code: Código do instrumento
            scale: Nome da escala

        Returns:
            Dicionário com distribuição de pontuações
        """
        scores, _ = self._extract_scale_data(dataset_id, instrument_code, scale, db)
        return frequency_distribution(scores)

    # ---------------------- MÉTODOS DE SERVIÇO PARA ANÁLISES DE CONFIABILIDADE ----------------------

    def reliability_analysis(self, db: Session, dataset_id: int,
                             instrument_code: str) -> Dict[str, Any]:
        """
        Realiza análise de confiabilidade para um instrumento.

        Args:
            db: Sessão do banco de dados
            dataset_id: ID do dataset
            instrument_code: Código do instrumento

        Returns:
            Dicionário com alfa de Cronbach e correlações item-total
        """
        responses, _ = self._extract_item_responses(dataset_id, instrument_code, db)

        alpha = cronbach_alpha(responses)
        item_correlations = item_total_correlations(responses)

        return {
            'cronbach_alpha': alpha,
            'item_total_correlations': item_correlations,
            'n_items': responses.shape[1],
            'n_participants': responses.shape[0]
        }

    # ---------------------- MÉTODOS DE SERVIÇO PARA ANÁLISES COMPARATIVAS ----------------------

    def compare_groups(self, db: Session, dataset_id: int, instrument_code: str,
                       scale: str, group_field: str, group_values: List[Any]) -> Dict[str, Any]:
        """
        Compara pontuações entre grupos.

        Args:
            db: Sessão do banco de dados
            dataset_id: ID do dataset
            instrument_code: Código do instrumento
            scale: Nome da escala
            group_field: Campo usado para definir grupos (ex: "gender")
            group_values: Lista de valores para selecionar grupos (ex: ["male", "female"])

        Returns:
            Dicionário com resultados da comparação
        """
        dataset = self.dataset_repository.get_by_id(db, dataset_id)

        if not dataset:
            raise ValueError(f"Dataset com ID {dataset_id} não encontrado")

        # Obter resultados do instrumento
        results_data = self.dataset_repository.get_instrument_results(db, dataset_id, instrument_code)

        if not results_data or 'results' not in results_data:
            raise ValueError(f"Não foram encontrados resultados para o instrumento {instrument_code}")

        # Mapear resultados por participant_id
        results_by_id = {r.get('participant_id', ''): r for r in results_data['results']}

        # Organizar dados em grupos
        groups = [[] for _ in range(len(group_values))]

        for participant_data in dataset.data:
            # Verificar se o participante tem o campo grupo
            if group_field in participant_data:
                group_value = participant_data[group_field]
                participant_id = participant_data.get('id', '')

                # Verificar se o valor do grupo está na lista de valores
                if group_value in group_values:
                    group_index = group_values.index(group_value)

                    # Verificar se temos resultados para este participante
                    if participant_id in results_by_id:
                        result = results_by_id[participant_id]

                        if result.get('complete', False) and 'scores' in result and scale in result['scores']:
                            groups[group_index].append(result['scores'][scale])

        # Converter para numpy arrays
        groups = [np.array(group) for group in groups]

        # Realizar a análise estatística adequada
        if len(group_values) == 2:
            # Teste t para dois grupos
            return independent_t_test(groups[0], groups[1])
        else:
            # ANOVA para mais de dois grupos
            return one_way_anova(groups)

    def compare_scales(self, db: Session, dataset_id: int,
                       instrument_code: str, scales: List[str]) -> Dict[str, Any]:
        """
        Compara diferentes escalas do mesmo instrumento usando MANOVA.

        Args:
            db: Sessão do banco de dados
            dataset_id: ID do dataset
            instrument_code: Código do instrumento
            scales: Lista de escalas a comparar

        Returns:
            Dicionário com resultados da MANOVA
        """
        # Obter pontuações para cada escala
        scale_data = []
        all_participant_ids = []

        for scale in scales:
            scores, ids = self._extract_scale_data(dataset_id, instrument_code, scale, db)
            scale_data.append((scores, ids))
            all_participant_ids.append(ids)

        # Identificar participantes comuns em todas as escalas
        common_participants = set(all_participant_ids[0])
        for ids in all_participant_ids[1:]:
            common_participants.intersection_update(ids)

        # Verificar se há participantes suficientes
        if len(common_participants) < len(scales) + 2:
            raise ValueError(
                f"Número insuficiente de participantes ({len(common_participants)}) para MANOVA com {len(scales)} variáveis")

        # Criar matriz de dados para cada participante
        participant_data = {}

        for pid in common_participants:
            participant_data[pid] = []

        # Preencher dados de cada escala para cada participante
        for scale_idx, (scores, ids) in enumerate(scale_data):
            scores_dict = {pid: score for score, pid in zip(scores, ids)}

            for pid in common_participants:
                if pid in scores_dict:
                    participant_data[pid].append(scores_dict[pid])
                else:
                    # Remover participante se faltarem dados
                    participant_data.pop(pid, None)

        # Organizar participantes em grupos baseados em alguma variável
        # Para MANOVA precisamos definir grupos
        # Vamos buscar os dados originais para definir os grupos
        dataset = self.dataset_repository.get_by_id(db, dataset_id)

        if not dataset:
            raise ValueError(f"Dataset com ID {dataset_id} não encontrado")

        # Buscar uma variável categórica para agrupar
        # Por exemplo, vamos buscar por gênero, grupo etário, ou qualquer campo categórico
        group_variables = ["gender", "age_group", "group", "condition", "treatment"]

        # Procurar a primeira variável categórica disponível
        group_field = None
        group_values = set()
        data_by_group = {}

        for field in group_variables:
            # Verificar se o campo existe nos dados
            field_exists = False

            for participant_data_row in dataset.data:
                if field in participant_data_row:
                    field_exists = True
                    pid = participant_data_row.get('id', '')

                    if pid in participant_data and pid in common_participants:
                        group_val = participant_data_row[field]
                        group_values.add(group_val)

                        if group_val not in data_by_group:
                            data_by_group[group_val] = []

                        data_by_group[group_val].append(participant_data[pid])

            if field_exists and len(group_values) >= 2:
                group_field = field
                break

        # Verificar se encontramos um campo de agrupamento válido
        if not group_field or len(group_values) < 2:
            # Se não encontramos, podemos criar grupos artificiais
            # por exemplo, dividindo em dois grupos por mediana

            # Calcular mediana da primeira escala
            median_scale1 = np.median([data[0] for data in participant_data.values()])

            # Dividir em dois grupos: acima e abaixo da mediana
            data_by_group = {
                'below_median': [],
                'above_median': []
            }

            for pid, data in participant_data.items():
                if data[0] < median_scale1:
                    data_by_group['below_median'].append(data)
                else:
                    data_by_group['above_median'].append(data)

            group_field = "median_split"
            group_values = {'below_median', 'above_median'}

        # Converter para arrays numpy
        groups_data = []
        for group_val in group_values:
            if group_val in data_by_group and len(data_by_group[group_val]) > 0:
                group_array = np.array(data_by_group[group_val])
                if len(group_array) > len(scales):  # Verificar se há dados suficientes
                    groups_data.append(group_array)

        # Realizar MANOVA
        if len(groups_data) >= 2:
            manova_result = manova(groups_data, len(scales))

            # Adicionar metadados
            manova_result['group_field'] = group_field
            manova_result['group_values'] = list(group_values)
            manova_result['scale_names'] = scales

            return manova_result
        else:
            raise ValueError(
                "Dados insuficientes para MANOVA. É necessário ter pelo menos dois grupos com dados completos.")

    # ---------------------- MÉTODOS DE SERVIÇO PARA ANÁLISES CORRELACIONAIS ----------------------

    def correlate_scales(self, db: Session, dataset_id: int,
                         instrument_code: str, scales: List[str]) -> Dict[str, Any]:
        """
        Calcula correlações entre diferentes escalas do mesmo instrumento.

        Args:
            db: Sessão do banco de dados
            dataset_id: ID do dataset
            instrument_code: Código do instrumento
            scales: Lista de escalas para correlacionar

        Returns:
            Dicionário com matriz de correlação
        """
        # Obter pontuações para cada escala
        scale_scores = []
        all_participant_ids = []

        for scale in scales:
            scores, ids = self._extract_scale_data(dataset_id, instrument_code, scale, db)
            scale_scores.append(scores)
            all_participant_ids.append(ids)

        # Identificar participantes comuns em todas as escalas
        common_participants = set(all_participant_ids[0])
        for ids in all_participant_ids[1:]:
            common_participants.intersection_update(ids)

        # Filtrar scores para apenas participantes comuns
        filtered_scores = []
        for i, (scores, ids) in enumerate(zip(scale_scores, all_participant_ids)):
            # Criar dict de scores por participant_id
            scores_dict = {pid: score for score, pid in zip(scores, ids)}

            # Obter scores na mesma ordem para cada escala
            scale_filtered = [scores_dict[pid] for pid in common_participants if pid in scores_dict]
            filtered_scores.append(np.array(scale_filtered))

        # Organizar matriz para correlação
        data_matrix = np.column_stack(filtered_scores)

        return {
            'correlation_results': correlation_matrix(data_matrix),
            'scale_names': scales,
            'n_participants': len(common_participants)
        }

    def correlate_instruments(self, db: Session, dataset_id: int,
                              instrument1_code: str, scale1: str,
                              instrument2_code: str, scale2: str) -> Dict[str, float]:
        """
        Calcula correlação entre escalas de diferentes instrumentos.

        Args:
            db: Sessão do banco de dados
            dataset_id: ID do dataset
            instrument1_code: Código do primeiro instrumento
            scale1: Escala do primeiro instrumento
            instrument2_code: Código do segundo instrumento
            scale2: Escala do segundo instrumento

        Returns:
            Dicionário com coeficiente de correlação e valor p
        """
        # Obter pontuações de cada instrumento
        scores1, ids1 = self._extract_scale_data(dataset_id, instrument1_code, scale1, db)
        scores2, ids2 = self._extract_scale_data(dataset_id, instrument2_code, scale2, db)

        # Criar dicionários de scores por ID
        scores1_dict = {pid: score for score, pid in zip(scores1, ids1)}
        scores2_dict = {pid: score for score, pid in zip(scores2, ids2)}

        # Identificar participantes comuns
        common_ids = set(ids1).intersection(set(ids2))

        # Filtrar para apenas participantes com dados em ambos os instrumentos
        filtered_scores1 = []
        filtered_scores2 = []

        for pid in common_ids:
            if pid in scores1_dict and pid in scores2_dict:
                filtered_scores1.append(scores1_dict[pid])
                filtered_scores2.append(scores2_dict[pid])

        # Calcular correlação
        if len(filtered_scores1) > 1:
            correlation_result = pearson_correlation(
                np.array(filtered_scores1),
                np.array(filtered_scores2)
            )

            correlation_result['instrument1'] = instrument1_code
            correlation_result['scale1'] = scale1
            correlation_result['instrument2'] = instrument2_code
            correlation_result['scale2'] = scale2

            return correlation_result
        else:
            raise ValueError("Dados insuficientes para calcular correlação")

    # ---------------------- MÉTODOS DE SERVIÇO PARA ANÁLISES LONGITUDINAIS ----------------------

    def longitudinal_analysis(self, db: Session, pre_dataset_id: int, post_dataset_id: int,
                              instrument_code: str, scale: str) -> Dict[str, float]:
        """
        Compara medidas pré e pós intervenção (longitudinal).

        Args:
            db: Sessão do banco de dados
            pre_dataset_id: ID do dataset pré-intervenção
            post_dataset_id: ID do dataset pós-intervenção
            instrument_code: Código do instrumento
            scale: Nome da escala

        Returns:
            Dicionário com resultados do teste t pareado
        """
        # Obter pontuações pré e pós intervenção
        pre_scores, pre_ids = self._extract_scale_data(pre_dataset_id, instrument_code, scale, db)
        post_scores, post_ids = self._extract_scale_data(post_dataset_id, instrument_code, scale, db)

        # Criar dicionários de scores por ID
        pre_dict = {pid: score for score, pid in zip(pre_scores, pre_ids)}
        post_dict = {pid: score for score, pid in zip(post_scores, post_ids)}

        # Identificar participantes comuns
        common_ids = set(pre_ids).intersection(set(post_ids))

        # Filtrar para apenas participantes com dados em ambos os momentos
        paired_pre = []
        paired_post = []

        for pid in common_ids:
            if pid in pre_dict and pid in post_dict:
                paired_pre.append(pre_dict[pid])
                paired_post.append(post_dict[pid])

        # Calcular teste t pareado
        if len(paired_pre) > 1:
            return paired_t_test(
                np.array(paired_pre),
                np.array(paired_post)
            )
        else:
            raise ValueError("Dados insuficientes para análise longitudinal")

    def multiple_timepoints_analysis(self, db: Session, dataset_ids: List[int],
                                     instrument_code: str, scale: str) -> Dict[str, Any]:
        """
        Analisa dados de múltiplos pontos temporais.

        Args:
            db: Sessão do banco de dados
            dataset_ids: Lista de IDs de datasets em ordem cronológica
            instrument_code: Código do instrumento
            scale: Nome da escala

        Returns:
            Dicionário com resultados da ANOVA de medidas repetidas
        """
        # Obter pontuações para cada timepoint
        all_scores = []
        all_ids = []

        for dataset_id in dataset_ids:
            scores, ids = self._extract_scale_data(dataset_id, instrument_code, scale, db)
            all_scores.append(scores)
            all_ids.append(ids)

        # Identificar participantes comuns em todos os timepoints
        common_participants = set(all_ids[0])
        for ids in all_ids[1:]:
            common_participants.intersection_update(ids)

        # Filtrar scores para apenas participantes comuns em todos os timepoints
        measurements = []
        for i, (scores, ids) in enumerate(zip(all_scores, all_ids)):
            # Criar dict de scores por participant_id
            scores_dict = {pid: score for score, pid in zip(scores, ids)}

            # Obter scores na mesma ordem para cada timepoint
            timepoint_data = [scores_dict[pid] for pid in common_participants if pid in scores_dict]

            if len(timepoint_data) == len(common_participants):
                measurements.append(np.array(timepoint_data))
            else:
                raise ValueError(f"Dados incompletos para o timepoint {i}")

        # Calcular ANOVA de medidas repetidas
        if len(measurements) > 1 and len(common_participants) > 1:
            result = repeated_measures_anova(measurements)
            result['n_participants'] = len(common_participants)
            result['n_timepoints'] = len(measurements)
            return result
        else:
            raise ValueError("Dados insuficientes para análise de múltiplos timepoints")


# Instância compartilhada do serviço
statistical_service = StatisticalService(DatasetRepository())