# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression tests for ISSUE-63: MetadataExpert.delete_related_elements()/
delete_metadata_element() were missed when the deleteMethod-dropped-silently
bug was fixed for ~15 other OMVS modules (ISSUE-62's DeleteElementRequestBody
fix, and DeleteRelationshipRequestBody's earlier fix). Both methods used to
route through OpenMetadataDeleteRequestBody/_async_open_metadata_delete_body_
request, which has no deleteMethod field at all -- a caller-supplied
deleteMethod validated successfully and vanished before serialization.

No live server needed: model-level round trips plus mocked _async_make_request
calls confirm the actual outgoing JSON body.
"""
from unittest.mock import MagicMock, patch

from pyegeria.models.models import DeleteElementRequestBody, DeleteRelationshipRequestBody
from pyegeria.omvs.metadata_expert import MetadataExpert


def _client():
    with patch("pyegeria.core._base_server_client.BaseServerClient.check_connection", return_value=""):
        return MetadataExpert(view_server="vs", platform_url="https://localhost:9443",
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


def test_delete_related_elements_uses_delete_relationship_request_body():
    me = _client()
    cap = {}
    me._async_make_request = _mock_request(cap)

    me.delete_related_elements("rel-guid", {"class": "DeleteRelationshipRequestBody", "deleteMethod": "SOFT_DELETE"})

    assert cap["url"].endswith("/related-elements/rel-guid/delete")
    assert '"deleteMethod": "SOFT_DELETE"' in cap["body"]


def test_delete_related_elements_no_body_sends_no_request_body():
    # Matches _async_delete_relationship_request's existing no-body-provided
    # behavior (unchanged by this fix) -- no body means no deleteMethod
    # override, so the server's own default still applies. This is expected;
    # the fix is that an override is now POSSIBLE, not that one is implied.
    me = _client()
    cap = {}
    me._async_make_request = _mock_request(cap)

    me.delete_related_elements("rel-guid")

    assert cap["url"].endswith("/related-elements/rel-guid/delete")
    assert cap["body"] is None


def test_delete_metadata_element_uses_delete_element_request_body():
    me = _client()
    cap = {}
    me._async_make_request = _mock_request(cap)

    me.delete_metadata_element("element-guid", {"class": "DeleteElementRequestBody", "deleteMethod": "PURGE", "cascadeDelete": True})

    assert cap["url"].endswith("/metadata-elements/element-guid/delete")
    assert '"deleteMethod": "PURGE"' in cap["body"]
    assert '"cascadeDelete": true' in cap["body"]


def test_delete_metadata_element_cascade_delete_param_flows_through_no_body():
    me = _client()
    cap = {}
    me._async_make_request = _mock_request(cap)

    me.delete_metadata_element("element-guid", cascade_delete=True)

    assert cap["url"].endswith("/metadata-elements/element-guid/delete")
    assert '"cascadeDelete": true' in cap["body"]


def test_delete_relationship_request_body_still_preserves_delete_method():
    # Direct model round-trip, matching the report's own verification --
    # confirms the sibling fix (already landed) is still intact.
    b = DeleteRelationshipRequestBody.model_validate(
        {"class": "DeleteRelationshipRequestBody", "deleteMethod": "SOFT_DELETE"})
    dumped = b.model_dump(by_alias=True, exclude_none=True)
    assert dumped["deleteMethod"] == "SOFT_DELETE"


def test_delete_element_request_body_still_preserves_delete_method_and_cascade():
    b = DeleteElementRequestBody.model_validate(
        {"class": "DeleteElementRequestBody", "deleteMethod": "PURGE", "cascadeDelete": True})
    dumped = b.model_dump(by_alias=True, exclude_none=True)
    assert dumped["deleteMethod"] == "PURGE"
    assert dumped["cascadeDelete"] is True
