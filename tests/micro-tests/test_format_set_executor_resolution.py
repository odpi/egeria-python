import pytest
from typing import Any, cast

from pyegeria.view import format_set_executor as fse


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


