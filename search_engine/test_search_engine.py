"""
Тестирование поискового движка
"""
from search_engine.search_engine import Doc, search


def test_search_hello():
    docs = [
        Doc("1", "hello world"),
        Doc("2", "hi there"),
        Doc("3", "world hello"),
    ]
    assert search(docs, "hello") == ["1", "3"]


def test_search_not_found():
    docs = [Doc("1", "foo bar")]
    assert search(docs, "baz") == []


def test_search_exact_word():
    docs = [Doc("1", "cat cats caterpillar")]
    assert search(docs, "cat") == ["1"]


def test_search_empty():
    docs = []
    assert search(docs, "cat") == []


def test_search_full_empty():
    docs = []
    assert search(docs, "") == []


def test_search_with_space():
    docs = [
        Doc("1", "foo bar"),
    ]
    assert search(docs, " ") == []


def test_search_space():
    docs = [
        Doc("1", "      "),
    ]
    assert search(docs, " ") == []


def test_search_preprocessing():
    docs = [
        Doc("1", "foo... bar!"),
    ]
    assert search(docs, "foo") == ["1"]
    assert search(docs, "foo...") == ["1"]
    assert search(docs, "bar") == ["1"]
    assert search(docs, "bar!") == ["1"]

    docs = [
        Doc("1", "Hello!!!! _WorlD"),
        Doc("2", "hellow world"),  # not in result
    ]
    assert search(docs, "hello") == ["1"]


def test_search_multiple_words():
    docs = [
        Doc("1", "hello world"),
        Doc("2", "Hello!!!! _WorlD"),
        Doc("3", "hellow world"),
        Doc("4", "hellow worldw"),
    ]
    assert search(docs, "hello world") == ["1", "2", "3"]


def test_search_requirements_doc():
    """
    Тут лежат тесты описанные в требовании
    """
    docs = [
        Doc("doc1", "I can't shoot straight unless I've had a pint!"),
    ]
    assert search(docs, "pint") == ["doc1"]
    assert search(docs, "pint!") == ["doc1"]


def test_search_ranking():
    docs = [
        Doc("doc1", "I can't shoot straight unless I've had a pint!"),
        Doc("doc2", "Don't shoot shoot shoot that thing at me."),
        Doc("doc3", "I'm your shooter."),
    ]
    assert search(docs, "shoot") == ["doc2", "doc1"]


def test_search_same_rank():
    docs = [
        Doc("doc1", "Don't shoot shoot shoot that thing at me."),
        Doc("doc2", "Don't shoot shoot shoot that thing at me."),
        Doc("doc3", "Don't shoot shoot shoot that thing at me.."),
    ]
    assert search(docs, "shoot") == ["doc1", "doc2", "doc3"]


def test_fuzzy_search_shoot_at_me():
    docs = [
        Doc("doc1", "I can't shoot straight unless I've had a pint!"),
        Doc("doc2", "Don't shoot shoot shoot that thing at me."),
        Doc("doc3", "I'm your shooter."),
    ]
    assert search(docs, "shoot at me") == ["doc2", "doc1"]


def test_fuzzy_search_rank_by_words_and_occurrences():
    docs = [
        Doc("doc1", "foo bar baz"),
        Doc("doc2", "foo foo qux"),
        Doc("doc3", "foo bar qux qux"),
    ]
    # запрос: 3 слова, но у доков совпадают по-разному
    # doc3: foo, bar, qux -> 3 разных слова, много вхождений
    # doc2: foo, qux -> 2 разных
    # doc1: foo, bar -> 2 разных, но меньше вхождений, чем у doc2
    assert search(docs, "foo bar qux") == ["doc3", "doc2", "doc1"]
