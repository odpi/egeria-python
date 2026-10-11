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
from pyegeria.omvs.data_discovery import DataDiscovery
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
    (DataDiscovery, "get_analysis_reports_by_name"),
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
