# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression tests for DeleteElementRequestBody's cascadeDelete/deleteMethod
fields (PYEGERIA_ISSUES.md ISSUE-62).

Before this fix, DeleteElementRequestBody had neither field defined --
PyegeriaModel's extra='ignore' meant a caller-supplied "cascadeDelete"/
"deleteMethod" validated successfully but was silently dropped before
serialization, so every _async_delete_X wrapper threading cascade_delete
through _async_delete_element_request's no-body-provided path had never
actually sent cascadeDelete in the outgoing request body.

No live server needed: model-level round trips plus a mocked
_async_make_request to confirm the actual outgoing JSON body.
BaseServerClient.__init__ does its own live connectivity probe
(check_connection()) before any mock can be installed, so
check_connection is patched out for the duration of client construction
-- otherwise this file would silently depend on a reachable Egeria
platform despite living in tests/micro-tests/.
"""
from unittest.mock import MagicMock, patch

from pyegeria.models.models import DeleteElementRequestBody
from pyegeria.omvs.automated_curation import AutomatedCuration


def _client():
    with patch("pyegeria.core._base_server_client.BaseServerClient.check_connection", return_value=""):
        return AutomatedCuration(view_server="vs", platform_url="https://localhost:9443",
                                  user_id="u", user_pwd="p")


def _mock_request(capture):
    async def fake(method, url, body=None, **kwargs):
        capture["method"] = method
        capture["url"] = url
        capture["body"] = body
        resp = MagicMock()
        resp.json = MagicMock(return_value={})
        return resp
    return fake


def test_cascade_delete_survives_validation_both_spellings():
    b1 = DeleteElementRequestBody.model_validate(
        {"class": "DeleteElementRequestBody", "cascadeDelete": True})
    assert b1.cascade_delete is True

    b2 = DeleteElementRequestBody.model_validate(
        {"class": "DeleteElementRequestBody", "cascadedDelete": True})
    assert b2.cascade_delete is True


def test_delete_method_survives_validation():
    b = DeleteElementRequestBody.model_validate(
        {"class": "DeleteElementRequestBody", "deleteMethod": "PURGE"})
    assert b.delete_method == "PURGE"


def test_cascade_delete_and_delete_method_serialize_with_canonical_names():
    b = DeleteElementRequestBody.model_validate(
        {"class": "DeleteElementRequestBody", "cascadedDelete": True, "deleteMethod": "ARCHIVE"})
    dumped = b.model_dump_json(exclude_none=True)
    assert '"cascadeDelete":true' in dumped
    assert '"deleteMethod":"ARCHIVE"' in dumped
    # confirms the alt spelling never leaks into the outgoing body
    assert "cascadedDelete" not in dumped


async def test_delete_element_request_no_body_path_sends_cascade_delete():
    client = _client()
    cap = {}
    client._async_make_request = _mock_request(cap)

    await client._async_delete_element_request(
        "https://localhost:9443/servers/vs/api/open-metadata/x/y/delete",
        body=None, cascade_delete=True,
    )

    assert cap["body"] is not None
    assert '"cascadeDelete": true' in cap["body"]


async def test_delete_element_request_forwards_caller_dict_body():
    client = _client()
    cap = {}
    client._async_make_request = _mock_request(cap)

    await client._async_delete_element_request(
        "https://localhost:9443/servers/vs/api/open-metadata/x/y/delete",
        body={"class": "DeleteElementRequestBody", "deleteMethod": "SOFT_DELETE"},
    )

    assert cap["body"] is not None
    assert '"deleteMethod": "SOFT_DELETE"' in cap["body"]
