# utils/__init__.py
from .password import PasswordUtils
from .jwt import JWTUtils, TokenData
from .instrument_plugins import (
    InstrumentProcessor,
    DASS21Processor,
    InstrumentRegistry
)
from .statistical_tests import (
    # Análises descritivas
    calculate_descriptive_stats,
    frequency_distribution,
    category_distribution,

    # Análises de confiabilidade
    cronbach_alpha,
    item_total_correlations,

    # Análises comparativas
    independent_t_test,
    one_way_anova,
    manova,

    # Análises correlacionais
    pearson_correlation,
    correlation_matrix,

    # Análises longitudinais
    paired_t_test,
    repeated_measures_anova
)

__all__ = [
    # Utilidades de segurança
    "PasswordUtils",
    "JWTUtils",
    "TokenData",

    # Classes de instrumentos
    "InstrumentProcessor",
    "DASS21Processor",
    "InstrumentRegistry",

    # Funções estatísticas
    "calculate_descriptive_stats",
    "frequency_distribution",
    "category_distribution",
    "cronbach_alpha",
    "item_total_correlations",
    "independent_t_test",
    "one_way_anova",
    "manova",
    "pearson_correlation",
    "correlation_matrix",
    "paired_t_test",
    "repeated_measures_anova"
]