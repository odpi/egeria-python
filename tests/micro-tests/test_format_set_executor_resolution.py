import pytest
from typing import Any, cast

from pyegeria.view import format_set_executor as fse
from pyegeria.view.analytic_registry import AnalyticActionSpec


class _WrongClient:
    async def _async_get_elements_by_property_value(self, **kwargs):
        raise AssertionError("Wrong client selected for report action")


class _RightClient:
    def __init__(self):
        self.called = False
        self.last_kwargs = {}

    async def _async_get_elements_by_property_value(self, **kwargs):
        self.called = True
        self.last_kwargs = kwargs
        return [{"guid": "123", "displayName": "ok"}]


class _FakeEgeriaTech:
    def __init__(self):
        self.view_server = "vs"
        self.platform_url = "https://example"
        self.user_id = "u"
        self.user_pwd = "p"
        self.token = "token"
        self._instantiated_clients = {}
        self._subclient_map = {
            "wrong": _WrongClient,
            "right": _RightClient,
        }

    def _get_subclient(self, name):
        if name not in self._instantiated_clients:
            cls = self._subclient_map[name]
            # Lightweight local-only stubs for this unit test.
            if cls is _RightClient:
                self._instantiated_clients[name] = _RightClient()
            else:
                self._instantiated_clients[name] = _WrongClient()
        return self._instantiated_clients[name]

    def get_token(self):
        return self.token

    async def _async_create_egeria_bearer_token(self, user_id=None, password=None, new_password=None):
        self.token = self.token or "token"
        return self.token


@pytest.mark.asyncio
async def test_async_run_report_uses_declared_client_class(monkeypatch):
    fake_client = _FakeEgeriaTech()

    fake_fmt = {
        "action": {
            "function": "ClassificationExplorer.get_elements_by_property_value",
            "required_params": ["property_value"],
            "optional_params": [],
            "spec_params": {"property_names": ["displayName", "qualifiedName"]},
        },
        "target_type": "Referenceable",
    }

    monkeypatch.setattr(fse, "select_report_spec", lambda report_name, out: fake_fmt)
    monkeypatch.setattr(fse, "get_report_registry", lambda: {})
    monkeypatch.setattr(fse, "_resolve_client_and_method", lambda decl: (_RightClient, "_async_get_elements_by_property_value"))

    result = await fse._async_run_report(
        report_name="Referenceable",
        egeria_client=cast(Any, fake_client),
        output_format="DICT",
        params={"property_value": "Sales Forecast"},
    )

    assert result["kind"] == "json"
    assert result["data"][0]["guid"] == "123"
    assert fake_client._get_subclient("right").called is True


@pytest.mark.asyncio
async def test_async_run_report_normalizes_report_filter_aliases(monkeypatch):
    fake_client = _FakeEgeriaTech()

    fake_fmt = {
        "action": {
            "function": "ClassificationExplorer.get_elements_by_property_value",
            "required_params": ["property_value"],
            "optional_params": [
                "metadata_element_type",
                "metadata_element_subtypes",
                "limit_results_by_status",
                "sequencing_order",
                "sequencing_property",
                "anchor_scope_guid",
            ],
            "spec_params": {"property_names": ["displayName", "qualifiedName"]},
        },
        "target_type": "Referenceable",
    }

    monkeypatch.setattr(fse, "select_report_spec", lambda report_name, out: fake_fmt)
    monkeypatch.setattr(fse, "get_report_registry", lambda: {})
    monkeypatch.setattr(fse, "_resolve_client_and_method", lambda decl: (_RightClient, "_async_get_elements_by_property_value"))

    result = await fse._async_run_report(
        report_name="Referenceable",
        egeria_client=cast(Any, fake_client),
        output_format="DICT",
        params={
            "search_string": "Sales Forecast",
            "metadata_element_type_name": "DigitalProduct",
            "metadata_element_subtype_names": ["RootCollection", "CollectionFolder"],
            "limit_result_by_status": ["ACTIVE"],
            "output_sort_order": "PROPERTY_ASCENDING",
            "order_property_name": "displayName",
            "anchor_scope_id": "Collection::SalesForecast::Root::1.0",
            "metadata_element_type": "",
        },
    )

    assert result["kind"] == "json"
    kwargs = fake_client._get_subclient("right").last_kwargs
    assert kwargs["property_value"] == "Sales Forecast"
    assert kwargs["metadata_element_type"] == "DigitalProduct"
    assert kwargs["metadata_element_subtypes"] == ["RootCollection", "CollectionFolder"]
    assert kwargs["limit_results_by_status"] == ["ACTIVE"]
    assert kwargs["sequencing_order"] == "PROPERTY_ASCENDING"
    assert kwargs["sequencing_property"] == "displayName"
    assert kwargs["anchor_scope_guid"] == "Collection::SalesForecast::Root::1.0"


