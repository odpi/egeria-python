# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression test for ISSUE-151 (PYEGERIA_ISSUES.md): `get_engine_actions` posted
to `automated-curation/engine-actions`, which the View Server does not have
(404). It was removed; `find_engine_actions("*")` is the list-all, and
`print_engine_actions` now uses it.

No live server needed: a mocked `_async_make_request` captures the URL.
"""
import json
from unittest.mock import MagicMock, patch

from pyegeria.omvs.automated_curation import AutomatedCuration


def _client():
    with patch("pyegeria.core._base_server_client.BaseServerClient.check_connection", return_value=""):
        return AutomatedCuration(view_server="vs", platform_url="https://localhost:9443",
                                 user_id="u", user_pwd="p")


def test_get_engine_actions_is_removed():
    client = _client()
    assert not hasattr(client, "get_engine_actions")
    assert not hasattr(client, "_async_get_engine_actions")


def test_print_engine_actions_uses_asset_search():
    client = _client()
    cap = {}

    async def fake(method, url, body=None, **kwargs):
        cap["url"] = url
        cap["body"] = json.loads(body) if isinstance(body, str) else (body or {})
        resp = MagicMock()
        resp.json = MagicMock(return_value={"elements": []})
        return resp

    client._async_make_request = fake
    client.print_engine_actions()

    assert cap["url"].endswith("/automated-curation/assets/by-search-string")
    assert not cap["url"].endswith("/engine-actions")
    assert cap["body"].get("metadataElementTypeName") == "EngineAction"
