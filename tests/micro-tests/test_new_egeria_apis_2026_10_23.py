"""
New Egeria APIs from the refreshed .http collections (2026-10-23), checked against
Egeria main 4486d1a7f1 (Spring @RequestBody types, registered properties classes):
  classification-explorer: UsageActivity and MemberPopularityProfile add/update/clear
  metadata-expert:         undo / restore for metadata elements and relationships
  product-catalog:         find digital product catalogs (generic collection find)
No live server: the HTTP call is captured and the verb, URL and body asserted.
"""
import json

import pytest

from pyegeria.omvs.classification_explorer import ClassificationExplorer
from pyegeria.omvs.metadata_expert import MetadataExpert
from pyegeria.omvs.product_catalog import ProductCatalog


class _Response:
    def json(self):
        return {"class": "VoidResponse", "elements": [], "relatedHTTPCode": 200}


def _client(cls, calls, monkeypatch):
    monkeypatch.setattr(cls, "check_connection", lambda self: "test")
    client = cls("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append({"method": method, "url": url,
                      "body": json.loads(payload) if isinstance(payload, str) else payload})
        return _Response()

    client._async_make_request = fake_make_request
    return client


CE = "/servers/view-server/api/open-metadata/classification-explorer"
ME = "/servers/view-server/api/open-metadata/metadata-expert"


@pytest.mark.asyncio
@pytest.mark.parametrize("slug, props_class", [
    ("usage_activity", "UsageActivityProperties"),
    ("member_popularity_profile", "MemberPopularityProfileProperties"),
])
async def test_activity_classification_add_update_clear(monkeypatch, slug, props_class):
    calls: list = []
    client = _client(ClassificationExplorer, calls, monkeypatch)
    seg = slug.replace("_", "-")

    await getattr(client, f"_async_add_{slug}")("el-guid")
    await getattr(client, f"_async_update_{slug}")("el-guid", {
        "class": "UpdateClassificationRequestBody", "mergeUpdate": True,
        "properties": {"class": props_class}})
    await getattr(client, f"_async_clear_{slug}")("el-guid")

    add, update, clear = calls
    assert add["url"].endswith(f"{CE}/elements/el-guid/{seg}")
    assert add["body"]["class"] == "NewClassificationRequestBody"
    assert add["body"]["properties"]["class"] == props_class
    assert update["url"].endswith(f"{CE}/elements/el-guid/{seg}/update")
    assert update["body"]["class"] == "UpdateClassificationRequestBody"
    assert update["body"]["mergeUpdate"] is True
    assert clear["url"].endswith(f"{CE}/elements/el-guid/{seg}/remove")
    assert clear["body"]["class"] == "DeleteClassificationRequestBody"
    assert {c["method"] for c in calls} == {"POST"}


@pytest.mark.asyncio
async def test_usage_activity_counts_reach_the_wire(monkeypatch):
    calls: list = []
    client = _client(ClassificationExplorer, calls, monkeypatch)
    await client._async_add_usage_activity("el-guid", {
        "class": "NewClassificationRequestBody",
        "properties": {"class": "UsageActivityProperties", "explicitGetCount": 3, "findCount": 5}})
    props = calls[0]["body"]["properties"]
    assert props["explicitGetCount"] == 3 and props["findCount"] == 5


@pytest.mark.asyncio
@pytest.mark.parametrize("method, url_tail", [
    ("_async_undo_metadata_element_update", "/metadata-elements/g1/undo"),
    ("_async_restore_metadata_element", "/metadata-elements/g1/restore"),
    ("_async_undo_related_elements_update", "/related-elements/g1/undo"),
    ("_async_restore_related_elements", "/related-elements/g1/restore"),
])
async def test_metadata_expert_undo_and_restore(monkeypatch, method, url_tail):
    calls: list = []
    client = _client(MetadataExpert, calls, monkeypatch)
    await getattr(client, method)("g1")
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith(f"{ME}{url_tail}")
    # Egeria declares MetadataSourceRequestBody for all four
    assert calls[0]["body"]["class"] == "MetadataSourceRequestBody"


@pytest.mark.asyncio
async def test_find_digital_product_catalogs_uses_the_product_catalog_marker(monkeypatch):
    calls: list = []
    client = _client(ProductCatalog, calls, monkeypatch)
    await client._async_find_digital_product_catalogs("Open Metadata Digital Product Catalog")
    await client._async_find_digital_product_catalogs(metadata_element_type_name="DigitalProduct")
    first, second = calls
    assert first["url"].endswith("/api/open-metadata/product-catalog/collections/by-search-string")
    assert first["body"]["class"] == "SearchStringRequestBody"
    assert first["body"]["searchString"] == "Open Metadata Digital Product Catalog"
    assert first["body"]["metadataElementTypeName"] == "DigitalProductCatalog"
    assert second["body"]["metadataElementTypeName"] == "DigitalProduct"
    assert "searchString" not in second["body"]          # "*" means every element of the type


def test_product_catalog_keeps_collection_manager_behaviour_for_inherited_methods(monkeypatch):
    # EgeriaTech resolves a method on whichever sub-client has it; an inherited
    # find_collections on ProductCatalog must still call collection-manager.
    monkeypatch.setattr(ProductCatalog, "check_connection", lambda self: "test")
    pc = ProductCatalog("view-server", "https://localhost:1", "user", "pwd")
    assert pc.collection_command_root.endswith("/api/open-metadata/collection-manager/collections")


@pytest.mark.asyncio
@pytest.mark.parametrize("method, verb, body_class", [
    ("_async_link_subject_area_hierarchy", "attach", "NewRelationshipRequestBody"),
    ("_async_detach_subject_area_hierarchy", "detach", "DeleteRelationshipRequestBody"),
])
async def test_subject_area_hierarchy_uses_egerias_url(monkeypatch, method, verb, body_class):
    # ISSUE-165: the SDK called subject-area/collections/{g}/collection-hierarchies/{g}/..., which
    # Egeria never served; SubjectAreaResource maps subject-areas/{g}/subject-area-hierarchies/{g}/...
    from pyegeria.omvs.subject_area import SubjectArea
    calls: list = []
    client = _client(SubjectArea, calls, monkeypatch)
    await getattr(client, method)("parent-guid", "nested-guid", {"class": body_class})
    assert calls[0]["url"].endswith(
        f"/api/open-metadata/subject-area/subject-areas/parent-guid/subject-area-hierarchies/nested-guid/{verb}")
