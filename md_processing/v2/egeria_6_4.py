# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Shared pieces of the Dr.Egeria commands for the Egeria 6.4 additions (odpi/egeria#9463).

- **The version gate.** Every 6.4 command asks pyegeria.core.egeria_6_4_gate first. On an Egeria before 6.4 the
  command is refused with the "needs Egeria 6.4" words, as a WARNING row: never an error, never "none", and
  nothing is sent. When the platform's version can't be read, the command runs, and a bare HTTP 404 from its
  6.4 request is turned into the same words.
- **Bodies.** The request bodies are built here from the parsed attributes, then sent through the pyegeria 6.4
  wrappers, which check the properties class and refuse keys the class doesn't read. Keys the class doesn't
  read are therefore dropped here first and reported as "not applied", the same as the rest of Dr.Egeria.
- **Values.** Position-style attributes must be whole numbers; times used to pick one assessment must carry a
  zone and are compared as UTC instants.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pyegeria.core.egeria_6_4_gate import async_egeria_6_4_status, is_missing_6_4_endpoint, needs_6_4_words
from pyegeria.core.utils import body_slimmer
from md_processing.md_processing_utils.common_md_utils import (
    set_delete_rel_request_body, set_rel_prop_body, set_rel_request_body)
from md_processing.md_processing_utils.typed_properties import record_not_applied
from md_processing.v2.processors import AsyncBaseCommandProcessor

EMPTY = (None, "", [], {})


def value(attributes: Dict[str, Any], name: str) -> Any:
    return (attributes.get(name) or {}).get("value")


def guid(attributes: Dict[str, Any], name: str) -> Optional[str]:
    return (attributes.get(name) or {}).get("guid")


def read_keys_only(props: dict, attributes: Dict[str, Any], attribute_of: Dict[str, str]) -> dict:
    """Drop the keys `props["class"]` doesn't read (Egeria would ignore them, and the 6.4 wrappers refuse them),
    reporting each given one as "not applied" on the attribute it came from."""
    from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
    cls = props.get("class")
    reads = (PROPERTIES_CLASS_FIELDS.get(cls) or ("", None))[1]
    if reads is None:
        return props
    for key in [k for k in props if k != "class" and k not in reads]:
        dropped = props.pop(key)
        attribute = attribute_of.get(key)
        if attribute and dropped not in EMPTY:
            record_not_applied(attributes, attribute, [f"not applied: {attribute}: {cls} has no {key} property"])
    return props


def int_value(attributes: Dict[str, Any], name: str) -> Optional[int]:
    """A whole-number attribute (Position, Min/Max Cardinality); refused with words when it isn't one."""
    raw = value(attributes, name)
    if raw in EMPTY:
        return None
    try:
        return int(str(raw).strip())
    except ValueError:
        raise ValueError(f"{name} must be a whole number; '{raw}' isn't one.") from None


def utc_instant(text: Any, name: str) -> datetime:
    """An ISO 8601 date/time WITH a zone, as a UTC instant. A time with no zone is refused: it can't be compared
    with what Egeria stored."""
    s = str(text).strip()
    try:
        when = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"{name} '{s}' isn't an ISO 8601 date/time (for example 2026-11-21T10:00:00Z).") from None
    if when.tzinfo is None:
        raise ValueError(f"{name} '{s}' has no time zone, so it can't be compared with the time Egeria stored. "
                         f"Add one, for example {s}Z for UTC or {s}+01:00.")
    return when.astimezone(timezone.utc)


