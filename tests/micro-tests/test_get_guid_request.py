# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Unit tests for ServerClient._async_get_guid_request's response-key fallback
(ISSUE-42 / PY-22, PYEGERIA_ISSUES.md).

No live server: `_async_make_request` is mocked to return each of the three
response shapes this helper needs to handle. `_async_get_guid_request` is
shared by 40+ callers across the OMVS classes; most endpoints return a
singular "element"/"elementGraph" (an element-graph response), but at least
one -- ProjectManager.get_linked_projects's .../projects endpoint -- returns
a genuine list under the plural "elements" key. Before this fix, that third
shape was never checked, so get_linked_projects always returned
NO_ELEMENTS_FOUND even when the server's raw response body had real data.
"""
from unittest.mock import MagicMock, patch

from pyegeria.omvs.project_manager import ProjectManager


def _client():
    # BaseServerClient.__init__ does its own live connectivity probe
    # (check_connection()) before any mock can be installed, so
    # check_connection is patched out for the duration of client
    # construction -- otherwise this file would silently depend on a
    # reachable Egeria platform despite living in tests/micro-tests/.
    with patch("pyegeria.core._base_server_client.BaseServerClient.check_connection", return_value=""):
        return ProjectManager(view_server="vs", platform_url="https://localhost:9443",
                               user_id="u", user_pwd="p")


def _mock_request(payload):
    async def fake(method, url, body=None, **kwargs):
        resp = MagicMock()
        resp.json = MagicMock(return_value=payload)
        return resp
    return fake


async def test_get_linked_projects_parses_plural_elements_key():
    """The bug: the real Egeria response for this endpoint uses "elements"
    (plural, a list), which the helper never checked before this fix."""
    pm = _client()
    pm._async_make_request = _mock_request({
        "class": "OpenMetadataRootElementsResponse", "relatedHTTPCode": 200,
        "elements": [{"class": "OpenMetadataRootElement", "elementHeader": {"guid": "child-1"}},
                     {"class": "OpenMetadataRootElement", "elementHeader": {"guid": "child-2"}}],
    })
    result = await pm._async_get_linked_projects("parent-guid")
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["elementHeader"]["guid"] == "child-1"


async def test_get_guid_request_still_prefers_singular_element_key():
    """Existing callers whose endpoint returns "element" (singular) must be
    unaffected -- this key is checked first, so the new "elements" fallback
    is never reached for them."""
    pm = _client()
    pm._async_make_request = _mock_request({
        "class": "OpenMetadataRootElementResponse", "relatedHTTPCode": 200,
        "element": {"class": "OpenMetadataRootElement", "elementHeader": {"guid": "single"}},
    })
    result = await pm._async_get_linked_projects("parent-guid")
    assert result["elementHeader"]["guid"] == "single"


async def test_get_guid_request_still_falls_back_to_element_graph():
    pm = _client()
    pm._async_make_request = _mock_request({
        "class": "OpenMetadataRootElementGraphResponse", "relatedHTTPCode": 200,
        "elementGraph": {"class": "OpenMetadataRootElementGraph", "elementHeader": {"guid": "graph"}},
    })
    result = await pm._async_get_linked_projects("parent-guid")
    assert result["elementHeader"]["guid"] == "graph"


async def test_get_guid_request_returns_no_elements_found_when_none_present():
    """None of the three keys present -> still degrades to NO_ELEMENTS_FOUND,
    not an exception -- same as before this fix."""
    from pyegeria.core._globals import NO_ELEMENTS_FOUND
    pm = _client()
    pm._async_make_request = _mock_request({"class": "VoidResponse", "relatedHTTPCode": 200})
    result = await pm._async_get_linked_projects("parent-guid")
    assert result == NO_ELEMENTS_FOUND
