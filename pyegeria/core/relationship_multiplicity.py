# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Multi-link relationship detection.

"Multi-link" means more than one instance of a relationship type may exist
between the same ordered pair of elements (e.g. DataFlow, ControlFlow,
Certification) -- as opposed to the common case where a relationship type
allows at most one instance between a given pair. For a multi-link type, a
relationship's own GUID (not just the pair of element GUIDs) is required to
target a *specific* instance for Update/Detach.

There is no literal boolean field named "multi-link" in Egeria's type-def
JSON. The real, live-queryable signal is the `relationshipCategory` field
returned by `ValidMetadataManager.get_all_relationship_defs()`, with values:

  - "MULTI_LINK"  -- more than one instance may exist between the same pair
  - "UNI_LINK"    -- at most one instance between a given pair (the default)
  - "REVERSIBLE"  -- symmetric relationship (e.g. Synonym, Antonym)

Confirmed live against a running server (2026-08-16): 21 MULTI_LINK types
(DataFlow, ControlFlow, Certification, License, CatalogTarget, ... -- see
`get_all_relationship_defs()` for the current authoritative list), 169
UNI_LINK, 9 REVERSIBLE. SolutionLinkingWire was reported as UNI_LINK then
because the 6.1 type patch set multiLink without updateMultiLink; a later
Egeria types patch (updateSolutionLinkingWireRelationship) corrects it, and
it is MULTI_LINK on current platforms, as is DigitalProductDependency.
`relationshipCategory` is the source of truth for detection logic.

Because a multi-link `Link` command can never rely on the server to reject
or merge a second instance, re-running the same Dr.Egeria markdown would
pile up duplicates.  `async_find_matching_relationship` locates the instance
a command describes (same ends, same identifying properties) so the caller
can update it in place instead.

Only REVERSIBLE and MULTI_LINK are of practical interest to callers here;
UNI_LINK is treated as "not multi-link" (`is_multi_link()` returns False).
"""
from __future__ import annotations

from typing import Any, Optional

# Cached per (platform_url, view_server) since relationship type defs are
# effectively static for the lifetime of a session -- avoids a network
# round-trip on every multi-link check. Keyed by a plain tuple rather than
# the client instance itself since multiple client objects may point at the
# same server.
_relationship_category_cache: dict[tuple[str, str], dict[str, str]] = {}

MULTI_LINK = "MULTI_LINK"
UNI_LINK = "UNI_LINK"
REVERSIBLE = "REVERSIBLE"


def _cache_key(client) -> tuple[str, str]:
    return (getattr(client, "platform_url", ""), getattr(client, "view_server", ""))


async def _async_get_relationship_category_map(client, refresh: bool = False) -> dict[str, str]:
    """Return {relationship type name: relationshipCategory}, fetching once per server and caching.

    Parameters
    ----------
    client
        Any OMVS client with `_async_get_all_relationship_defs` (i.e. a
        `ValidMetadataManager` or an `EgeriaTech` facade that proxies to one).
    refresh: bool, default = False
        Bypass the cache and re-fetch from the server.
    """
    key = _cache_key(client)
    if not refresh and key in _relationship_category_cache:
        return _relationship_category_cache[key]

    defs = await client._async_get_all_relationship_defs()
    category_map: dict[str, str] = {}
    if isinstance(defs, list):
        for d in defs:
            if not isinstance(d, dict):
                continue
            name = d.get("name")
            category = d.get("relationshipCategory")
            if name and category:
                category_map[name] = category

    _relationship_category_cache[key] = category_map
    return category_map


async def async_get_relationship_category(client, relationship_type_name: str, refresh: bool = False) -> Optional[str]:
    """Return the relationshipCategory ("MULTI_LINK" | "UNI_LINK" | "REVERSIBLE") for a relationship type, or None if unknown."""
    category_map = await _async_get_relationship_category_map(client, refresh=refresh)
    return category_map.get(relationship_type_name)


async def async_is_multi_link(client, relationship_type_name: str, refresh: bool = False) -> bool:
    """True if this relationship type allows more than one instance between the same pair of elements.

    Unknown type names return False rather than raising -- callers that
    don't recognize a relationship type name should fall back to
    pair-based (non-GUID-targeted) semantics, the historical default.
    """
    category = await async_get_relationship_category(client, relationship_type_name, refresh=refresh)
    return category == MULTI_LINK


def clear_relationship_category_cache() -> None:
    """Drop all cached relationshipCategory lookups. Mainly useful for tests."""
    _relationship_category_cache.clear()


def _relationship_property(rel: dict, name: str) -> Any:
    """Read a property from a relationship returned by find-relationships.

    The by-search-conditions endpoint returns properties in OMRS instance form
    (`relationshipProperties.propertyValueMap.<name>.primitiveValue`); other
    endpoints return a flat bean (`relationshipProperties.<name>`).  Accept both.
    """
    props = rel.get("relationshipProperties") or rel.get("properties") or {}
    value_map = props.get("propertyValueMap")
    if isinstance(value_map, dict):
        entry = value_map.get(name)
        return entry.get("primitiveValue") if isinstance(entry, dict) else entry
    return props.get(name)


async def async_find_matching_relationship(client, relationship_type_name: str, end1_guid: str, end2_guid: str,
                                           match_properties: dict[str, Any]) -> Optional[str]:
    """Return the GUID of the relationship of this type between end1 and end2 whose identifying
    properties all equal `match_properties`, or None if there is none.

    Used by Dr.Egeria `Link` commands on MULTI_LINK types so that re-running a file updates the
    instance it created rather than adding another.  A property whose expected value is None must
    be absent (or null) on the relationship, so a dependency with no supply chain is not confused
    with one that names a chain.  The search is narrowed on the server by the string-valued
    properties, so it does not depend on paging through every relationship of the type.
    With empty `match_properties`, any relationship of the type between the two ends matches.

    Parameters
    ----------
    client
        Any client with `_async_find_relationships_between_elements` (e.g. `EgeriaTech`).
    relationship_type_name: str
        e.g. "DigitalProductDependency", "SolutionLinkingWire".
    end1_guid, end2_guid: str
        GUIDs of the elements at end 1 and end 2, in that order.
    match_properties: dict
        Property name -> expected value, e.g. {"label": "...", "iscQualifiedName": "..."}.
    """
    if not end1_guid or not end2_guid:
        return None
    # Only strings narrow the server search; other values are still matched client-side below.
    conditions = [
        {"property": name, "operator": "EQ",
         "value": {"class": "PrimitiveTypePropertyValue", "typeName": "string", "primitiveValue": value}}
        for name, value in match_properties.items() if isinstance(value, str)
    ]
    body: dict[str, Any] = {"class": "FindRelationshipRequestBody", "relationshipTypeName": relationship_type_name}
    if conditions:
        body["searchProperties"] = {"class": "SearchProperties", "conditions": conditions, "matchCriteria": "ALL"}

    found = await client._async_find_relationships_between_elements(body)
    # The endpoint returns {"relationships": [...], "mermaidGraph": ...}; older code expected a bare list.
    if isinstance(found, dict):
        found = found.get("relationships") or []
    if not isinstance(found, list):
        return None

    for rel in found:
        if not isinstance(rel, dict):
            continue
        if rel.get("elementGUIDAtEnd1") != end1_guid or rel.get("elementGUIDAtEnd2") != end2_guid:
            continue
        if all(_relationship_property(rel, name) == value for name, value in match_properties.items()):
            return rel.get("relationshipGUID")
    return None
