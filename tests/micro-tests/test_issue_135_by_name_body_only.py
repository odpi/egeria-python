"""
ISSUE-135: 14 *_by_name wrappers required their first argument (`name` or `filter_string`) even though
they accept `body`, so a body-only call raised TypeError. The first argument now defaults to None in
both the async and sync versions; name-only and name+body calls are unchanged.
"""
import inspect
import json

import pytest

from pyegeria.omvs.actor_manager import ActorManager
from pyegeria.omvs.asset_maker import AssetMaker
from pyegeria.omvs.connection_maker import ConnectionMaker
from pyegeria.omvs.data_designer import DataDesigner
from pyegeria.omvs.product_manager import ProductManager
from pyegeria.omvs.schema_maker import SchemaMaker
from pyegeria.omvs.solution_architect import SolutionArchitect

WRAPPERS = [
    (ActorManager, "get_actor_profiles_by_name"),
    (ActorManager, "get_actor_roles_by_name"),
    (AssetMaker, "get_assets_by_name"),
    (AssetMaker, "get_software_capabilities_by_name"),
    (ConnectionMaker, "get_connections_by_name"),
    (ConnectionMaker, "get_connector_types_by_name"),
    (ConnectionMaker, "get_endpoints_by_name"),
    (DataDesigner, "get_data_fields_by_name"),
    (DataDesigner, "get_data_value_specifications_by_name"),
    # DataDiscovery.get_analysis_reports_by_name now delegates (deprecated) to
    # AssetMaker.get_assets_by_name, which is listed; see test_issue165_replacements.py.
    (ProductManager, "get_governance_action_processes_by_name"),
    (SchemaMaker, "get_schema_types_by_name"),
    (SchemaMaker, "get_schema_attributes_by_name"),
    (SolutionArchitect, "get_concept_model_elements_by_name"),
]


class _Response:
    def json(self):
        return {"relatedHTTPCode": 200, "elements": []}


def _capture(cls, monkeypatch):
    monkeypatch.setattr(cls, "check_connection", lambda self: "test")
    client = cls("view-server", "https://localhost:1", "user", "pwd")
    calls: list = []

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append(json.loads(payload) if isinstance(payload, str) else payload)
        return _Response()

    client._async_make_request = fake_make_request
    return client, calls


@pytest.mark.parametrize("cls, method", WRAPPERS)
def test_first_argument_is_optional_in_both_versions(cls, method):
    for name in (method, f"_async_{method}"):
        params = list(inspect.signature(getattr(cls, name)).parameters.values())[1:]
        assert params[0].default is None, f"{cls.__name__}.{name}({params[0].name}) still required"


@pytest.mark.asyncio
@pytest.mark.parametrize("cls, method", WRAPPERS)
async def test_body_only_call_sends_the_body(cls, method, monkeypatch):
    client, calls = _capture(cls, monkeypatch)

    await getattr(client, f"_async_{method}")(body={"class": "FilterRequestBody", "filter": "Probe"})

    assert calls[0]["filter"] == "Probe"


@pytest.mark.asyncio
@pytest.mark.parametrize("cls, method", WRAPPERS)
async def test_name_only_call_is_unchanged(cls, method, monkeypatch):
    client, calls = _capture(cls, monkeypatch)

    await getattr(client, f"_async_{method}")("Erin")

    assert calls[0]["filter"] == "Erin"


# --- Wrappers that already defaulted `name` but mishandled a body-only call -----------------

from pyegeria.omvs.automated_curation import AutomatedCuration

SA_WRAPPERS = [
    "_async_get_info_supply_chain_by_name",
    "_async_get_solution_blueprints_by_name",
    "_async_get_solution_components_by_name",
    "_async_get_solution_roles_by_name",
]


def _capture_with_url(cls, monkeypatch):
    monkeypatch.setattr(cls, "check_connection", lambda self: "test")
    client = cls("view-server", "https://localhost:1", "user", "pwd")
    calls: list = []

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append({"url": url, "body": json.loads(payload) if isinstance(payload, str) else payload})
        return _Response()

    client._async_make_request = fake_make_request
    return client, calls


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SA_WRAPPERS)
async def test_solution_architect_body_only_keeps_the_filter_and_the_callers_dict(method, monkeypatch):
    client, calls = _capture_with_url(SolutionArchitect, monkeypatch)
    body = {"class": "FilterRequestBody", "filter": "Probe"}

    await getattr(client, method)(body=body)

    assert calls[0]["body"]["filter"] == "Probe"
    assert body == {"class": "FilterRequestBody", "filter": "Probe"}  # not mutated


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SA_WRAPPERS)
async def test_solution_architect_name_still_sets_the_filter(method, monkeypatch):
    client, calls = _capture_with_url(SolutionArchitect, monkeypatch)

    await getattr(client, method)("Erin", body={"class": "FilterRequestBody", "filter": "Probe"})

    assert calls[0]["body"]["filter"] == "Erin"


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SA_WRAPPERS)
async def test_solution_architect_paging_goes_in_the_body(method, monkeypatch):
    """Egeria's SolutionArchitectResource/ActorManagerResource read paging from the body only."""
    client, calls = _capture_with_url(SolutionArchitect, monkeypatch)

    await getattr(client, method)("Erin", start_from=5, page_size=7)

    assert calls[0]["body"]["startFrom"] == 5 and calls[0]["body"]["pageSize"] == 7
    assert "startFrom" not in calls[0]["url"] and "pageSize" not in calls[0]["url"]


@pytest.mark.asyncio
@pytest.mark.parametrize("method", SA_WRAPPERS)
async def test_solution_architect_body_paging_is_not_overridden(method, monkeypatch):
    client, calls = _capture_with_url(SolutionArchitect, monkeypatch)

    await getattr(client, method)(body={"class": "FilterRequestBody", "filter": "P", "pageSize": 3})

    assert calls[0]["body"]["pageSize"] == 3


@pytest.mark.asyncio
async def test_engine_actions_by_name_accepts_a_body_only_call(monkeypatch):
    client, calls = _capture_with_url(AutomatedCuration, monkeypatch)

    await client._async_get_engine_actions_by_name(body={"class": "FilterRequestBody", "filter": "Probe"})

    assert calls[0]["body"]["filter"] == "Probe"


@pytest.mark.asyncio
async def test_engine_actions_by_name_sends_its_type_filter(monkeypatch):
    client, calls = _capture_with_url(AutomatedCuration, monkeypatch)

    await client._async_get_engine_actions_by_name("Erin")

    assert calls[0]["body"]["metadataElementTypeName"] == "EngineAction"
