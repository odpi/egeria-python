"""PY-44: get_relationships_with_property_value sent openMetadataType in a FindPropertyNamesProperties body.
FindPropertyNamesProperties inherits GetOptions.metadataElementTypeName and reads nothing called
openMetadataType (Egeria ignores unknown keys silently), so the relationship type was never applied.
The test captures the body actually sent. No live server."""
import json

from pyegeria.core._server_client import ServerClient


class _Response:
    status_code = 200

    def json(self):
        return {"class": "RelationshipsResponse", "relationships": [], "relatedHTTPCode": 200}


def _client(monkeypatch, calls):
    monkeypatch.setattr(ServerClient, "check_connection", lambda self: "test")
    client = ServerClient("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append({"url": url, "body": json.loads(payload) if isinstance(payload, str) else payload})
        return _Response()

    client._async_make_request = fake_make_request
    return client


def test_the_relationship_type_is_sent_as_metadataElementTypeName(monkeypatch):
    calls: list = []
    _client(monkeypatch, calls).get_relationships_with_property_value("SemanticAssignment", "v", ["name"])
    body = calls[-1]["body"]
    assert body["class"] == "FindPropertyNamesProperties"
    assert body["metadataElementTypeName"] == "SemanticAssignment"
    assert "openMetadataType" not in body
    assert body["propertyValue"] == "v" and body["propertyNames"] == ["name"]


def test_the_type_key_is_one_the_properties_class_reads():
    from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS

    assert "metadataElementTypeName" in PROPERTIES_CLASS_FIELDS["FindPropertyNamesProperties"][1]
    assert "openMetadataType" not in PROPERTIES_CLASS_FIELDS["FindPropertyNamesProperties"][1]
