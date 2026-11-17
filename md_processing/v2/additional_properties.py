"""additionalProperties on a merge update: keep the keys the document doesn't write.

Egeria replaces a map property as one value, even on a merge update (`mergeUpdate: true` merges
properties, not the keys inside one map property). A Dr.Egeria Create that finds its element (and
becomes an Update), or an Update with Merge Update true, used to send only the keys its document
gave, so every other key on the element was removed: on laz a SavedQuery's refresh keys
(lastRefreshedTime, resultCount, resultsSetGuid, smartQueryRelGuid, lastRefreshParams) were wiped
this way, and a CDO Report's search keys nearly were.

The fix: on a merge update, read the element's stored map and overlay the document's keys on it,
key by key, so the map sent is the whole map. A replace update (Merge Update false) still replaces,
and says which keys go.

There is no way in a Dr.Egeria document to clear a single key: a Dictionary value is parsed to
strings (a JSON `null` becomes the string "null"), and an empty value is no value. To remove keys,
use Merge Update false, which replaces the element's properties with exactly what the document gives.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional


class AdditionalPropertiesUnreadable(ValueError):
    """A merge update would send additionalProperties, but the stored map couldn't be read."""


def stored_additional_properties(element: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """The element's stored additionalProperties ({} when it has none), or None when the element
    wasn't read with its properties (so its map is unknown)."""
    if not isinstance(element, dict):
        return None
    properties = element.get("properties")
    if not isinstance(properties, dict):
        return None
    stored = properties.get("additionalProperties")
    if stored is None:
        return {}
    return dict(stored) if isinstance(stored, dict) else None


def merge_additional_properties(stored: Dict[str, Any], document: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """The stored map with the document's keys laid over it: the document wins key by key, and keys
    it doesn't give are kept."""
    merged = dict(stored or {})
    merged.update(document or {})
    return merged


def replace_note(stored: Optional[Dict[str, Any]], sent_keys: Iterable[str]) -> Optional[str]:
    """The sentence a replace update (Merge Update false) adds, naming the stored keys it removes."""
    removed = sorted(set(stored or {}) - set(sent_keys))
    if not removed:
        return None
    return ("Merge Update is false, so this update replaces additionalProperties as a whole: "
            f"these stored keys are removed: {', '.join(removed)}")


def unreadable_message(what: str) -> str:
    return (f"Refusing to update {what}: the update would send additionalProperties, but the element's "
            "stored additionalProperties couldn't be read, and Egeria replaces that map as a whole, so the "
            "keys this document doesn't give would be removed. Re-run once the element can be read, or set "
            "Merge Update to false to replace the map on purpose.")
