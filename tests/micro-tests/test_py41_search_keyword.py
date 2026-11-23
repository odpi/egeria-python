"""PY-41: add_search_keyword_to_element sent only `keyword`. Egeria's SearchKeywordProperties reads displayName,
description, typeName and extendedProperties (and drops any other key silently, ignoreUnknown), so the keyword
element was created empty. The keyword is now sent as displayName. Each test captures the body actually sent.
No live server."""
import json

import pytest

from pyegeria.core._server_client import ServerClient
from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS


class _Response:
    status_code = 200

    def json(self):
        return {"class": "GUIDResponse", "guid": "kw-guid", "relatedHTTPCode": 200}


@pytest.fixture
def sent(monkeypatch):
    calls: list = []
    monkeypatch.setattr(ServerClient, "check_connection", lambda self: "test")
    client = ServerClient("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append({"url": url, "body": json.loads(payload) if isinstance(payload, str) else payload})
        return _Response()

    client._async_make_request = fake_make_request
    return client, calls


def test_the_keyword_is_sent_as_displayName(sent):
    client, calls = sent
    assert client.add_search_keyword_to_element("el-guid", "myKeyword") == "kw-guid"
    props = calls[-1]["body"]["properties"]
    assert props["class"] == "SearchKeywordProperties"
    assert props["displayName"] == "myKeyword"
    assert "keyword" not in props
    assert calls[-1]["url"].endswith("/elements/el-guid/search-keywords")


def test_a_description_is_passed_through_when_given(sent):
    client, calls = sent
    client.add_search_keyword_to_element("el-guid", "myKeyword", description="what it finds")
    assert calls[-1]["body"]["properties"]["description"] == "what it finds"


def test_no_description_is_none_sent_never_an_empty_string(sent):
    client, calls = sent
    client.add_search_keyword_to_element("el-guid", "myKeyword")
    assert "description" not in calls[-1]["body"]["properties"]


def test_the_public_call_still_works_the_old_way_positionally_and_by_body(sent):
    client, calls = sent
    client.add_search_keyword_to_element("el-guid", "kw", None)                 # (element_guid, keyword, body)
    assert calls[-1]["body"]["properties"]["displayName"] == "kw"
    body = {"class": "NewAttachmentRequestBody",
            "properties": {"class": "SearchKeywordProperties", "displayName": "own", "description": "d"}}
    client.add_search_keyword_to_element("el-guid", body=body, description="ignored")
    assert calls[-1]["body"]["properties"]["displayName"] == "own"             # a caller's body is sent as given


def test_no_keyword_and_no_body_is_refused(sent):
    client, calls = sent
    with pytest.raises(Exception):
        client.add_search_keyword_to_element("el-guid")
    assert calls == []


def test_every_key_sent_is_one_the_properties_class_reads(sent):
    client, calls = sent
    client.add_search_keyword_to_element("el-guid", "k", description="d")
    props = {k for k in calls[-1]["body"]["properties"] if k != "class"}
    assert props <= set(PROPERTIES_CLASS_FIELDS["SearchKeywordProperties"][1])
