# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""A report spec at a given version, resolved as the user (D14: follow latest by default, pinning allowed).

A Report follows the latest version of its spec unless it pins one (`ReportDraft.pinned_version`, written as
the Report's `reportSpecVersion`). A pinned version is read from the spec element's own history in Egeria,
**as the user** (the caller's client), and converted by the same code the spec cache uses. It never goes
through the public fetched-name path (`egeria:<label>@vN`, a process-wide map shared across users; the
Portal-3 hazard), and nothing is cached or registered.

Published versions are treated as immutable in effect: a change is a new version, so version N always
means the same spec.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from pyegeria.authoring.models import AuthoringRefused


def as_element(item: Dict[str, Any]) -> Dict[str, Any]:
    """A history entry as the element shape the rest of pyegeria reads. Egeria's element history returns
    OpenMetadataElements (`elementGUID`, `versions`, `elementProperties.propertyValueMap`) rather than view
    beans (`elementHeader`, flat `properties`); a view bean is returned unchanged."""
    if item.get("elementHeader"):
        return item
    from pyegeria.view.saved_query import _properties
    header = {k: item.get(k) for k in ("type", "versions", "origin", "status", "classifications") if k in item}
    header["guid"] = item.get("elementGUID")
    for c in item.get("classifications") or []:
        if isinstance(c, dict) and (c.get("type") or {}).get("typeName") == "ZoneMembership":
            header["zoneMembership"] = c
    return {"elementHeader": header, "properties": _properties(item)}


def _version_of(el: Dict[str, Any]) -> Optional[int]:
    v = ((el.get("elementHeader") or {}).get("versions") or {}).get("version")
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


async def async_spec_versions(client: Any, label: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """(the current spec element, every version Egeria returns for it, newest first), read as the user."""
    from md_processing.v2.report import find_report_spec_element
    current = await find_report_spec_element(client, label)
    if not current:
        raise AuthoringRefused(f"Egeria holds no report spec {label!r} that you can see.")
    guid = (current.get("elementHeader") or {}).get("guid")
    try:
        raw = await client.metadata_expert._async_get_element_history(guid, oldest_first=False, page_size=0)
    except Exception as exc:  # noqa: BLE001 -- said in words
        raise AuthoringRefused(f"The versions of spec {label!r} could not be read: {type(exc).__name__}: "
                               f"{' '.join(str(exc).split())[:200]}") from exc
    versions = [as_element(e) for e in raw if isinstance(e, dict) and (e.get("elementHeader") or e.get("elementGUID"))] \
        if isinstance(raw, list) else []
    return current, versions


async def async_spec_at_version(client: Any, label: str, version: int):
    """The FormatSet of spec `label` at `version`, read as the user. Refused in words when that version isn't
    held (the versions that are, are named)."""
    from pyegeria.view.egeria_spec_cache import _Skip, _build
    if client is None:
        raise AuthoringRefused("A pinned spec version is read from Egeria as you: a client is needed.")
    current, history = await async_spec_versions(client, label)
    candidates = [current] + history
    found = next((el for el in candidates if _version_of(el) == version), None)
    if found is None:
        held = sorted({v for v in (_version_of(el) for el in candidates) if v is not None})
        raise AuthoringRefused(f"Spec {label!r} has no version {version}; Egeria holds "
                               f"{', '.join(str(v) for v in held) or 'no readable versions'}.")
    try:
        built = _build(found, folders=[], identity=getattr(client, "user_id", "") or "")
    except _Skip as exc:
        raise AuthoringRefused(f"Version {version} of spec {label!r} can't be read as a spec: {exc.reason}")
    return built.format_set
