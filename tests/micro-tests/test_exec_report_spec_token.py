"""ISSUE-86: exec_report_spec (and _exec_analytic_chart, _run_analytic_function)
should authenticate with a caller-supplied bearer token via set_bearer_token()
instead of always minting a fresh one via create_egeria_bearer_token() when a
token is available -- e.g. Egeria Advisor, whose session carries the user's
Egeria token and no longer their password.

Unit-level: monkeypatches EgeriaTech inside format_set_executor with a fake
that just records which auth path was taken -- no live server required.
"""
import pytest

from pyegeria.view import format_set_executor as fse


class _FakeEgeriaTech:
    """Records how it was authenticated; raises if create_egeria_bearer_token()
    is called when a token was supplied (that would mean the token path was
    bypassed and a fresh token minted from user/user_pass instead)."""

    def __init__(self, view_server=None, view_url=None, user_id=None, user_pwd=None, **kwargs):
        self.view_server = view_server
        self.view_url = view_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.set_bearer_token_calls = []
        self.create_egeria_bearer_token_calls = 0

    def set_bearer_token(self, token):
        self.set_bearer_token_calls.append(token)

    def create_egeria_bearer_token(self):
        self.create_egeria_bearer_token_calls += 1


@pytest.fixture
def fake_egeria_tech(monkeypatch):
    instances = []

    def factory(*args, **kwargs):
        inst = _FakeEgeriaTech(*args, **kwargs)
        instances.append(inst)
        return inst

    monkeypatch.setattr(fse, "EgeriaTech", factory)
    return instances


def _dummy_analytic_action():
    def _dummy(client):
        return {"count": 1}
    return {"analytic_function": _dummy, "analytic_spec_params": {}}


def test_run_analytic_function_uses_token_when_given(fake_egeria_tech, monkeypatch):
    """When a token is supplied, set_bearer_token(token) is used -- not
    create_egeria_bearer_token()."""
    monkeypatch.setattr(
        fse, "_resolve_analytic_function", lambda decl: decl
    )
    monkeypatch.setattr(
        fse, "_bind_client_args", lambda func, client: (client,)
    )

    action = _dummy_analytic_action()
    result = fse._run_analytic_function(
        action, params={}, view_server="vs", view_url="url",
        user="svc-user", user_pass="svc-pass", token="caller-token-123",
    )

    assert result == {"count": 1}
    assert len(fake_egeria_tech) == 1
    client = fake_egeria_tech[0]
    assert client.set_bearer_token_calls == ["caller-token-123"]
    assert client.create_egeria_bearer_token_calls == 0


def test_run_analytic_function_mints_token_when_none_given(fake_egeria_tech, monkeypatch):
    """Backward compatible: with no token, the old create_egeria_bearer_token()
    path from user/user_pass is used unchanged."""
    monkeypatch.setattr(
        fse, "_resolve_analytic_function", lambda decl: decl
    )
    monkeypatch.setattr(
        fse, "_bind_client_args", lambda func, client: (client,)
    )

    action = _dummy_analytic_action()
    result = fse._run_analytic_function(
        action, params={}, view_server="vs", view_url="url",
        user="svc-user", user_pass="svc-pass",
    )

    assert result == {"count": 1}
    assert len(fake_egeria_tech) == 1
    client = fake_egeria_tech[0]
    assert client.set_bearer_token_calls == []
    assert client.create_egeria_bearer_token_calls == 1