def stored_instant(stored: Any) -> Optional[datetime]:
    """A time as Egeria returns it (ISO 8601 text, or epoch milliseconds), as a UTC instant; None if unreadable."""
    if stored in EMPTY:
        return None
    try:
        if isinstance(stored, (int, float)):
            return datetime.fromtimestamp(stored / 1000, tz=timezone.utc)
        when = datetime.fromisoformat(str(stored).strip().replace("Z", "+00:00"))
        return (when if when.tzinfo else when.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
    except (ValueError, OverflowError):
        return None


#: The Link Command Base / relationship attributes and the property each fills.
REL_ATTRIBUTE_OF = {"label": "Label", "description": "Description", "effectiveFrom": "Effective From",
                    "effectiveTo": "Effective To", "extendedProperties": "Extended Properties", "typeName": "Type Name"}


def new_relationship_body(type_name: str, attributes: Dict[str, Any], extra: Optional[dict] = None,
                          extra_attribute_of: Optional[Dict[str, str]] = None, with_properties: bool = True) -> dict:
    """A NewRelationshipRequestBody for a 6.4 link: `<type_name>Properties` from the shared relationship attributes
    plus `extra`, only keys the class reads. With nothing but the class (and typeName) given, no properties are
    sent: the 6.4 attach takes a body with no properties."""
    body = set_rel_request_body(type_name, attributes)
    props = {**set_rel_prop_body(type_name, attributes), **(extra or {})}
    props = read_keys_only(body_slimmer(props), attributes, {**REL_ATTRIBUTE_OF, **(extra_attribute_of or {})})
    meaningful = {k for k, v in props.items() if k not in ("class", "typeName") and v not in EMPTY}
    body["properties"] = props if (with_properties and meaningful) else None
    return body_slimmer(body)


def update_relationship_body(type_name: str, attributes: Dict[str, Any], extra: Optional[dict] = None,
                             extra_attribute_of: Optional[Dict[str, str]] = None) -> dict:
    """An UpdateRelationshipRequestBody (mergeUpdate unless Merge Update says otherwise)."""
    new = new_relationship_body(type_name, attributes, extra, extra_attribute_of)
    props = new.get("properties") or {"class": f"{type_name}Properties"}
    merge = value(attributes, "Merge Update")
    return body_slimmer({
        "class": "UpdateRelationshipRequestBody",
        "externalSourceGUID": new.get("externalSourceGUID"),
        "externalSourceName": new.get("externalSourceName"),
        "effectiveTime": new.get("effectiveTime"),
        "forLineage": new.get("forLineage", False),
        "forDuplicateProcessing": new.get("forDuplicateProcessing", False),
        "mergeUpdate": True if merge in EMPTY else bool(merge),
        "properties": props,
    })


def delete_relationship_body(attributes: Dict[str, Any]) -> dict:
    return body_slimmer(set_delete_rel_request_body("", attributes))


class Egeria64Processor(AsyncBaseCommandProcessor):
    """Base of every 6.4 command: the version gate around the normal execution."""

    _needs_6_4: bool = False

    def _needs_6_4_result(self, platform_url: str, version: str) -> Dict[str, Any]:
        what = f"{self.command.verb} {self.command.object_type}"
        words = needs_6_4_words(what, platform_url, version)
        parsed = self.parsed_output or {}
        return {
            "output": f"{self.command.raw_block}\n\n> ⚠️ **Needs Egeria 6.4**\n> - {words}\n",
            "status": "warning",
            "message": words,
            "verb": self.command.verb,
            "object_type": self.canonical_object_type,
            "markdown_object_type": self.markdown_object_type,
            "display_name": parsed.get("display_name"),
            "qualified_name": parsed.get("qualified_name"),
            "found": False,
            "needs_egeria_6_4": True,
        }

    async def execute(self) -> Dict[str, Any]:
        directive = self.context.get("directive", "process")
        url, version = getattr(self.client, "platform_url", "") or "", ""
        if directive in ("process", "validate"):
            carries, version, url = await async_egeria_6_4_status(self.client)
            if carries is False:
                return self._needs_6_4_result(url, version)
        self._needs_6_4 = False
        result = await super().execute()
        if self._needs_6_4:
            return self._needs_6_4_result(url, "")
        return result

    async def e64(self, awaitable):
        """Await a pyegeria 6.4 request; a bare 404 (the endpoint isn't served) marks the command "needs 6.4"."""
        try:
            return await awaitable
        except Exception as e:
            if is_missing_6_4_endpoint(e):
                self._needs_6_4 = True
            raise


class Egeria64LinkProcessor(Egeria64Processor):
    """A 6.4 relationship command: there is no target element of its own to look up or upsert."""

    def supports_target_element_lookup(self) -> bool:
        return False

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    LINK_VERBS = {"Link", "Attach", "Add"}
    DETACH_VERBS = {"Detach", "Unlink", "Remove"}

    def ends(self, attributes: Dict[str, Any], *names: str) -> list[str]:
        """The GUIDs of the named end attributes; refused with words naming any that is missing."""
        found = [guid(attributes, n) for n in names]
        missing = [n for n, g in zip(names, found) if not g]
        if missing:
            raise ValueError(f"{self.command.verb} {self.command.object_type} needs {' and '.join(missing)} "
                             f"(a qualified name, display name or GUID that resolves to an element).")
        return found  # type: ignore[return-value]
