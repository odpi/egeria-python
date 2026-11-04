# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Unit tests for configurable TLS verification of the Egeria platform's
certificate: pyegeria.core._globals.enable_ssl_check / ssl_verify, driven by
PYEGERIA_SSL_VERIFY / PYEGERIA_CA_BUNDLE (or "Pyegeria SSL Verify" /
"Pyegeria CA Bundle" in config.json).

Uses the same reset-then-reload pattern as test_globals_max_paging_size.py.
"""
import importlib
import os
import ssl

import certifi
import pytest

import pyegeria.core.config as config_module
import pyegeria.core._globals as globals_module
from pyegeria.core._globals import resolve_ssl_verify

_ENV_VARS = ("PYEGERIA_SSL_VERIFY", "PYEGERIA_CA_BUNDLE")


@pytest.fixture
def clean_ssl_env():
    saved = {k: os.environ.pop(k, None) for k in _ENV_VARS}
    config_module._app_config = None
    yield
    for k in _ENV_VARS:
        os.environ.pop(k, None)
        if saved[k] is not None:
            os.environ[k] = saved[k]
    config_module._app_config = None
    importlib.reload(globals_module)


def _reload():
    config_module._app_config = None
    importlib.reload(globals_module)


# --- resolve_ssl_verify -------------------------------------------------------

def test_resolve_off_is_false_even_with_bundle():
    assert resolve_ssl_verify(False) is False
    assert resolve_ssl_verify(False, "/no/such/file.pem") is False


def test_resolve_on_without_bundle_uses_httpx_default():
    assert resolve_ssl_verify(True) is True
    assert resolve_ssl_verify(True, "") is True


def test_resolve_on_with_bundle_builds_context():
    ctx = resolve_ssl_verify(True, certifi.where())
    assert isinstance(ctx, ssl.SSLContext)
    assert ctx.verify_mode == ssl.CERT_REQUIRED
    assert ctx.check_hostname is True


def test_resolve_missing_bundle_raises_rather_than_falling_back():
    with pytest.raises(FileNotFoundError, match="PYEGERIA_CA_BUNDLE"):
        resolve_ssl_verify(True, "/no/such/ca-bundle.pem")


# --- configuration wiring -----------------------------------------------------

def test_default_is_off(clean_ssl_env):
    _reload()
    assert globals_module.enable_ssl_check is False
    assert globals_module.ssl_verify is False


@pytest.mark.parametrize("value", ["true", "1", "yes", "on"])
def test_env_var_turns_verification_on(clean_ssl_env, value):
    os.environ["PYEGERIA_SSL_VERIFY"] = value
    _reload()
    assert globals_module.enable_ssl_check is True
    assert globals_module.ssl_verify is True


def test_env_var_with_ca_bundle(clean_ssl_env):
    os.environ["PYEGERIA_SSL_VERIFY"] = "true"
    os.environ["PYEGERIA_CA_BUNDLE"] = certifi.where()
    _reload()
    assert globals_module.enable_ssl_check is True
    assert isinstance(globals_module.ssl_verify, ssl.SSLContext)


def test_env_var_false_overrides_config_json(clean_ssl_env, monkeypatch, tmp_path):
    cfg = tmp_path / "config.json"
    cfg.write_text('{"Environment": {"Pyegeria SSL Verify": true}}')
    monkeypatch.setenv("PYEGERIA_CONFIG_DIRECTORY", str(tmp_path))
    monkeypatch.setenv("PYEGERIA_CONFIG_FILE", "config.json")
    _reload()
    assert globals_module.enable_ssl_check is True  # from config.json

    os.environ["PYEGERIA_SSL_VERIFY"] = "false"
    _reload()
    assert globals_module.enable_ssl_check is False  # env wins


def test_clients_pass_ssl_verify_to_httpx(clean_ssl_env, monkeypatch):
    # The session reads _globals.ssl_verify when it is created, so setting it
    # in code (after import) also takes effect.
    from pyegeria.core._base_server_client import BaseServerClient

    monkeypatch.setattr(BaseServerClient, "check_connection", lambda self: "ok", raising=False)
    sentinel = ssl.create_default_context(cafile=certifi.where())
    monkeypatch.setattr(globals_module, "ssl_verify", sentinel)

    captured = {}
    import pyegeria.core._base_server_client as bsc

    real = bsc.AsyncClient

    def spy(*args, **kwargs):
        captured["verify"] = kwargs.get("verify")
        return real(*args, **kwargs)

    monkeypatch.setattr(bsc, "AsyncClient", spy)
    client = BaseServerClient.__new__(BaseServerClient)
    import threading
    client._thread_local = threading.local()
    client.timeout = 30
    _ = client.session
    assert captured["verify"] is sentinel
