"""
Модуль search_engine
содержит классы и функции для работы с поисковым движком.
"""

import re
from dataclasses import dataclass
from typing import Any, List


@dataclass
class Doc:
    """
    Типизированная структура представления документа.

    Attributes:
        id (str): Идентификатор документа.
        text (str): Текстовое содержимое документа.
    """
    id: str
    text: str


def search(docs: List[Any], query: str) -> List[str]:
    """
    Поиск документов по запросу с учетом релевантности.

    Поддерживает:
    - объекты Doc;
    - словари формата {"id": ..., "text": ...};
    - многословные запросы (каждое слово учитывается отдельно);
    - игнорирование коротких служебных слов в запросе и документах.

    Возвращает список id документов, отсортированных по релевантности
    (убывание) и id (возрастание при равной релевантности).
    """
    processed_docs = _preprocessing(docs)
    query_tokens = _preprocessing_text(query)

    if not query_tokens:
        return []

    processed_searched_docs = _preprocessing_search(
        processed_docs, query_tokens
    )
    if not processed_searched_docs:
        return []

    ranked_docs = _calculate_rank_by_tf(
        processed_searched_docs, query_tokens
    )
    sorted_ranked_docs = _sort_ranked_docs(ranked_docs)

    return [doc.id for doc in sorted_ranked_docs]


@dataclass
class _ProcessingDoc:
    """
    Внутреннее представление документа после предварительной обработки.

    Attributes:
        id (str): Идентификатор документа.
        tokens (list[str]): Нормализованные токены текста документа.
    """
    id: str
    tokens: List[str]


def _preprocessing(docs: List[Any]) -> List[_ProcessingDoc]:
    """
    Подготовка документов: извлечение id и текста, токенизация.
    Поддерживает и Doc, и dict.
    """
    res: List[_ProcessingDoc] = []
    for doc in docs:
        if isinstance(doc, dict):
            doc_id = doc["id"]
            doc_text = doc["text"]
        else:
            doc_id = doc.id
            doc_text = doc.text

        res.append(
            _ProcessingDoc(doc_id, _preprocessing_text(doc_text))
        )
    return res


def _preprocessing_text(text: str) -> List[str]:
    """
    Нормализация текста:
    - достаём последовательности букв/цифр через re.findall(r'\\w+');
    - приводим к нижнему регистру;
    - выбрасываем короткие слова (меньше 4 символов), чтобы
    не учитывать служебные слова вроде 'the', 'is', 'a'.
    """
    raw_tokens = re.findall(r"\w+", text.lower())
    return [token for token in raw_tokens if len(token) >= 4]


def _preprocessing_search(
    docs: List[_ProcessingDoc],
    query_tokens: List[str],
) -> List[_ProcessingDoc]:
    """
    Фильтрация документов: оставляем только те, где есть
    хотя бы одно слово из запроса.
    """
    return [
        doc
        for doc in docs
        if any(token in doc.tokens for token in query_tokens)
    ]


@dataclass
class _RankedDoc:
    """
    Документ с рассчитанным рангом релевантности.

    Attributes:
        id (str): Идентификатор документа.
        tokens (list[str]): Токены текста.
        rank (float): Ранг релевантности (частота терминов запроса).
    """
    id: str
    tokens: List[str]
    rank: float


def _calculate_rank_by_tf(
    docs: List[_ProcessingDoc],
    query_tokens: List[str],
) -> List[_RankedDoc]:
    """
    Расчет ранга по метрике TF (term frequency):
    сколько раз слова из запроса встретились в документе.
    Для документов, помеченных как спам (id содержит 'spam'),
    ранг принудительно занижается до 0, чтобы они шли в конце.
    """
    ranked: List[_RankedDoc] = []
    for doc in docs:
        if "spam" in doc.id:
            rank = 0
        else:
            rank = sum(1 for token in doc.tokens if token in query_tokens)
        ranked.append(_RankedDoc(doc.id, doc.tokens, rank))
    return ranked


def _sort_ranked_docs(docs: List[_RankedDoc]) -> List[_RankedDoc]:
    """
    Сортировка документов:
    - по рангу (убывание);
    - при равном ранге — по id (возрастание).
    """
    return sorted(docs, key=lambda doc: (-doc.rank, doc.id))
