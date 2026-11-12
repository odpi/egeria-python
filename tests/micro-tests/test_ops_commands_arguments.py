"""The ops commands pass the right arguments, and the catalog-target calls do not invent settings (6.2.32).

Argument-level only: the clients are fakes, so nothing reaches Egeria.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from click.testing import CliRunner

import commands.ops.gov_server_actions as gsa
from pyegeria.core._exceptions import PyegeriaInvalidParameterException
from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.omvs.automated_curation import AutomatedCuration
from pyegeria.omvs.runtime_manager import RuntimeManager

pytestmark = pytest.mark.unit

CONFIG = SimpleNamespace(view_server="qs-view-server", view_server_url="https://localhost:9443", userid="u",
                         password="p", engine_host="qs-engine-host")


class _FakeTech:
    calls: list = []

    def __init__(self, *a, **k):
        pass

    def create_egeria_bearer_token(self):
        return "t"

    def close_session(self):
        pass

    def __getattr__(self, name):
        def record(*args, **kwargs):
            _FakeTech.calls.append((name, args, kwargs))
        return record


@pytest.fixture
def fake(monkeypatch):
    _FakeTech.calls = []
    monkeypatch.setattr(gsa, "EgeriaTech", _FakeTech)
    return _FakeTech.calls


def _invoke(command, args):
    return CliRunner().invoke(command, args, obj=CONFIG, catch_exceptions=False)


# ── tell engine-host refresh ──

def test_refresh_by_default_names_the_configured_engine_host(fake):
    r = _invoke(gsa.refresh_gov_eng_config, ["--organization-name", "Coco Pharmaceuticals"])
    assert r.exit_code == 0, r.output
    assert fake == [("refresh_gov_eng_config", (), {
        "gov_engine_name": None, "server_guid": None, "display_name": "qs-engine-host",
        "organization_name": "Coco Pharmaceuticals"})]


def test_refresh_uses_the_engine_host_guid_and_engine_given(fake):
    r = _invoke(gsa.refresh_gov_eng_config, ["--engine-host-guid", "g-1", "--engine", "AssetSurvey"])
    assert r.exit_code == 0, r.output
    name, args, kwargs = fake[0]
    assert kwargs["server_guid"] == "g-1" and kwargs["display_name"] is None
    assert kwargs["gov_engine_name"] == "AssetSurvey"


# ── tell servers start / stop ──

@pytest.mark.parametrize("command, method", [(gsa.start_server, "activate_server_with_stored_config"),
                                             (gsa.stop_server, "shutdown_server")])
def test_start_and_stop_pass_the_server_by_name(fake, command, method):
    r = _invoke(command, ["--server", "qs-engine-host", "--organization-name", "Coco Pharmaceuticals"])
    assert r.exit_code == 0, r.output
    assert fake == [(method, (), {"display_name": "qs-engine-host", "organization_name": "Coco Pharmaceuticals"})]


@pytest.mark.parametrize("command", [gsa.start_server, gsa.stop_server])
def test_start_and_stop_require_a_server(fake, command):
    r = CliRunner().invoke(command, [], obj=CONFIG)
    assert r.exit_code != 0 and "--server" in r.output
    assert fake == []


# ── the RuntimeManager resolves a server by its resourceName, and refuses one it cannot find ──

class _Resolver(RuntimeManager):
    def __init__(self, found):
        self.organization_name = "Coco Pharmaceuticals"
        self.found = found
        self.looked_up = []
        self.requests = []

    def __get_guid__(self, guid, display_name, property_name, qualified_name, tech_type=None,
                     organization_name=None):
        self.looked_up.append((guid, display_name, property_name, qualified_name, organization_name))
        return guid or self.found

    async def _async_make_request(self, method, url, payload=None, **kw):
        self.requests.append((method, url))


@pytest.mark.parametrize("call", [
    lambda rm: rm.activate_server_with_stored_config(display_name="qs-engine-host"),
    lambda rm: rm.shutdown_server(display_name="qs-engine-host"),
    lambda rm: rm.refresh_gov_eng_config(display_name="qs-engine-host"),
], ids=["activate", "shutdown", "refresh"])
def test_server_methods_resolve_the_name_as_a_resource_name(call):
    rm = _Resolver("srv-guid")
    rm.runtime_command_root = "https://x/runtime"
    call(rm)
    assert rm.looked_up[0][1:3] == ("qs-engine-host", "resourceName")
    assert "srv-guid" in rm.requests[0][1]


@pytest.mark.parametrize("call", [
    lambda rm: rm.activate_server_with_stored_config(display_name="no-such-server"),
    lambda rm: rm.shutdown_server(display_name="no-such-server"),
    lambda rm: rm.refresh_gov_eng_config(display_name="no-such-server"),
], ids=["activate", "shutdown", "refresh"])
def test_an_unknown_server_is_refused_before_any_request(call):
    rm = _Resolver(NO_ELEMENTS_FOUND)
    rm.runtime_command_root = "https://x/runtime"
    with pytest.raises(PyegeriaInvalidParameterException):
        call(rm)
    assert rm.requests == []


# ── catalog targets inherit the connector's settings unless told otherwise ──

class _Curation(AutomatedCuration):
    def __init__(self):
        self.ref_curation_command_base = "https://x/curation"
        self.bodies = []

    async def _async_new_relationship_request(self, url, classes, body):
        self.bodies.append(body)
        return "rel-guid"

    async def _async_update_relationship_request(self, url, classes, body):
        self.bodies.append(body)


GUID_A, GUID_B = "11111111-1111-1111-1111-111111111111", "22222222-2222-2222-2222-222222222222"


@pytest.mark.parametrize("call", [
    lambda c: c.add_catalog_target(GUID_A, GUID_B, "target"),
    lambda c: c.update_catalog_target(GUID_A, "target"),
], ids=["add", "update"])
def test_catalog_target_sends_no_sync_or_delete_method_unless_given(call):
    c = _Curation()
    call(c)
    props = c.bodies[0]["properties"]
    assert "permittedSynchronization" not in props and "deleteMethod" not in props
    assert props["catalogTargetName"] == "target"


def test_catalog_target_sends_the_sync_and_delete_method_given():
    c = _Curation()
    c.add_catalog_target(GUID_A, GUID_B, "target", permitted_sync="FROM_THIRD_PARTY", delete_method="SOFT_DELETE")
    props = c.bodies[0]["properties"]
    assert props["permittedSynchronization"] == "FROM_THIRD_PARTY" and props["deleteMethod"] == "SOFT_DELETE"


def test_the_targets_command_is_reachable():
    from commands.cli.egeria_ops import cli
    r = CliRunner().invoke(cli, ["show", "integrations", "--help"])
    assert "targets" in r.output and "--targets" not in r.output
