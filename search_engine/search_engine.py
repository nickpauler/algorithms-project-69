"""Search engine module."""
import re


def normalize_text(text):
    """
    Нормализует текст: извлекает слова, приводит к нижнему регистру.

    Args:
        text: Входная строка.

    Returns:
        Список слов (термов) в нижнем регистре.
    """
    return [word.lower() for word in re.findall(r'\w+', text)]


def search(docs, query):
    """
    Поиск документов по запросу с учетом нормализации.

    Args:
        docs: Список документов.
        query: Поисковый запрос (слово).

    Returns:
        Список id документов, содержащих искомое слово.
    """
    if not query:
        return []

    # Нормализуем поисковый запрос. Так как это одно слово, берем первый элемент.
    # Если запрос пустой или состоит только из знаков, findall вернет [],
    # что обработается далее.
    processed_query_list = normalize_text(query)
    if not processed_query_list:
        return []
    search_term = processed_query_list[0]

    result = []
    for doc in docs:
        # Нормализуем текст документа
        doc_terms = normalize_text(doc['text'])
        if search_term in doc_terms:
            result.append(doc['id'])

    return result

