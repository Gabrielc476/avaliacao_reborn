# utils/instrument_plugins.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class InstrumentProcessor(ABC):
    """
    Interface para processadores de instrumentos psicológicos
    """

    @property
    @abstractmethod
    def code(self) -> str:
        """
        Retorna o código único do instrumento
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Retorna o nome do instrumento
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Retorna a descrição do instrumento
        """
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """
        Retorna a versão do instrumento
        """
        pass

    @property
    @abstractmethod
    def structure(self) -> Dict[str, Any]:
        """
        Retorna a estrutura do instrumento (perguntas, escalas, etc.)
        """
        pass

    @abstractmethod
    def process(self, responses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa as respostas e retorna os resultados

        Args:
            responses: Lista de respostas ao instrumento

        Returns:
            Lista de resultados processados
        """
        pass

    @abstractmethod
    def extract_responses(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extrai as respostas específicas do instrumento dos dados

        Args:
            data: Dados brutos

        Returns:
            Lista de respostas específicas para o instrumento
        """
        pass


class DASS21Processor(InstrumentProcessor):
    """
    Processador para o instrumento DASS-21
    """

    @property
    def code(self) -> str:
        return "DASS21"

    @property
    def name(self) -> str:
        return "Depression Anxiety Stress Scales - 21"

    @property
    def description(self) -> str:
        return "Escala de 21 itens que mede os estados emocionais negativos de depressão, ansiedade e estresse"

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def structure(self) -> Dict[str, Any]:
        return {
            "scales": ["depression", "anxiety", "stress"],
            "questions": 21,
            "scale_items": {
                "depression": [3, 5, 10, 13, 16, 17, 21],
                "anxiety": [2, 4, 7, 9, 15, 19, 20],
                "stress": [1, 6, 8, 11, 12, 14, 18]
            },
            "response_options": [
                {"value": 0, "label": "Não se aplicou de maneira alguma"},
                {"value": 1, "label": "Aplicou-se em algum grau, ou por algum tempo"},
                {"value": 2, "label": "Aplicou-se em um grau considerável, ou por uma boa parte do tempo"},
                {"value": 3, "label": "Aplicou-se muito, ou na maioria do tempo"}
            ]
        }

    def process(self, responses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calcula as pontuações para respostas do DASS-21
        """
        results = []

        for response in responses:
            # Verificar se todas as perguntas necessárias estão presentes
            valid = all(f"q{i}" in response for i in range(1, 22))

            if not valid:
                # Adicionar resultado vazio se os dados estiverem incompletos
                results.append({
                    "participant_id": response.get("participant_id"),
                    "complete": False,
                    "scores": None,
                    "categories": None,
                    "error": "Dados incompletos"
                })
                continue

            # Cálculo das subescalas usando a estrutura definida
            depression_items = self.structure["scale_items"]["depression"]
            anxiety_items = self.structure["scale_items"]["anxiety"]
            stress_items = self.structure["scale_items"]["stress"]

            depression_score = sum(response[f"q{i}"] for i in depression_items)
            anxiety_score = sum(response[f"q{i}"] for i in anxiety_items)
            stress_score = sum(response[f"q{i}"] for i in stress_items)

            # Classificação baseada nas pontuações
            depression_category = self._classify_depression(depression_score)
            anxiety_category = self._classify_anxiety(anxiety_score)
            stress_category = self._classify_stress(stress_score)

            # Montar o resultado
            result = {
                "participant_id": response.get("participant_id"),
                "complete": True,
                "scores": {
                    "depression": depression_score,
                    "anxiety": anxiety_score,
                    "stress": stress_score,
                    "total": depression_score + anxiety_score + stress_score
                },
                "categories": {
                    "depression": depression_category,
                    "anxiety": anxiety_category,
                    "stress": stress_category
                }
            }

            results.append(result)

        return results

    def extract_responses(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extrai as respostas do DASS-21 dos dados
        """
        dass21_responses = []

        # Prefixo usado para identificar perguntas do DASS-21 nos dados
        prefix = f"{self.code.lower()}_"

        for item in data:
            response = {}

            # Identificar participante
            response["participant_id"] = item.get("id")

            # Extrair respostas específicas do DASS-21
            for key, value in item.items():
                # Se a chave começa com o prefixo do DASS-21
                if key.startswith(prefix):
                    # Remover o prefixo e armazenar
                    question_key = key.replace(prefix, "")
                    response[question_key] = value

            # Adicionar à lista se houver respostas para o DASS-21
            if len(response) > 1:  # Mais do que apenas o participant_id
                dass21_responses.append(response)

        return dass21_responses

    def _classify_depression(self, score: int) -> str:
        # Classificação para depressão
        if score <= 9:
            return "normal"
        elif score <= 13:
            return "mild"
        elif score <= 20:
            return "moderate"
        elif score <= 27:
            return "severe"
        else:
            return "extremely_severe"

    def _classify_anxiety(self, score: int) -> str:
        # Classificação para ansiedade
        if score <= 7:
            return "normal"
        elif score <= 9:
            return "mild"
        elif score <= 14:
            return "moderate"
        elif score <= 19:
            return "severe"
        else:
            return "extremely_severe"

    def _classify_stress(self, score: int) -> str:
        # Classificação para estresse
        if score <= 14:
            return "normal"
        elif score <= 18:
            return "mild"
        elif score <= 25:
            return "moderate"
        elif score <= 33:
            return "severe"
        else:
            return "extremely_severe"


# Registro de processadores de instrumentos
class InstrumentRegistry:
    """
    Registro para processadores de instrumentos
    """

    _processors = {}

    @classmethod
    def register(cls, processor: InstrumentProcessor):
        """
        Registra um processador de instrumento
        """
        cls._processors[processor.code] = processor

    @classmethod
    def get(cls, code: str) -> InstrumentProcessor:
        """
        Obtém um processador pelo código do instrumento

        Args:
            code: Código do instrumento

        Returns:
            Processador do instrumento

        Raises:
            ValueError: Se o processador não for encontrado
        """
        if code not in cls._processors:
            raise ValueError(f"Processador para instrumento '{code}' não encontrado")

        return cls._processors[code]

    @classmethod
    def list_all(cls) -> List[Dict[str, str]]:
        """
        Lista todos os processadores registrados

        Returns:
            Lista de informações básicas sobre os processadores
        """
        return [
            {
                "code": processor.code,
                "name": processor.name,
                "description": processor.description,
                "version": processor.version
            }
            for processor in cls._processors.values()
        ]


# Registrar processadores conhecidos
InstrumentRegistry.register(DASS21Processor())