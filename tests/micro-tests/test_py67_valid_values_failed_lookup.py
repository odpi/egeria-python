"""PY-67: a failed valid-values lookup is not "no valid values"."""
import asyncio
import importlib
import threading
from unittest.mock import AsyncMock, MagicMock

import pytest

from pyegeria import PyegeriaTimeoutException
from pyegeria.core._server_client import ServerClient


class _Stub(ServerClient):
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return "http://x"


def _client(request):
    c = _Stub.__new__(_Stub)
    c._valid_value_cache = {}
    c.server_name = "qs-view-server"
    c._async_make_request = request
    return c


def _resp(elements):
    r = MagicMock()
    r.json.return_value = {"elements": elements}
    return r


def test_a_failed_lookup_raises_and_is_not_cached():
    c = _client(AsyncMock(side_effect=PyegeriaTimeoutException({"caller": "t"}, {"endpoint": "x"}, None)))
    with pytest.raises(PyegeriaTimeoutException):
        asyncio.run(c._async_get_valid_metadata_values("status"))
    assert c._valid_value_cache == {}


def test_any_error_raises_not_empty():
    c = _client(AsyncMock(side_effect=ConnectionError("down")))
    with pytest.raises(ConnectionError):
        asyncio.run(c._async_get_valid_metadata_values("status"))


def test_egeria_answering_with_none_is_still_empty_and_cached():
    c = _client(AsyncMock(return_value=_resp([])))
    assert asyncio.run(c._async_get_valid_metadata_values("status")) == []
    assert c._valid_value_cache == {"status:None": []}


def test_values_are_returned_and_cached():
    c = _client(AsyncMock(return_value=_resp([{"preferredValue": "ACTIVE"}])))
    assert asyncio.run(c._async_get_valid_metadata_values("status")) == [{"preferredValue": "ACTIVE"}]
    c._async_make_request = AsyncMock(side_effect=AssertionError("must come from the cache"))
    assert asyncio.run(c._async_get_valid_metadata_values("status")) == [{"preferredValue": "ACTIVE"}]


# ── the template generator now writes the marker for a failure, and nothing for a real "none" ──
def _generator(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # the module adds a log file named debug_log in the working directory on import
    return importlib.import_module("commands.tech.generate_md_cmd_templates")


class _RealClientFailing:
    """A real ServerClient lookup path: get_valid_metadata_values runs the async method, whose request fails."""
    def __init__(self, request):
        self._c = _client(request)

    def get_valid_metadata_values(self, prop_name, type_name=None):
        return asyncio.run(self._c._async_get_valid_metadata_values(prop_name, type_name))


def test_the_template_generator_says_the_lookup_failed(monkeypatch, tmp_path):
    gen = _generator(monkeypatch, tmp_path)
    client = _RealClientFailing(AsyncMock(side_effect=ConnectionError("down")))
    values, default = gen._resolve_valid_values({"property_name": "status"}, client)
    assert values == "valid values not read (Egeria lookup failed: ConnectionError)" and default is None


def test_the_template_generator_says_nothing_when_egeria_holds_none(monkeypatch, tmp_path):
    gen = _generator(monkeypatch, tmp_path)
    client = _RealClientFailing(AsyncMock(return_value=_resp([])))
    assert gen._resolve_valid_values({"property_name": "status"}, client) == ("", None)


def test_the_template_generator_writes_the_server_values(monkeypatch, tmp_path):
    gen = _generator(monkeypatch, tmp_path)
    client = _RealClientFailing(AsyncMock(return_value=_resp([{"preferredValue": "ACTIVE"}, {"preferredValue": "DELETED"}])))
    values, _ = gen._resolve_valid_values({"property_name": "status"}, client)
    assert "ACTIVE" in values and "DELETED" in values


# ── the Dr.Egeria help generator ──
def _help_value(monkeypatch, tmp_path, client):
    monkeypatch.chdir(tmp_path)
    helpgen = importlib.import_module("commands.tech.generate_dr_help")
    attrs = [{"name": "Status", "property_name": "status", "input_required": "No"}]
    monkeypatch.setattr(helpgen, "get_command_spec", lambda command: {"verb": "Classify", "Attributes": attrs})
    rows = helpgen._extract_help_fields("Classify Anything", client)
    return rows[0]["Valid Values"]


def test_the_help_generator_says_a_failed_lookup_was_not_read(monkeypatch, tmp_path):
    failing = MagicMock()
    failing.get_valid_metadata_values.side_effect = ConnectionError("down")
    assert _help_value(monkeypatch, tmp_path, failing) == "valid values not read (Egeria lookup failed: ConnectionError)"


def test_the_help_generator_says_no_connection_was_not_read(monkeypatch, tmp_path):
    assert _help_value(monkeypatch, tmp_path, None) == "valid values not read (no Egeria connection)"


def test_the_help_generator_writes_the_server_values_and_nothing_for_none(monkeypatch, tmp_path):
    ok = MagicMock()
    ok.get_valid_metadata_values.return_value = [{"preferredValue": "ACTIVE"}, {"preferredValue": "DELETED"}]
    assert _help_value(monkeypatch, tmp_path, ok) == "ACTIVE; DELETED"
    none = MagicMock()
    none.get_valid_metadata_values.return_value = []
    assert _help_value(monkeypatch, tmp_path, none) in ("", [], None)
