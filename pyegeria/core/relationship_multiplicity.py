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
UNI_LINK, 9 REVERSIBLE. Note SolutionLinkingWire is UNI_LINK in the live
type registry despite being treated as multi-link by existing Dr.Egeria
code (Egeria PR #9156) -- per user direction, `relationshipCategory` is
the source of truth going forward for new/updated detection logic.

Only REVERSIBLE and MULTI_LINK are of practical interest to callers here;
UNI_LINK is treated as "not multi-link" (`is_multi_link()` returns False).
"""
from __future__ import annotations

from typing import Optional

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
