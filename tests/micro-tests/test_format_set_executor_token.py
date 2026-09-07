"""ISSUE-86: `exec_report_spec(..., token=...)` must authenticate the client it
builds with `set_bearer_token(token)` instead of minting one from
user/user_pass, on BOTH client-building paths (the format-row/find path and
the analytic_function path). With no token, behaviour is unchanged
(`create_egeria_bearer_token()`)."""
import pytest

from pyegeria.view import format_set_executor as fse
from pyegeria.core import mcp_adapter


class _RecordingClient:
    """Stands in for any OMVS client class the executor instantiates."""
    instances: list = []

    def __init__(self, view_server, view_url, user_id=None, user_pwd=None, **kw):
        self.view_server = view_server
        self.platform_url = view_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.token = None
        self.calls: list[str] = []
        _RecordingClient.instances.append(self)

    def create_egeria_bearer_token(self, *a, **kw):
        self.calls.append("create")
        self.token = "minted"
        return self.token

    def set_bearer_token(self, token):
        self.calls.append("set")
        self.token = token

    def find_things(self, **kwargs):
        return [{"guid": "1", "displayName": "x"}]


@pytest.fixture(autouse=True)
def _reset_instances():
    _RecordingClient.instances = []
    yield
    _RecordingClient.instances = []


_FIND_FMT = {
    "action": {
        "function": "Fake.find_things",
        "required_params": [],
        "optional_params": [],
        "spec_params": {},
    },
    "target_type": "Referenceable",
}

_ANALYTIC_FMT = {
    "action": {"analytic_function": "fake.analytic", "analytic_spec_params": {}},
    "target_type": "Referenceable",
}


def _patch_find_path(monkeypatch):
    monkeypatch.setattr(fse, "select_report_spec", lambda name, out: _FIND_FMT)
    monkeypatch.setattr(fse, "get_report_registry", lambda: {})
    monkeypatch.setattr(fse, "_resolve_client_and_method",
                        lambda decl: (_RecordingClient, "find_things"))


def _patch_analytic_path(monkeypatch):
    def _analytic(client):
        return {"count": 3, "token_seen": client.token}
    monkeypatch.setattr(fse, "select_report_spec", lambda name, out: _ANALYTIC_FMT)
    monkeypatch.setattr(fse, "get_report_registry", lambda: {})
    monkeypatch.setattr(fse, "_resolve_analytic_function", lambda decl: _analytic)
    monkeypatch.setattr(fse, "EgeriaTech", _RecordingClient)


# --- format-row (find_method) path -------------------------------------------

def test_find_path_with_token_uses_set_bearer_token(monkeypatch):
    _patch_find_path(monkeypatch)
    result = fse.exec_report_spec(
        "Anything", output_format="DICT", view_server="vs", view_url="https://x",
        user="svc", user_pass="svc-pw", token="user-token",
    )
    assert result["kind"] == "json"
    (client,) = _RecordingClient.instances
    assert client.calls == ["set"]
    assert client.token == "user-token"


def test_find_path_without_token_mints_bearer_token(monkeypatch):
    _patch_find_path(monkeypatch)
    result = fse.exec_report_spec(
        "Anything", output_format="DICT", view_server="vs", view_url="https://x",
        user="svc", user_pass="svc-pw",
    )
    assert result["kind"] == "json"
    (client,) = _RecordingClient.instances
    assert client.calls == ["create"]
    assert client.user_id == "svc" and client.user_pwd == "svc-pw"


# --- analytic_function path ---------------------------------------------------

def test_analytic_path_with_token_uses_set_bearer_token(monkeypatch):
    _patch_analytic_path(monkeypatch)
    result = fse.exec_report_spec(
        "Anything", output_format="DICT", view_server="vs", view_url="https://x",
        user="svc", user_pass="svc-pw", token="user-token",
    )
    assert result == {"kind": "json", "data": {"count": 3, "token_seen": "user-token"}}
    (client,) = _RecordingClient.instances
    assert client.calls == ["set"]


def test_analytic_path_without_token_mints_bearer_token(monkeypatch):
    _patch_analytic_path(monkeypatch)
    result = fse.exec_report_spec(
        "Anything", output_format="DICT", view_server="vs", view_url="https://x",
        user="svc", user_pass="svc-pw",
    )
    assert result["data"]["token_seen"] == "minted"
    (client,) = _RecordingClient.instances
    assert client.calls == ["create"]


def test_chart_path_threads_token(monkeypatch):
    """SERIES/BAR/PIE dispatch to _exec_analytic_chart before the Format-row
    lookup -- the token must survive that hop too."""
    _patch_analytic_path(monkeypatch)
    monkeypatch.setattr(fse, "get_report_spec_heading", lambda name: "H", raising=False)
    fse.exec_report_spec(
        "Anything", output_format="BAR", view_server="vs", view_url="https://x",
        user="svc", user_pass="svc-pw", token="user-token",
    )
    (client,) = _RecordingClient.instances
    assert client.calls == ["set"]
    assert client.token == "user-token"


# --- MCP adapter passthrough --------------------------------------------------

def test_mcp_run_report_forwards_token(monkeypatch):
    seen = {}

    def _fake_exec(**kwargs):
        seen.update(kwargs)
        return {"kind": "empty"}

    monkeypatch.setattr(mcp_adapter, "exec_report_spec", _fake_exec)
    mcp_adapter.run_report(report="R", user="u", user_pass="p", token="tok")
    assert seen["token"] == "tok"
    assert seen["user"] == "u" and seen["user_pass"] == "p"


def test_mcp_run_report_default_token_is_none(monkeypatch):
    seen = {}
    monkeypatch.setattr(mcp_adapter, "exec_report_spec",
                        lambda **kw: seen.update(kw) or {"kind": "empty"})
    mcp_adapter.run_report(report="R", user="u", user_pass="p")
    assert seen["token"] is None
