"""PY-23: Egeria's query parameter is `startingAtEnd` (ClassificationExplorerResource); pyegeria sent `startAtEnd`."""
import asyncio
import pathlib
import re

import pytest

from pyegeria.omvs.classification_explorer import ClassificationExplorer

ROOT = pathlib.Path(__file__).resolve().parents[2] / "pyegeria"


@pytest.fixture(autouse=True)
def _no_connection(monkeypatch):
    monkeypatch.setattr(ClassificationExplorer, "check_connection", lambda self: "test")


def _client():
    return ClassificationExplorer("view-server", "https://egeria.example:9443", "user", "pwd")


def _capture(monkeypatch, client, attr):
    seen = {}

    async def fake(url, *a, **k):
        seen["url"] = url
        return []
    monkeypatch.setattr(client, attr, fake)
    return seen


def test_no_pyegeria_source_sends_startAtEnd():
    bad = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*.py") if re.search(r"[?&]startAtEnd=", p.read_text())]
    assert bad == []


@pytest.mark.parametrize("rel", [None, "SemanticAssignment"])
def test_get_related_elements_sends_startingAtEnd(monkeypatch, rel):
    c = _client()
    seen = _capture(monkeypatch, c, "_async_get_results_body_request")
    asyncio.run(c._async_get_related_elements("g1", rel, start_at_end=1))
    assert "?startingAtEnd=1" in seen["url"] and "startAtEnd" not in seen["url"]


def test_start_at_end_two_is_sent(monkeypatch):
    c = _client()
    seen = _capture(monkeypatch, c, "_async_get_results_body_request")
    asyncio.run(c._async_get_related_elements("g1", "SemanticAssignment", start_at_end=2))
    assert seen["url"].endswith("?startingAtEnd=2")


def test_with_property_value_sends_startingAtEnd(monkeypatch):
    c = _client()
    seen = _capture(monkeypatch, c, "_async_find_request")
    asyncio.run(c._async_get_related_elements_with_property_value("g1", "SemanticAssignment", "v", start_at_end=1))
    assert "/with-exact-property-value?startingAtEnd=1" in seen["url"]
