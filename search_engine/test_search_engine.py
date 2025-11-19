"""Tests for search engine."""
from search_engine.search_engine import search


def test_search_base():
    """Test base search functionality."""
    doc1 = {'id': 'doc1', 'text': "I can't shoot straight unless I've had a pint!"}
    doc2 = {'id': 'doc2', 'text': "Don't shoot shoot shoot that thing at me."}
    doc3 = {'id': 'doc3', 'text': "I'm your shooter."}
    docs = [doc1, doc2, doc3]

    assert search(docs, 'shoot') == ['doc1', 'doc2']


def test_search_with_punctuation():
    """Test search handles punctuation."""
    doc1 = {'id': 'doc1', 'text': "I can't shoot straight unless I've had a pint!"}
    docs = [doc1]
    assert search(docs, 'pint') == ['doc1']
    assert search(docs, 'pint!') == ['doc1']


def test_search_with_case_insensitivity():
    """Test search is case-insensitive."""
    doc1 = {'id': 'doc1', 'text': 'Shoot first, ask questions later.'}
    docs = [doc1]
    assert search(docs, 'shoot') == ['doc1']
    assert search(docs, 'Shoot') == ['doc1']


def test_search_empty_or_no_match():
    """Test empty results for empty docs or no match."""
    docs = [
        {'id': 'doc1', 'text': 'Some random text.'},
    ]
    assert search([], 'shoot') == []
    assert search(docs, 'nofound') == []
    assert search(docs, '!') == []

