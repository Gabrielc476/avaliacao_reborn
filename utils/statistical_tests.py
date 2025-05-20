# utils/statistical_tests.py
"""
Utilidades para cálculos estatísticos relacionados aos instrumentos psicológicos.
Implementa diversos testes e métricas estatísticas para análise de dados.
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Union, Optional, Any


# ---------------------- ANÁLISES DESCRITIVAS ----------------------

def calculate_descriptive_stats(data: np.ndarray) -> Dict[str, float]:
    """
    Calcula estatísticas descritivas básicas para um conjunto de dados.

    Args:
        data: Array de dados para análise

    Returns:
        Dicionário com estatísticas descritivas
    """
    return {
        'mean': float(np.mean(data)),
        'median': float(np.median(data)),
        'std_dev': float(np.std(data, ddof=1)),
        'min': float(np.min(data)),
        'max': float(np.max(data)),
        'q1': float(np.percentile(data, 25)),
        'q3': float(np.percentile(data, 75)),
        'n': len(data)
    }


def frequency_distribution(data: np.ndarray, bins: Optional[List] = None) -> Dict[str, List]:
    """
    Calcula a distribuição de frequência para um conjunto de dados.

    Args:
        data: Array de dados para análise
        bins: Lista opcional definindo os limites dos bins. Se None, bins serão calculados automaticamente.

    Returns:
        Dicionário com bins e contagens
    """
    if bins is None:
        # Determinar bins automaticamente
        counts, bin_edges = np.histogram(data, bins='auto')
    else:
        counts, bin_edges = np.histogram(data, bins=bins)

    return {
        'bin_edges': bin_edges.tolist(),
        'counts': counts.tolist(),
        'relative_freq': (counts / len(data)).tolist()
    }


def category_distribution(data: List[str]) -> Dict[str, Dict[str, Union[int, float]]]:
    """
    Calcula a distribuição de categorias em dados categóricos.

    Args:
        data: Lista de categorias

    Returns:
        Dicionário com categorias, contagens e porcentagens
    """
    # Contagem de frequência
    unique, counts = np.unique(data, return_counts=True)

    # Calcular porcentagens
    percentages = (counts / len(data)) * 100

    result = {}
    for i, category in enumerate(unique):
        result[category] = {
            'count': int(counts[i]),
            'percentage': float(percentages[i])
        }

    return result


# ---------------------- ANÁLISES DE CONFIABILIDADE ----------------------

def cronbach_alpha(data: np.ndarray) -> float:
    """
    Calcula o coeficiente alfa de Cronbach para um conjunto de itens.

    Args:
        data: Array 2D onde cada linha é um participante e cada coluna é um item

    Returns:
        Coeficiente alfa de Cronbach
    """
    # Número de itens
    n_items = data.shape[1]

    # Variâncias de cada item
    item_variances = np.var(data, axis=0, ddof=1)
    total_variance = np.var(np.sum(data, axis=1), ddof=1)

    # Cálculo do alfa de Cronbach
    alpha = (n_items / (n_items - 1)) * (1 - np.sum(item_variances) / total_variance)

    return float(alpha)


def item_total_correlations(data: np.ndarray) -> Dict[int, float]:
    """
    Calcula correlações item-total para cada item em um instrumento.

    Args:
        data: Array 2D onde cada linha é um participante e cada coluna é um item

    Returns:
        Dicionário com índice do item e correlação item-total
    """
    n_items = data.shape[1]
    correlations = {}

    for i in range(n_items):
        # Para cada item, calcular a pontuação total excluindo o item
        other_items = np.concatenate([data[:, :i], data[:, i + 1:]], axis=1)
        rest_score = np.sum(other_items, axis=1)

        # Calcular correlação entre o item e a pontuação total sem o item
        item_data = data[:, i]
        corr, _ = stats.pearsonr(item_data, rest_score)
        correlations[i] = float(corr)

    return correlations


# ---------------------- ANÁLISES COMPARATIVAS ----------------------

def independent_t_test(group1: np.ndarray, group2: np.ndarray) -> Dict[str, float]:
    """
    Realiza um teste t independente para comparar as médias de dois grupos.

    Args:
        group1: Dados do primeiro grupo
        group2: Dados do segundo grupo

    Returns:
        Dicionário com estatística t, valor p e tamanho do efeito (d de Cohen)
    """
    # Teste t
    t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=False)

    # Tamanho do efeito (d de Cohen)
    n1, n2 = len(group1), len(group2)
    s1, s2 = np.std(group1, ddof=1), np.std(group2, ddof=1)

    # Variância combinada
    s_pooled = np.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2))

    # d de Cohen
    cohen_d = (np.mean(group1) - np.mean(group2)) / s_pooled

    return {
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'cohen_d': float(cohen_d),
        'mean_diff': float(np.mean(group1) - np.mean(group2)),
        'group1_mean': float(np.mean(group1)),
        'group2_mean': float(np.mean(group2)),
        'group1_std': float(np.std(group1, ddof=1)),
        'group2_std': float(np.std(group2, ddof=1))
    }


def one_way_anova(groups: List[np.ndarray]) -> Dict[str, Union[float, Dict[str, float]]]:
    """
    Realiza uma ANOVA unidirecional para comparar médias de vários grupos.

    Args:
        groups: Lista de arrays, um para cada grupo

    Returns:
        Dicionário com estatística F, valor p, e médias dos grupos
    """
    # ANOVA
    f_stat, p_value = stats.f_oneway(*groups)

    # Calcular estatísticas por grupo
    group_stats = {}
    for i, group in enumerate(groups):
        group_stats[f'group_{i + 1}'] = {
            'mean': float(np.mean(group)),
            'std': float(np.std(group, ddof=1)),
            'n': len(group)
        }

    # Calcular eta-quadrado (tamanho do efeito)
    grand_mean = np.mean(np.concatenate(groups))
    ss_between = sum(len(group) * (np.mean(group) - grand_mean) ** 2 for group in groups)
    ss_total = sum((x - grand_mean) ** 2 for group in groups for x in group)
    eta_squared = ss_between / ss_total if ss_total != 0 else 0

    return {
        'f_statistic': float(f_stat),
        'p_value': float(p_value),
        'eta_squared': float(eta_squared),
        'group_stats': group_stats
    }


def manova(groups: List[np.ndarray], dependent_vars: int) -> Dict[str, Any]:
    """
    Implementa uma versão completa da MANOVA (Multivariate Analysis of Variance).

    Args:
        groups: Lista de arrays 2D, cada um com shape (n_sujeitos, n_vars)
        dependent_vars: Número de variáveis dependentes

    Returns:
        Dicionário com estatísticas da MANOVA
    """
    # Verificar se temos dados suficientes
    if len(groups) < 2:
        raise ValueError("MANOVA requer no mínimo dois grupos")

    for group in groups:
        if group.shape[1] != dependent_vars:
            raise ValueError(f"Cada grupo deve ter {dependent_vars} variáveis dependentes")

    # Número de grupos
    k = len(groups)

    # Número total de observações
    n_total = sum(group.shape[0] for group in groups)

    # Verifica se temos observações suficientes
    if n_total <= k + dependent_vars:
        raise ValueError("Número insuficiente de observações para MANOVA")

    # Calcular médias globais
    all_data = np.vstack(groups)
    grand_means = np.mean(all_data, axis=0)

    # Calcular médias de cada grupo
    group_means = [np.mean(group, axis=0) for group in groups]
    group_sizes = [group.shape[0] for group in groups]

    # Calcular matrizes SSCP (Sum of Squares and Cross Products)
    sscp_between = np.zeros((dependent_vars, dependent_vars))
    for i, (group_mean, n_group) in enumerate(zip(group_means, group_sizes)):
        mean_diff = (group_mean - grand_means).reshape(-1, 1)
        sscp_between += n_group * (mean_diff @ mean_diff.T)

    sscp_within = np.zeros((dependent_vars, dependent_vars))
    for i, group in enumerate(groups):
        for observation in group:
            obs_diff = (observation - group_means[i]).reshape(-1, 1)
            sscp_within += obs_diff @ obs_diff.T

    sscp_total = sscp_between + sscp_within

    # Calcular graus de liberdade
    df_between = k - 1
    df_within = n_total - k
    df_total = n_total - 1

    # Calcular estatísticas multivariadas
    try:
        # Inversa da matriz within
        w_inv = np.linalg.inv(sscp_within)

        # Produto das matrizes
        w_inv_b = w_inv @ sscp_between

        # Calcular autovalores para as estatísticas multivariadas
        eigenvalues = np.real(np.linalg.eigvals(w_inv_b))
        eigenvalues = eigenvalues[eigenvalues > 1e-10]  # Remover autovalores insignificantes

        s = min(df_between, dependent_vars)
        m = (np.abs(df_between - dependent_vars) - 1) / 2
        n = (df_within - dependent_vars - 1) / 2

        # Calcular Lambda de Wilks
        wilks_lambda = np.prod(1 / (1 + eigenvalues))

        # Calcular estatística F aproximada para Lambda de Wilks
        r = df_within - (dependent_vars - df_between + 1) / 2
        u = (dependent_vars * df_between - 2) / 4
        if dependent_vars * df_between == 2:
            t = 1
        else:
            t = np.sqrt((dependent_vars ** 2 * df_between ** 2 - 4) /
                        (dependent_vars ** 2 + df_between ** 2 - 5))

        degrees_f1 = dependent_vars * df_between
        degrees_f2 = r * t - 2 * u

        if degrees_f2 > 0:  # Verificar se os graus de liberdade são válidos
            wilks_f = (1 - wilks_lambda ** (1 / t)) / (wilks_lambda ** (1 / t)) * degrees_f2 / degrees_f1
            wilks_p = 1 - stats.f.cdf(wilks_f, degrees_f1, degrees_f2)
        else:
            wilks_f = np.nan
            wilks_p = np.nan

        # Calcular Traço de Pillai
        pillai_trace = np.sum(eigenvalues / (1 + eigenvalues))

        # Aproximação F para o Traço de Pillai
        pillai_f = (2 * n + s + 1) / (2 * m + s + 1) * (pillai_trace / (s - pillai_trace))
        pillai_p = 1 - stats.f.cdf(pillai_f, s * (2 * m + s + 1), s * (2 * n + s + 1))

        # Calcular Traço de Hotelling-Lawley
        hotelling_trace = np.sum(eigenvalues)

        # Aproximação F para o Traço de Hotelling-Lawley
        hotelling_f = (2 * (s * n + 1)) / (s * (2 * m + s + 1)) * hotelling_trace
        hotelling_p = 1 - stats.f.cdf(hotelling_f, s * (2 * m + s + 1), 2 * (s * n + 1))

        # Calcular Maior Raiz de Roy
        roys_root = np.max(eigenvalues)

        # Aproximação F para a Maior Raiz de Roy
        roys_f = roys_root * (df_within - dependent_vars + df_between) / dependent_vars
        roys_p = 1 - stats.f.cdf(roys_f, dependent_vars, df_within - dependent_vars + df_between)

    except np.linalg.LinAlgError:
        # Em caso de erro na inversão da matriz
        return {
            'error': 'Erro no cálculo matricial. A matriz within pode ser singular.',
            'individual_tests': {}
        }

    # Calcular estatísticas univariadas para cada variável dependente
    var_results = {}
    for var in range(dependent_vars):
        var_data = [group[:, var] for group in groups]
        anova_result = one_way_anova(var_data)
        var_results[f'var_{var + 1}'] = anova_result

    # Organizar resultados
    result = {
        'multivariate_tests': {
            'wilks_lambda': {
                'value': float(wilks_lambda),
                'f_approx': float(wilks_f) if not np.isnan(wilks_f) else None,
                'df1': int(degrees_f1) if not np.isnan(degrees_f1) else None,
                'df2': int(degrees_f2) if not np.isnan(degrees_f2) else None,
                'p_value': float(wilks_p) if not np.isnan(wilks_p) else None
            },
            'pillai_trace': {
                'value': float(pillai_trace),
                'f_approx': float(pillai_f),
                'df1': int(s * (2 * m + s + 1)),
                'df2': int(s * (2 * n + s + 1)),
                'p_value': float(pillai_p)
            },
            'hotelling_trace': {
                'value': float(hotelling_trace),
                'f_approx': float(hotelling_f),
                'df1': int(s * (2 * m + s + 1)),
                'df2': int(2 * (s * n + 1)),
                'p_value': float(hotelling_p)
            },
            'roys_root': {
                'value': float(roys_root),
                'f_approx': float(roys_f),
                'df1': int(dependent_vars),
                'df2': int(df_within - dependent_vars + df_between),
                'p_value': float(roys_p)
            }
        },
        'eigenvalues': [float(e) for e in eigenvalues],
        'n_groups': k,
        'n_total': n_total,
        'n_dependent_vars': dependent_vars,
        'df_between': df_between,
        'df_within': df_within,
        'df_total': df_total,
        'individual_tests': var_results
    }

    return result


# ---------------------- ANÁLISES CORRELACIONAIS ----------------------

def pearson_correlation(x: np.ndarray, y: np.ndarray) -> Dict[str, float]:
    """
    Calcula a correlação de Pearson entre duas variáveis.

    Args:
        x: Primeira variável
        y: Segunda variável

    Returns:
        Dicionário com coeficiente de correlação e valor p
    """
    corr, p_value = stats.pearsonr(x, y)

    return {
        'correlation': float(corr),
        'p_value': float(p_value),
        'n': len(x)
    }


def correlation_matrix(data: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Calcula a matriz de correlação entre múltiplas variáveis.

    Args:
        data: Array 2D onde cada coluna é uma variável

    Returns:
        Dicionário com matriz de correlação e p-valores
    """
    n_vars = data.shape[1]
    corr_matrix = np.zeros((n_vars, n_vars))
    p_matrix = np.zeros((n_vars, n_vars))

    for i in range(n_vars):
        for j in range(i, n_vars):
            if i == j:
                corr_matrix[i, j] = 1.0
                p_matrix[i, j] = 0.0
            else:
                corr, p = stats.pearsonr(data[:, i], data[:, j])
                corr_matrix[i, j] = corr
                corr_matrix[j, i] = corr  # Matriz é simétrica
                p_matrix[i, j] = p
                p_matrix[j, i] = p  # Matriz é simétrica

    return {
        'correlation_matrix': corr_matrix,
        'p_value_matrix': p_matrix
    }


