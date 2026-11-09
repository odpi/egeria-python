"""exec_report_spec logs a spec refusal at WARNING and any other ValueError at ERROR (6.2.29).

Both are still raised (6.2.28: never a silent None). Offline: the find method's request raises.
"""
from __future__ import annotations

import pytest
from loguru import logger

import pyegeria.view.format_set_executor as fse
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.omvs.asset_catalog import AssetCatalog
from pyegeria.view.format_set_executor import AnalyticFunctionRefused, exec_report_spec
from pyegeria.view.microflow import AllowlistRefusal, CannotRunYet, MicroflowError
from pyegeria.view.role_supply import RoleRefused
from pyegeria.core.request_filters import SearchRefused

pytestmark = pytest.mark.unit


@pytest.fixture
def raising_asset_catalog(monkeypatch):
    """AssetCatalog with no platform, whose request raises the exception the test sets."""
    box = {}

    def _init(self, view_server, platform_url, user_id=None, user_pwd=None, **_):
        self.view_server, self.platform_url, self.user_id = view_server, platform_url, user_id

    async def _request(self, *a, **k):
        raise box["exc"]

    real_resolve = fse._resolve_client_and_method

    def _resolve(decl):
        cls, method = real_resolve(decl)
        return (AssetCatalog, method) if decl == "AssetCatalog.get_asset_graph_by_guid" else (cls, method)

    def _no_egeria_tech(self, *a, **k):
        raise AssertionError("the test would have built a real EgeriaTech client")

    monkeypatch.setattr(fse, "_resolve_client_and_method", _resolve)
    monkeypatch.setattr(EgeriaTech, "__init__", _no_egeria_tech)
    monkeypatch.setattr(AssetCatalog, "__init__", _init)
    monkeypatch.setattr(AssetCatalog, "_async_make_request", _request)
    monkeypatch.setattr(AssetCatalog, "create_egeria_bearer_token", lambda self, *a, **k: "token")
    monkeypatch.setattr(AssetCatalog, "close_session", lambda self: None)
    return box


@pytest.fixture
def log_records():
    records = []
    sink = logger.add(lambda m: records.append((m.record["level"].name, m.record["message"])), level="DEBUG")
    yield records
    logger.remove(sink)


def _run():
    return exec_report_spec("Asset-Graph", output_format="DICT", params={"guid": "g-1"},
                            view_server="qs-view-server", view_url="https://localhost:9443",
                            user="tester", user_pass="unused")


def _failed_lines(records):
    return [(level, msg) for level, msg in records if "Report spec 'Asset-Graph' (DICT) failed:" in msg]


@pytest.mark.parametrize("exc", [
    AllowlistRefusal("stage 0: not on the allowlist"),
    AnalyticFunctionRefused("not a registered name"),
    RoleRefused("Routine 'x' cannot run: no reader."),
    CannotRunYet("producer/join"),
    MicroflowError("not valid JSON"),
    SearchRefused("give a search string or a narrower type"),
], ids=lambda e: type(e).__name__)
def test_a_refusal_logs_at_warning_and_is_raised(raising_asset_catalog, log_records, exc):
    raising_asset_catalog["exc"] = exc
    with pytest.raises(type(exc)):
        _run()
    lines = _failed_lines(log_records)
    assert [level for level, _ in lines] == ["WARNING"]
    assert str(exc) in lines[0][1]


def test_an_unexpected_value_error_still_logs_at_error(raising_asset_catalog, log_records):
    raising_asset_catalog["exc"] = ValueError("something broke")
    with pytest.raises(ValueError, match="something broke"):
        _run()
    assert [level for level, _ in _failed_lines(log_records)] == ["ERROR"]


def test_search_refused_is_a_value_error():
    assert issubclass(SearchRefused, ValueError)


def test_star_on_a_root_type_logs_at_warning_through_exec_report_spec(monkeypatch, log_records):
    """End to end: Element-DrE-Basic searches OpenMetadataRoot; '*' is refused before any request."""
    from pyegeria.omvs.classification_explorer import ClassificationExplorer

    async def _no_request(self, *a, **k):
        raise AssertionError("the refusal should come before any request")

    monkeypatch.setattr(ClassificationExplorer, "_async_make_request", _no_request)
    monkeypatch.setattr(EgeriaTech, "close_session", lambda self: None, raising=False)
    with pytest.raises(ValueError) as exc:
        exec_report_spec("Element-DrE-Basic", output_format="DICT", params={"search_string": "*"},
                         view_server="qs-view-server", view_url="https://localhost:9443",
                         user="tester", user_pass="unused", token="offline-token")
    assert isinstance(exc.value, SearchRefused)
    assert "give a search string or a narrower type" in str(exc.value)
    lines = [(level, msg) for level, msg in log_records if "Report spec 'Element-DrE-Basic' (DICT) failed:" in msg]
    assert [level for level, _ in lines] == ["WARNING"]
