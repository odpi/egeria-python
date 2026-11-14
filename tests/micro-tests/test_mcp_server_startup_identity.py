# SPDX-License-Identifier: Apache-2.0
"""The MCP server signs in at startup as the CONFIGURED identity, never a hard-coded one (security fix, 2026-11-14).

Until this fix, pyegeria/core/mcp_server.py built its client from the settings' user but then called
create_egeria_bearer_token("<a demo persona>", "<its demo password>"): a credential in released source, and every
MCP server signed in as that one persona whatever it was configured with.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

import pyegeria.core.mcp_server as mcp

SRC = Path(mcp.__file__)


def _settings(user, pwd):
    return SimpleNamespace(
        User_Profile=SimpleNamespace(user_name=user, user_pwd=pwd),
        Environment=SimpleNamespace(egeria_view_server="view-server",
                                    egeria_view_server_url="https://localhost:9443"),
    )


class _FakeClient:
    instances = []

    def __init__(self, server, url, user_id, user_pwd):
        self.args = (server, url, user_id, user_pwd)
        self.token_for = None
        _FakeClient.instances.append(self)

    def create_egeria_bearer_token(self, user_id, user_pwd):
        self.token_for = (user_id, user_pwd)


@pytest.fixture(autouse=True)
def _fake_client(monkeypatch):
    _FakeClient.instances = []
    monkeypatch.setattr(mcp, "EgeriaTech", _FakeClient)


def test_startup_signs_in_as_the_configured_user():
    client = mcp._startup_client(_settings("someone", "their-password"))
    assert client.args[2:] == ("someone", "their-password")
    assert client.token_for == ("someone", "their-password")


@pytest.mark.parametrize("user,pwd", [(None, None), ("", ""), ("someone", ""), ("", "pw"), ("someone", None)])
def test_no_configured_identity_starts_without_egeria_and_says_so(user, pwd, caplog):
    messages = []
    sink = mcp.logger.add(lambda m: messages.append(str(m)), level="WARNING")
    try:
        client = mcp._startup_client(_settings(user, pwd))
    finally:
        mcp.logger.remove(sink)
    assert client is None
    assert not _FakeClient.instances, "no client is built and no sign-in is attempted"
    assert any("no Egeria user or password is configured" in m for m in messages)


def test_no_string_literal_is_passed_to_a_token_call():
    """Every create_egeria_bearer_token call in mcp_server.py passes variables, never string literals."""
    tree = ast.parse(SRC.read_text(encoding="utf-8"))
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            if name in ("create_egeria_bearer_token", "_async_create_egeria_bearer_token"):
                if any(isinstance(a, ast.Constant) and isinstance(a.value, str) for a in node.args):
                    offenders.append(node.lineno)
    assert offenders == [], f"string literal credentials at lines {offenders}"
