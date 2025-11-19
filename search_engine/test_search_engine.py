"""Tests for search engine."""
from search_engine.search_engine import search


def test_search_finds_documents_with_query():
    """Test finding documents with a query."""
    doc1 = {'id': 'doc1', 'text': "I can't shoot straight unless I've had a pint!"}
    doc2 = {'id': 'doc2', 'text': "Don't shoot shoot shoot that thing at me."}
    doc3 = {'id': 'doc3', 'text': "I'm your shooter."}
    docs = [doc1, doc2, doc3]

    result = search(docs, 'shoot')
    assert result == ['doc1', 'doc2', 'doc3']


def test_search_returns_empty_array_for_empty_docs():
    """Test with an empty list of documents."""
    result = search([], 'shoot')
    assert result == []


def test_search_returns_empty_array_when_no_match():
    """Test when no documents match the query."""
    doc1 = {'id': 'doc1', 'text': 'Hello world'}
    docs = [doc1]

    result = search(docs, 'shoot')
    assert result == []


def test_search_finds_single_document():
    """Test finding a single document."""
    doc1 = {'id': 'doc1', 'text': 'I can shoot'}
    docs = [doc1]

    result = search(docs, 'shoot')
    assert result == ['doc1']
