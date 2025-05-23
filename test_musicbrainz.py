import pytest
from api.musicbrainz import search_release

def test_search_release_valid_artist_title(monkeypatch):
    class DummyResponse:
        def raise_for_status(self): pass
        def json(self): return {"releases": [{"title": "Hello", "artist": "Adele"}]}

    def dummy_get(*args, **kwargs):
        return DummyResponse()

    monkeypatch.setattr("requests.get", dummy_get)
    results = search_release("Adele", "Hello")
    assert isinstance(results, list)
    assert results[0]["title"] == "Hello"