@pytest.mark.asyncio
async def test_async_run_report_coerces_limit_result_status_string_to_list(monkeypatch):
    fake_client = _FakeEgeriaTech()

    fake_fmt = {
        "action": {
            "function": "ClassificationExplorer.get_elements_by_property_value",
            "required_params": ["property_value"],
            "optional_params": ["limit_results_by_status"],
            "spec_params": {"property_names": ["displayName", "qualifiedName"]},
        },
        "target_type": "Referenceable",
    }

    monkeypatch.setattr(fse, "select_report_spec", lambda report_name, out: fake_fmt)
    monkeypatch.setattr(fse, "get_report_registry", lambda: {})
    monkeypatch.setattr(fse, "_resolve_client_and_method", lambda decl: (_RightClient, "_async_get_elements_by_property_value"))

    result = await fse._async_run_report(
        report_name="Referenceable",
        egeria_client=cast(Any, fake_client),
        output_format="DICT",
        params={
            "search_string": "Sales Forecast",
            "limit_result_by_status": "ACTIVE",
        },
    )

    assert result["kind"] == "json"
    kwargs = fake_client._get_subclient("right").last_kwargs
    assert kwargs["limit_results_by_status"] == ["ACTIVE"]


@pytest.mark.asyncio
async def test_async_run_report_coerces_inherited_list_filters_from_strings(monkeypatch):
    fake_client = _FakeEgeriaTech()

    fake_fmt = {
        "action": {
            "function": "ClassificationExplorer.get_elements_by_property_value",
            "required_params": ["property_value"],
            "optional_params": [
                "metadata_element_subtypes",
                "skip_relationships",
                "include_only_relationships",
                "skip_classified_elements",
                "include_only_classified_elements",
                "governance_zone_filter",
            ],
            "spec_params": {"property_names": ["displayName", "qualifiedName"]},
        },
        "target_type": "Referenceable",
    }

    monkeypatch.setattr(fse, "select_report_spec", lambda report_name, out: fake_fmt)
    monkeypatch.setattr(fse, "get_report_registry", lambda: {})
    monkeypatch.setattr(fse, "_resolve_client_and_method", lambda decl: (_RightClient, "_async_get_elements_by_property_value"))

    result = await fse._async_run_report(
        report_name="Referenceable",
        egeria_client=cast(Any, fake_client),
        output_format="DICT",
        params={
            "search_string": "Sales Forecast",
            "metadata_element_subtype_names": "RootCollection, CollectionFolder",
            "skip_relationships": "SemanticAssignment",
            "include_only_relationships": "CollectionMembership,Anchor",
            "skip_classified_elements": "Confidentiality",
            "include_only_classified_elements": "Anchors,SubjectArea",
            "governance_zone_filter": "PersonalZone,BusinessZone",
        },
    )

    assert result["kind"] == "json"
    kwargs = fake_client._get_subclient("right").last_kwargs
    assert kwargs["metadata_element_subtypes"] == ["RootCollection", "CollectionFolder"]
    assert kwargs["skip_relationships"] == ["SemanticAssignment"]
    assert kwargs["include_only_relationships"] == ["CollectionMembership", "Anchor"]
    assert kwargs["skip_classified_elements"] == ["Confidentiality"]
    assert kwargs["include_only_classified_elements"] == ["Anchors", "SubjectArea"]
    assert kwargs["governance_zone_filter"] == ["PersonalZone", "BusinessZone"]


# ── run_analytic_action (BACKLOG.md NEXT-18 -- fetch+analytic action shape) ──
# Fake fetch/analytic functions are monkeypatched onto the real, importable
# overview_metrics module (same pattern test_overview_metrics.py's
# test_metric_trend_snapshot_failure_yields_none_not_raise already uses for
# dotted-path resolution) rather than a local test-module path, since
# "micro-tests" isn't a valid dotted package segment.

def test_run_analytic_action_runs_fetch_then_analytic_with_same_client(monkeypatch):
    import pyegeria.view.overview_metrics as om_module

    def _fetch(mgr, type_map):
        return [{"label": l, "type": t, "count": len(t)} for l, t in type_map]

    def _analytic(by_type, mgr):
        # Asserts the analytic step gets the SAME client instance the fetch
        # step was bound to, not a fresh/re-resolved one -- the whole point
        # of an analytic step being able to itself fetch further data.
        assert mgr == "CLIENT-42"
        return {"total": sum(r["count"] for r in by_type), "byType": by_type}

    monkeypatch.setattr(om_module, "_fetch_for_test", _fetch, raising=False)
    monkeypatch.setattr(om_module, "_analytic_for_test", _analytic, raising=False)

    spec = AnalyticActionSpec(
        fetch="pyegeria.view.overview_metrics._fetch_for_test",
        analytic="pyegeria.view.overview_metrics._analytic_for_test",
    )
    result = fse.run_analytic_action(
        spec, "CLIENT-42", fetch_kwargs={"type_map": [("A", "Alpha"), ("B", "Beta")]},
    )
    assert result == {
        "total": 9,
        "byType": [{"label": "A", "type": "Alpha", "count": 5}, {"label": "B", "type": "Beta", "count": 4}],
    }


def test_run_analytic_action_returns_raw_fetch_when_no_analytic_declared(monkeypatch):
    import pyegeria.view.overview_metrics as om_module

    def _fetch_only(mgr, type_map):
        return [{"label": l, "type": t} for l, t in type_map]

    monkeypatch.setattr(om_module, "_fetch_only_for_test", _fetch_only, raising=False)

    spec = AnalyticActionSpec(fetch="pyegeria.view.overview_metrics._fetch_only_for_test")
    result = fse.run_analytic_action(spec, "CLIENT-42", fetch_kwargs={"type_map": [("A", "Alpha")]})
    assert result == [{"label": "A", "type": "Alpha"}]

