"""
Модуль search_engine
содержит классы и функции для работы с поисковым движком.
"""

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List


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
    Поиск документов по запросу с использованием обратного индекса.

    Этапы:
    1. Подготовка данных (токенизация).
    2. Построение обратного индекса.
    3. Быстрый отбор кандидатов (через индекс).
    4. Ранжирование (релевантность, спам в конец).
    """
    processed_docs = _preprocessing(docs)
    query_tokens = _preprocessing_text(query)

    if not query_tokens:
        return []

    # Строим индекс и фильтруем кандидатов (вместо перебора всех docs)
    index = _build_inverted_index(docs)
    candidates = _get_candidates_by_index(index, query_tokens, processed_docs)

    if not candidates:
        return []

    ranked_docs = _calculate_rank(candidates, query_tokens)
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
            _ProcessingDoc(doc_id, _preprocessing_text(doc_text)),
        )
    return res


def _preprocessing_text(text: str) -> List[str]:
    """
    Нормализация текста:
    - достаём последовательности букв/цифр;
    - приводим к нижнему регистру;
    - выбрасываем слова короче 4 символов.
    """
    raw_tokens = re.findall(r"\w+", text.lower())
    return [token for token in raw_tokens if len(token) >= 4]


def _build_inverted_index(docs: List[Any]) -> Dict[str, Dict[str, int]]:
    """
    Построение обратного индекса:
    term -> {doc_id: term_frequency_in_doc}
    """
    index: Dict[str, Dict[str, int]] = defaultdict(dict)
    for d in docs:
        doc_id = d["id"] if isinstance(d, dict) else d.id
        text = d["text"] if isinstance(d, dict) else d.text
        # Используем ту же токенизацию, что и для запросов
        tokens = _preprocessing_text(text)
        freqs = Counter(tokens)
        for term, cnt in freqs.items():
            index[term][doc_id] = cnt
    return index


def _get_candidates_by_index(
    index: Dict[str, Dict[str, int]],
    query_tokens: List[str],
    processed_docs: List[_ProcessingDoc],
) -> List[_ProcessingDoc]:
    """
    Отбор документов-кандидатов через обратный индекс.
    Если слово из запроса есть в индексе -> добавляем все docs с этим словом.
    """
    candidate_ids = set()
    for token in query_tokens:
        # Объединяем множества ID документов для каждого слова запроса
        candidate_ids |= set(index.get(token, {}).keys())

    # Быстрый доступ к объектам _ProcessingDoc по ID
    id_to_doc = {doc.id: doc for doc in processed_docs}

    return [
        id_to_doc[doc_id]
        for doc_id in candidate_ids
        if doc_id in id_to_doc
    ]


@dataclass
class _RankedDoc:
    """
    Документ с рассчитанным рангом релевантности.

    Attributes:
        id (str): Идентификатор документа.
        tokens (list[str]): Токены текста.
        match_count (int): Количество уникальных слов из запроса.
        total_occurrences (int): Общее число вхождений слов запроса.
    """
    id: str
    tokens: List[str]
    match_count: int
    total_occurrences: int


def _calculate_rank(
    docs: List[_ProcessingDoc],
    query_tokens: List[str],
) -> List[_RankedDoc]:
    """
    Расчет ранга (как в шаге 4):
    1. match_count — уникальные слова.
    2. total_occurrences — сумма вхождений.

    Спам (id содержит 'spam') улетает в конец (rank=0).
    """
    unique_query_tokens = set(query_tokens)
    ranked: List[_RankedDoc] = []

    for doc in docs:
        if "spam" in doc.id:
            match_count = 0
            total_occurrences = 0
        else:
            found_tokens = [
                token
                for token in doc.tokens
                if token in unique_query_tokens
            ]
            match_count = len(set(found_tokens))
            total_occurrences = len(found_tokens)

        ranked.append(
            _RankedDoc(doc.id, doc.tokens, match_count, total_occurrences),
        )
    return ranked


def _sort_ranked_docs(docs: List[_RankedDoc]) -> List[_RankedDoc]:
    """
    Сортировка:
    1. match_count (убывание)
    2. total_occurrences (убывание)
    3. id (возрастание)
    """
    return sorted(
        docs,
        key=lambda doc: (
            -doc.match_count,
            -doc.total_occurrences,
            doc.id,
        ),
    )
