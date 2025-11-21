"""
Модуль search_engine
содержит классы и функции для работы с поисковым движком.
"""

import math
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
    Поиск с использованием обратного индекса и ранжирования TF‑IDF.

    Этапы:
    1. Токенизация документов и запроса.
    2. Построение обратного индекса (term -> {doc_id: count}).
    3. Отбор кандидатов по индексу.
    4. Ранжирование суммой TF‑IDF по словам запроса.
    5. Сортировка по убыванию score, затем по id.
    """
    processed_docs = _preprocessing(docs)
    query_tokens = _preprocessing_text(query)
    if not query_tokens:
        return []

    index = _build_inverted_index(docs)
    candidates = _get_candidates_by_index(index, query_tokens, processed_docs)
    if not candidates:
        return []

    ranked_docs = _rank_by_tfidf(
        candidates,
        query_tokens,
        index,
        total_docs=len(processed_docs),
    )
    sorted_docs = _sort_ranked_docs(ranked_docs)
    return [d.id for d in sorted_docs]


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
    Поддерживает Doc и dict.
    """
    res: List[_ProcessingDoc] = []
    for doc in docs:
        if isinstance(doc, dict):
            doc_id = doc["id"]
            doc_text = doc["text"]
        else:
            doc_id = doc.id
            doc_text = doc.text
        res.append(_ProcessingDoc(doc_id, _preprocessing_text(doc_text)))
    return res


def _preprocessing_text(text: str) -> List[str]:
    """
    Нормализация текста:
    - извлекаем последовательности букв/цифр;
    - приводим к нижнему регистру;
    - отбрасываем слова короче 4 символов.
    """
    raw = re.findall(r"\w+", text.lower())
    return [t for t in raw if len(t) >= 4]


def _build_inverted_index(docs: List[Any]) -> Dict[str, Dict[str, int]]:
    """
    Построение обратного индекса:
    term -> {doc_id: количество вхождений термина в документе}.
    """
    index: Dict[str, Dict[str, int]] = defaultdict(dict)
    for d in docs:
        doc_id = d["id"] if isinstance(d, dict) else d.id
        text = d["text"] if isinstance(d, dict) else d.text
        freqs = Counter(_preprocessing_text(text))
        for term, cnt in freqs.items():
            index[term][doc_id] = cnt
    return index


def _get_candidates_by_index(
    index: Dict[str, Dict[str, int]],
    query_tokens: List[str],
    processed_docs: List[_ProcessingDoc],
) -> List[_ProcessingDoc]:
    """
    Отбор документов, содержащих хотя бы одно слово из запроса.
    """
    candidate_ids = set()
    for token in query_tokens:
        candidate_ids |= set(index.get(token, {}).keys())

    id_to_doc = {doc.id: doc for doc in processed_docs}
    return [
        id_to_doc[doc_id]
        for doc_id in candidate_ids
        if doc_id in id_to_doc
    ]


@dataclass
class _RankedDoc:
    """
    Документ с рассчитанным TF‑IDF score.

    Attributes:
        id (str): Идентификатор документа.
        score (float): Суммарный TF‑IDF по словам запроса.
    """
    id: str
    score: float


def _rank_by_tfidf(
    docs: List[_ProcessingDoc],
    query_tokens: List[str],
    index: Dict[str, Dict[str, int]],
    total_docs: int,
) -> List[_RankedDoc]:
    """
    Подсчёт ранга по TF‑IDF.

    Определения:
    - TF = count(term, doc)  (сырая частота без нормализации)
    - IDF = log(N / (df + 1)), где N — число документов,
      df — число документов, содержащих term.

    Спам (id содержит 'spam') получает нулевой score.
    """
    unique_terms = set(query_tokens)
    ranked: List[_RankedDoc] = []

    for doc in docs:
        if "spam" in doc.id:
            ranked.append(_RankedDoc(doc.id, 0.0))
            continue

        score = 0.0
        for term in unique_terms:
            postings = index.get(term)
            if not postings or doc.id not in postings:
                continue
            tf = postings[doc.id]
            df = len(postings)
            idf = math.log((total_docs + 1) / (df + 1)) + 1
            score += tf * idf

        ranked.append(_RankedDoc(doc.id, score))

    return ranked


def _sort_ranked_docs(docs: List[_RankedDoc]) -> List[_RankedDoc]:
    """
    Сортировка: по score (убывание), затем по id (возрастание).
    """
    return sorted(docs, key=lambda d: (-d.score, d.id))
