"""Search engine module."""


def search(docs, query):
    """
    Search for documents containing the query string.

    Args:
        docs: A list of documents, where each doc is a dict with 'id' and 'text'.
        query: The string to search for.

    Returns:
        A list of document IDs that contain the query.
    """
    if not docs:
        return []

    return [doc['id'] for doc in docs if query in doc['text']]

