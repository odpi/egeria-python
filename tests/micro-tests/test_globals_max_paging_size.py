# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Unit tests for pyegeria.core._globals.max_paging_size (introduced in 18486a9,
"feat(config): make max_paging_size env-configurable").

max_paging_size is read from pyegeria.core.config.settings.Environment at
_globals import time, falling back to a bare 500 if settings can't load yet.
Both the env-var override and the fallback path are exercised here by
resetting the memoized AppConfig and reloading _globals -- same
reset-then-reload pattern test_env_settings.py already uses for
load_app_config() itself.
"""
import importlib
import os

import pyegeria.core.config as config_module
import pyegeria.core._globals as globals_module


def _reset_app_config():
    config_module._app_config = None


def _reload_globals():
    importlib.reload(globals_module)


def test_max_paging_size_default_is_500():
    _reset_app_config()
    os.environ.pop("EGERIA_MAX_PAGE_SIZE", None)
    try:
        _reload_globals()
        assert globals_module.max_paging_size == 500
    finally:
        _reset_app_config()
        _reload_globals()


def test_max_paging_size_honors_env_override():
    _reset_app_config()
    os.environ["EGERIA_MAX_PAGE_SIZE"] = "750"
    try:
        _reload_globals()
        assert globals_module.max_paging_size == 750
    finally:
        os.environ.pop("EGERIA_MAX_PAGE_SIZE", None)
        _reset_app_config()
        _reload_globals()


def test_max_paging_size_falls_back_to_500_when_settings_unavailable(monkeypatch):
    class _BrokenSettings:
        def __getattr__(self, name):
            raise RuntimeError("settings not ready (mid-bootstrap)")

    monkeypatch.setattr(config_module, "settings", _BrokenSettings())
    try:
        _reload_globals()
        assert globals_module.max_paging_size == 500
    finally:
        # monkeypatch restores config_module.settings automatically, but
        # _globals must be reloaded again to pick that restoration up.
        monkeypatch.undo()
        _reset_app_config()
        _reload_globals()


def test_overview_metrics_default_cap_derives_from_max_paging_size():
    # overview_metrics.DEFAULT_CAP is meant to track _globals.max_paging_size
    # as one source of truth, not an independently-hardcoded constant that
    # happens to match today by coincidence (see 18486a9's commit message).
    import pyegeria.view.overview_metrics as om
    importlib.reload(om)
    assert om.DEFAULT_CAP == globals_module.max_paging_size
