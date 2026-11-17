# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Two shapes of the same element, and the conversion from raw to view.

Egeria's view services (classification-explorer, asset-maker, collection-manager, ...) return a **view bean**:

    {"elementHeader": {"guid", "type", "status", "versions", "anchor", "zoneMembership", "memento", ...},
     "properties": {"qualifiedName": ..., "displayName": ..., "additionalProperties": {...}}}

The raw metadata-expert endpoints (`get_metadata_element_by_guid`, `find_metadata_elements`, element history)
return an **OpenMetadataElement**:

    {"elementGUID", "type", "status", "versions", "origin", "headerVersion",
     "classifications": [{"type": {"typeName"}, "classificationProperties": {"propertyValueMap": {...}}}],
     "elementProperties": {"propertyValueMap": {name: {"class": "PrimitiveTypePropertyValue", ...}}}}

Code that reads `properties` or `elementHeader` from a raw element finds nothing and says nothing (a Portal
check never reported "done" this way, 2026-11-13). `as_view_element` converts a raw element to the view shape;
a view bean is returned unchanged.

Classifications go to the named header slots Egeria 6 uses (`anchor` for Anchors, then the classification name
in lowerCamelCase: `memento`, `zoneMembership`, `dataScope`, ...), each `{"classificationName",
"classificationProperties"}`, so a check like `elementHeader.memento` works on either shape.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

_SLOT_NAMES = {"Anchors": "anchor"}
_INT_CATEGORIES = {"OM_PRIMITIVE_TYPE_INT", "OM_PRIMITIVE_TYPE_LONG", "OM_PRIMITIVE_TYPE_SHORT",
                   "OM_PRIMITIVE_TYPE_BYTE", "OM_PRIMITIVE_TYPE_BIGINTEGER", "OM_PRIMITIVE_TYPE_DATE"}
_FLOAT_CATEGORIES = {"OM_PRIMITIVE_TYPE_FLOAT", "OM_PRIMITIVE_TYPE_DOUBLE", "OM_PRIMITIVE_TYPE_BIGDECIMAL"}


def is_raw_element(item: Any) -> bool:
    """True for an OpenMetadataElement (raw metadata-expert shape), False for a view bean or anything else."""
    return isinstance(item, dict) and "elementGUID" in item and "elementHeader" not in item


def property_value(value: Any) -> Any:
    """One raw property value as plain Python: primitives typed by their category, enums by symbolic name,
    maps as dicts, arrays as lists (in index order)."""
    if not isinstance(value, dict):
        return value
    if "primitiveValue" in value:
        raw, category = value["primitiveValue"], value.get("primitiveTypeCategory", "")
        try:
            if category in _INT_CATEGORIES and isinstance(raw, str):
                return int(raw)
            if category in _FLOAT_CATEGORIES and isinstance(raw, str):
                return float(raw)
            if category == "OM_PRIMITIVE_TYPE_BOOLEAN" and isinstance(raw, str):
                return raw.strip().lower() == "true"
        except ValueError:
            return raw
        return raw
    if "symbolicName" in value:
        return value["symbolicName"]
    if "mapValues" in value:
        return property_map((value.get("mapValues") or {}))
    if "arrayValues" in value:
        items = (value.get("arrayValues") or {}).get("propertyValueMap") or {}
        return [property_value(items[k]) for k in sorted(items, key=lambda k: int(k) if str(k).isdigit() else 0)]
    if "attributeValues" in value:   # a struct
        return property_map(value.get("attributeValues") or {})
    return value


def property_map(container: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """`{"propertyValueMap": {...}}` (an elementProperties or classificationProperties) as a flat dict."""
    pvm = (container or {}).get("propertyValueMap") or {}
    return {name: property_value(v) for name, v in pvm.items()}


def _slot(name: str) -> str:
    return _SLOT_NAMES.get(name) or (name[:1].lower() + name[1:])


def as_view_element(item: Any) -> Any:
    """A raw OpenMetadataElement in view-bean shape (`elementHeader` + flat `properties`); anything else
    (a view bean, a "No elements found" string, None) is returned unchanged."""
    if not is_raw_element(item):
        return item
    header: Dict[str, Any] = {"class": "ElementHeader", "guid": item.get("elementGUID")}
    for key in ("type", "status", "versions", "origin", "headerVersion"):
        if key in item:
            header[key] = item[key]
    for c in item.get("classifications") or []:
        if not isinstance(c, dict):
            continue
        name = (c.get("type") or {}).get("typeName") or c.get("classificationName")
        if not name:
            continue
        entry = {"classificationName": name, "classificationProperties": property_map(c.get("classificationProperties")),
                 "status": c.get("status"), "versions": c.get("versions")}
        slot = _slot(name)
        if slot in header and slot not in ("type", "status", "versions", "origin", "guid"):
            existing = header[slot]
            header[slot] = (existing if isinstance(existing, list) else [existing]) + [entry]
        else:
            header[slot] = entry
    return {"elementHeader": header, "properties": property_map(item.get("elementProperties"))}


__all__ = ["as_view_element", "is_raw_element", "property_map", "property_value"]