# ---------------------- ANÁLISES LONGITUDINAIS ----------------------

def paired_t_test(pre: np.ndarray, post: np.ndarray) -> Dict[str, float]:
    """
    Realiza um teste t pareado para comparar medidas repetidas (pré e pós).

    Args:
        pre: Medidas pré-intervenção
        post: Medidas pós-intervenção

    Returns:
        Dicionário com estatística t, valor p e tamanho do efeito (d de Cohen)
    """
    # Teste t pareado
    t_stat, p_value = stats.ttest_rel(pre, post)

    # Diferenças
    differences = post - pre

    # Tamanho do efeito (d de Cohen para amostras pareadas)
    cohen_d = np.mean(differences) / np.std(differences, ddof=1)

    return {
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'cohen_d': float(cohen_d),
        'mean_diff': float(np.mean(differences)),
        'pre_mean': float(np.mean(pre)),
        'post_mean': float(np.mean(post)),
        'pre_std': float(np.std(pre, ddof=1)),
        'post_std': float(np.std(post, ddof=1))
    }


def repeated_measures_anova(measurements: List[np.ndarray]) -> Dict[str, Any]:
    """
    Implementa uma ANOVA de medidas repetidas para múltiplas observações dos mesmos sujeitos.

    Args:
        measurements: Lista de arrays, um para cada ponto de tempo

    Returns:
        Dicionário com estatísticas da ANOVA de medidas repetidas
    """
    # Validar que todos os arrays têm o mesmo comprimento
    if len(set(len(m) for m in measurements)) > 1:
        raise ValueError("Todos os arrays de medidas devem ter o mesmo comprimento")

    n_subjects = len(measurements[0])
    n_times = len(measurements)

    # Converter para matriz
    data = np.array(measurements).T  # shape: (n_subjects, n_times)

    # Calcular médias
    subject_means = np.mean(data, axis=1)
    time_means = np.mean(data, axis=0)
    grand_mean = np.mean(data)

    # Soma dos quadrados
    ss_total = np.sum((data - grand_mean) ** 2)
    ss_subjects = n_times * np.sum((subject_means - grand_mean) ** 2)
    ss_times = n_subjects * np.sum((time_means - grand_mean) ** 2)
    ss_error = ss_total - ss_subjects - ss_times

    # Graus de liberdade
    df_subjects = n_subjects - 1
    df_times = n_times - 1
    df_error = df_subjects * df_times

    # Médias quadradas
    ms_subjects = ss_subjects / df_subjects if df_subjects != 0 else 0
    ms_times = ss_times / df_times if df_times != 0 else 0
    ms_error = ss_error / df_error if df_error != 0 else 0

    # Estatística F para efeito do tempo
    f_time = ms_times / ms_error if ms_error != 0 else 0
    p_time = 1 - stats.f.cdf(f_time, df_times, df_error)

    # Tamanho do efeito (eta-quadrado parcial)
    eta_squared = ss_times / (ss_times + ss_error) if (ss_times + ss_error) != 0 else 0

    # Estatísticas para cada ponto de tempo
    time_stats = {}
    for i, time_data in enumerate(np.transpose(data)):
        time_stats[f'time_{i + 1}'] = {
            'mean': float(np.mean(time_data)),
            'std': float(np.std(time_data, ddof=1))
        }

    return {
        'f_statistic': float(f_time),
        'p_value': float(p_time),
        'eta_squared': float(eta_squared),
        'time_stats': time_stats,
        'df_time': int(df_times),
        'df_error': int(df_error)
    }