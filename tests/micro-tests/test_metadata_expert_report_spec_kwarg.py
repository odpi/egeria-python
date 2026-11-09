"""MetadataExpert find methods under exec_report_spec.

exec_report_spec always adds `report_spec=<spec name>` to the call. The
MetadataExpert find methods hardcoded `report_spec=None` in their
`_async_find_request(...)` call while also forwarding `**kwargs`, so every
report spec backed by one of them (e.g. `Report-DrE-Basic`, `Dashboards`)
failed with "got multiple values for keyword argument 'report_spec'". These
tests run the real client class with only the HTTP transport faked.
"""
import pytest

import pyegeria.view.format_set_executor as fse
from pyegeria.core._server_client import ServerClient
from pyegeria.omvs.metadata_expert import MetadataExpert
from pyegeria.view.base_report_formats import get_report_registry

_ELEMENT = {
    "elementHeader": {
        "guid": "g1",
        "type": {"typeName": "Referenceable"},
        "origin": {"homeMetadataCollectionId": "mc1", "homeMetadataCollectionName": "mc"},
        "versions": {"createdBy": "u", "createTime": "2026-11-07T00:00:00Z", "version": 1},
        "status": "ACTIVE",
        "class": "ElementHeader",
    },
    "properties": {"qualifiedName": "Referenceable::x", "displayName": "x"},
}


class _FakeResponse:
    def json(self):
        return {"elements": [_ELEMENT]}


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    calls = []

    async def fake_make_request(self, request_type, endpoint, payload=None, *args, **kwargs):
        calls.append((request_type, endpoint, payload))
        return _FakeResponse()

    monkeypatch.setattr(ServerClient, "_async_make_request", fake_make_request)
    monkeypatch.setattr(ServerClient, "create_egeria_bearer_token", lambda self, *a, **k: "token")
    monkeypatch.setattr(ServerClient, "set_bearer_token", lambda self, token: None)
    monkeypatch.setattr(ServerClient, "check_connection", lambda self: "ok", raising=False)
    return calls


def _specs_using(method: str) -> list[str]:
    names = []
    for name, fs in get_report_registry().items():
        action = getattr(fs, "action", None)
        if action is not None and getattr(action, "function", None) == f"MetadataExpert.{method}":
            names.append(name)
    return sorted(names)


_WITH_STRING_SPECS = _specs_using("find_metadata_elements_with_string")


def test_known_failing_spec_is_covered():
    # Reproduced live 2026-11-07 with Report-DrE-Basic. Since 6.2.28 the generic-search specs
    # (Report-DrE-* among them) call ClassificationExplorer; the specs still on this function
    # (e.g. Dashboards) are picked up by the registry scan below.
    assert "Report-DrE-Basic" not in _WITH_STRING_SPECS
    assert "Dashboard-DrE-Basic" in _WITH_STRING_SPECS


@pytest.mark.parametrize("spec_name", _WITH_STRING_SPECS)
def test_exec_report_spec_runs(spec_name, _offline):
    result = fse.exec_report_spec(spec_name, output_format="DICT", params={"search_string": "*"},
                                  view_server="v", view_url="https://x", user="u", user_pass="p")
    assert result["kind"] != "unknown", result
    assert "multiple values" not in str(result)
    assert _offline, "expected one request to Egeria"
    assert _offline[0][1].endswith("/metadata-elements/by-search-string")


@pytest.mark.parametrize("method, args", [
    # an untyped '*' is refused in words since 6.2.28, so give it a type
    ("find_metadata_elements_with_string", {"metadata_element_type": "Report"}),
    ("find_elements_for_anchor", {"guid": "a1"}),
    ("find_elements_in_anchor_domain", {"anchor_domain": "Glossary"}),
    ("find_elements_in_anchor_scope", {"guid": "a1"}),
])
def test_find_methods_accept_report_spec(method, args, _offline):
    client = MetadataExpert("v", "https://x", "u", "p")
    result = getattr(client, method)(search_string="*", output_format="DICT",
                                     report_spec="Referenceable", **args)
    assert isinstance(result, list), result
    # report_spec is a client-side rendering option and must not reach the request body
    assert "report_spec" not in _offline[0][2] and "reportSpec" not in _offline[0][2]
