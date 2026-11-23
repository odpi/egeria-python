"""PY-71: find_digital_product_catalogs sent no type filter, so it listed every Collection (a live find("*")
returned 5 Agreements and no DigitalProductCatalog), and neither it nor the by-name helper had an output generator."""
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

from pyegeria.omvs.product_manager import ProductManager


def _lenient(self, name):
    if name.startswith("__"):
        raise AttributeError(name)
    return "http://x"


def _client(elements):
    klass = type("ProductManager", (ProductManager,), {"__getattr__": _lenient})
    obj = klass.__new__(klass)
    resp = MagicMock()
    resp.json.return_value = {"elements": elements}
    obj._async_make_request = AsyncMock(return_value=resp)
    obj._async_refresh_report_spec = AsyncMock(return_value=None)
    return obj


def _catalog(n=1):   # synthetic values on the Collection element key set
    return {"class": "OpenMetadataRootElement",
            "elementHeader": {"guid": f"00000000-0000-0000-0000-00000000000{n}",
                              "type": {"typeName": "DigitalProductCatalog"},
                              "origin": {"homeMetadataCollectionId": "00000000-0000-0000-0000-0000000000aa",
                                         "homeMetadataCollectionName": "Synthetic repository",
                                         "originCategory": "LOCAL_COHORT"},
                              "versions": {"createdBy": "synthetic-user", "createTime": "2026-01-01T00:00:00.000+00:00",
                                           "version": 1},
                              "status": "ACTIVE",
                              "classifications": [{"classificationName": "DigitalProductCatalog",
                                                   "classificationProperties": {}}]},
            "properties": {"class": "CollectionProperties", "qualifiedName": f"DigitalProductCatalog::Synthetic {n}",
                           "displayName": f"Synthetic catalog {n}", "description": "A synthetic catalog."},
            "mermaidGraph": "graph LR", "memberOfCollections": []}


def _body(obj):
    call = obj._async_make_request.call_args
    return json.loads(call.args[2])


def test_the_find_request_carries_the_digital_product_catalog_type_filter():
    obj = _client([])
    asyncio.run(obj._async_find_digital_product_catalogs("*"))
    assert _body(obj)["metadataElementSubtypeNames"] == ["DigitalProductCatalog"]


def test_a_callers_subtypes_replace_the_default():
    obj = _client([])
    asyncio.run(obj._async_find_digital_product_catalogs("*", metadata_element_subtypes=["Other"]))
    assert _body(obj)["metadataElementSubtypeNames"] == ["Other"]


def test_the_sibling_digital_product_find_still_filters_digital_products():
    obj = _client([])
    asyncio.run(obj._async_find_digital_products("*"))
    assert _body(obj)["metadataElementSubtypeNames"] == ["DigitalProduct"]


def test_a_catalog_element_formats_from_the_find():
    obj = _client([_catalog(1), _catalog(2)])
    out = asyncio.run(obj._async_find_digital_product_catalogs("*", output_format="DICT"))
    assert isinstance(out, list) and len(out) == 2
    assert {row.get("guid") or row.get("GUID") for row in out} == {"00000000-0000-0000-0000-000000000001",
                                                                    "00000000-0000-0000-0000-000000000002"}


def test_a_catalog_element_formats_from_the_by_name_helper():
    obj = _client([_catalog(1)])
    out = asyncio.run(obj._async_get_digital_product_catalogs_by_name("Synthetic catalog 1", output_format="DICT"))
    assert isinstance(out, list) and len(out) == 1
    assert (out[0].get("guid") or out[0].get("GUID")) == "00000000-0000-0000-0000-000000000001"


def test_json_output_is_still_the_raw_elements():
    els = [_catalog(1)]
    obj = _client(els)
    assert asyncio.run(obj._async_find_digital_product_catalogs("*")) == els
