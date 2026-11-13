# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Published versions (D14, owner 2026-11-13): "Published versions are immutable: a change means a new version."

**A new version under a stable identity.** A spec, Report or sheet keeps its qualifiedName and GUID; each
publish writes one new state of that element, with a **publication stamp** in its additionalProperties:

- `publishedVersion`: the stamped value it had (0 when it had none) + 1;
- `publishedAt`: UTC ISO time of the publish; `publishedBy`: the publisher's userId.

The stamp is written in the same Create/Update block as the content, so the stamp and the content land in one
Egeria version. Egeria's element history is append-only, so every earlier published state stays readable.

**Which history entry is published version N.** The **oldest** entry carrying `publishedVersion` N: the
publish wrote it. A later edit outside publishing (Dr.Egeria by hand, a re-sync, EA chat) leaves the stored
additionalProperties in place, so it carries the same stamp but different content; taking the newest
stamped entry would let such an edit change what "version N" reads. Content is what makes N immutable, so
the publish write itself is the version. (The brief, BRIEF-PYEGERIA-AUTHORING-D14, said "newest"; it assumed
edits drop the stamp. They don't: Egeria and pyegeria both keep the stored map on a merge update.)

**Edited since publication** is reported, never an error: an entry newer than the publication entry of the
current stamp whose properties differ from it. A classification-only change (Declassify on promotion, a
zone) doesn't change the properties, so it doesn't count.

**Pins name publications**, not Egeria instance versions (those count every change, zones included).

**Exact target, never a twin.** Before any plan, the element is found by exact qualifiedName (a Report
without one, by exact display name), as the user, with a page of 25 (B5: never 1). More than one match, a
full page, or a failed read refuses: a wrongly created twin would split the history and orphan every pin.

**No silent overwrite.** apply re-resolves the target and refuses if its GUID or `publishedVersion` changed
since the plan was made.

**Nothing deletes a published element.** No path in pyegeria.authoring deletes an element that carries a
publication stamp (withdraw removes folder membership only; retire is phase 2). Draft prune deletes only
unstamped private drafts.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from pyegeria.authoring.models import AuthoringRefused, ReportDraft, SpecDraft, as_draft

PUBLISHED_VERSION_KEY = "publishedVersion"
PUBLISHED_AT_KEY = "publishedAt"
PUBLISHED_BY_KEY = "publishedBy"
STAMP_KEYS = (PUBLISHED_AT_KEY, PUBLISHED_BY_KEY, PUBLISHED_VERSION_KEY)
#: additionalProperties keys the authoring API writes for itself. They are bookkeeping, never a Report
#: parameter, so readers that pass a Report's other additionalProperties to its spec skip them.
AUTHORING_KEYS = frozenset({"authoringState", "reportSpecVersion", *STAMP_KEYS})
TARGET_TYPES = {"spec": "ReportSpec", "report": "Report", "sheet": "Dashboard"}
#: B5: Egeria pages before it filters archived elements, so a one-element page can come back empty.
LOOKUP_PAGE = 25
#: The publishedAt value the plan digest is computed with: the time is set when the plan runs.
AT_PLACEHOLDER = "(set when published)"

NOT_RESOLVED = ("Publishing finds the exact element it will write first (D14), as you: plan with "
                "async_publish_plan(draft, client) (or pass the resolved target as held).")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _int(value: Any) -> Optional[int]:
    try:
        n = int(str(value).strip())
    except (TypeError, ValueError):
        return None
    return n if n >= 1 else None


def stamp_of(el: Optional[Dict[str, Any]]) -> Optional[int]:
    """The element's `publishedVersion`, or None when it has none (unversioned)."""
    extra = ((el or {}).get("properties") or {}).get("additionalProperties") or {}
    return _int(extra.get(PUBLISHED_VERSION_KEY)) if isinstance(extra, dict) else None


def _egeria_version(el: Dict[str, Any]) -> Optional[int]:
    v = ((el.get("elementHeader") or {}).get("versions") or {}).get("version")
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _content(el: Dict[str, Any]) -> Dict[str, Any]:
    """An entry's properties, less publishedAt (a re-stamp of the same version isn't a content change)."""
    props = dict(el.get("properties") or {})
    extra = props.get("additionalProperties")
    if isinstance(extra, dict):
        props["additionalProperties"] = {k: v for k, v in extra.items() if k != PUBLISHED_AT_KEY}
    return props


def ordered_entries(current: Optional[Dict[str, Any]], history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Current element and its history, one entry per Egeria version, oldest first."""
    seen: Dict[Any, Dict[str, Any]] = {}
    for el in [*(history or []), *([current] if current else [])]:
        key = _egeria_version(el)
        seen[key if key is not None else id(el)] = el   # the current element wins its own version
    return sorted(seen.values(), key=lambda e: (_egeria_version(e) is None, _egeria_version(e) or 0))


def published_versions(entries: List[Dict[str, Any]]) -> List[int]:
    return sorted({s for s in (stamp_of(e) for e in entries) if s is not None})


def publication_entry(entries: List[Dict[str, Any]], version: int) -> Optional[Dict[str, Any]]:
    """The history entry that IS published version `version`: the oldest one stamped with it."""
    return next((e for e in entries if stamp_of(e) == version), None)


def edited_since(entries: List[Dict[str, Any]], version: Optional[int]) -> bool:
    """Whether the element's content changed after published version `version` was written."""
    if version is None:
        return False
    pub = publication_entry(entries, version)
    if pub is None:
        return False
    base, later = _content(pub), entries[entries.index(pub) + 1:]
    return any(_content(e) != base for e in later)


def edited_note(label: str, version: int) -> str:
    return (f"{label} has been changed since published version {version} (outside publishing); followers see "
            f"the change, pins to {version} do not")


# ── Finding the exact target ─────────────────────────────────────────────────

def target_of(draft: Any) -> Tuple[str, str, str, str]:
    """(kind, element type, property searched, value): how the draft's element is found."""
    draft = as_draft(draft)
    if isinstance(draft, SpecDraft):
        from pyegeria.view.report_spec_publish import spec_qualified_name
        return "spec", "ReportSpec", "qualifiedName", spec_qualified_name(draft.label)
    if isinstance(draft, ReportDraft):
        if draft.qualified_name:
            return "report", "Report", "qualifiedName", draft.qualified_name
        return "report", "Report", "displayName", draft.display_name
    return "sheet", "Dashboard", "qualifiedName", f"Dashboard::{draft.name}"


def _is_not_found(exc: BaseException) -> bool:
    from pyegeria.core._exceptions import PyegeriaNotFoundException
    return isinstance(exc, PyegeriaNotFoundException)


async def _find_exact(client: Any, type_name: str, prop: str, value: str) -> List[Dict[str, Any]]:
    try:
        found = await client.classification_manager._async_get_elements_by_property_value(
            value, [prop], metadata_element_type=type_name, starts_with=False, ends_with=False, ignore_case=False,
            page_size=LOOKUP_PAGE, graph_query_depth=0)
    except Exception as exc:  # noqa: BLE001
        if _is_not_found(exc):
            return []
        raise AuthoringRefused(f"Couldn't find out whether Egeria already holds the {type_name} {value!r} "
                               f"({type(exc).__name__}). Publishing needs to know which element it writes, so "
                               f"nothing was planned; try again.") from exc
    rows = [e for e in found if isinstance(e, dict) and e.get("elementHeader")] if isinstance(found, list) else []
    if len(rows) >= LOOKUP_PAGE:
        raise AuthoringRefused(f"Egeria answered a full page ({LOOKUP_PAGE}) for the {type_name} {value!r}, so "
                               f"which element to write can't be told. Nothing was planned.")
    return [e for e in rows if (e.get("properties") or {}).get(prop) == value]


async def _history(client: Any, guid: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    from pyegeria.core.element_shape import as_view_element
    try:
        raw = await client.metadata_expert._async_get_element_history(guid, oldest_first=False, page_size=0)
    except Exception as exc:  # noqa: BLE001 -- said, not raised
        return [], f"its history couldn't be read ({type(exc).__name__})"
    if not isinstance(raw, list):
        return [], None   # "No elements found": no earlier versions
    return [as_view_element(e) for e in raw if isinstance(e, dict)], None


async def async_resolve_target(client: Any, draft: Any) -> Dict[str, Any]:
    """The element the draft's publish would write, read as the user. Returns the plan's `held`:

        {"resolved": True, "held": bool, "guid", "qualified_name", "zones", "published_version" (int|None),
         "published_versions": [...], "edited_since": bool|None, "notes": [...]}

    Refused in words when it can't be told (a failed read, more than one match, a full page)."""
    return await _resolve(client, target_of(draft))


async def _resolve(client: Any, target: Tuple[str, str, str, str]) -> Dict[str, Any]:
    if client is None:
        raise AuthoringRefused(NOT_RESOLVED)
    kind, type_name, prop, value = target
    matches = await _find_exact(client, type_name, prop, value)
    if len(matches) > 1:
        raise AuthoringRefused(f"Egeria holds {len(matches)} {type_name} elements with {prop} {value!r}; publishing "
                               f"would write one and leave the other. Give the qualified name, or remove the "
                               f"duplicate. Nothing was planned.")
    if not matches:
        return {"resolved": True, "held": False, "guid": None, "qualified_name": value if prop == "qualifiedName"
                else None, "zones": [], "published_version": None, "published_versions": [],
                "edited_since": False, "notes": []}
    el = matches[0]
    from pyegeria.view.egeria_spec_cache import _zones
    guid = (el.get("elementHeader") or {}).get("guid")
    history, why = await _history(client, guid) if guid else ([], "it has no GUID")
    entries = ordered_entries(el, history)
    current = stamp_of(el)
    notes = [f"Edited-since check not done: {why}."] if why else []
    edited = None if why else edited_since(entries, current)
    return {"resolved": True, "held": True, "guid": guid, "qualified_name": (el.get("properties") or {}).get("qualifiedName"),
            "zones": list(_zones(el)), "published_version": current,
            "published_versions": published_versions(entries), "edited_since": edited, "notes": notes}


async def async_check_unchanged_target(client: Any, plan: Dict[str, Any]) -> None:
    """Refuse when the plan's target changed since it was planned (another publish, a new twin)."""
    held = plan.get("publication") or {}
    if not held.get("resolved"):
        return
    if client is None:
        raise AuthoringRefused("Publishing re-checks the element it writes as you, just before it runs: "
                               "a client is needed.")
    now = await _resolve(client, tuple(plan["target"]))
    label = plan.get("label")
    if bool(now["held"]) != bool(held.get("held")) or now.get("guid") != held.get("guid"):
        raise AuthoringRefused(f"{label} is no longer the element this plan was made for (it was "
                               f"{'held' if held.get('held') else 'not held'} then); re-plan.")
    if now.get("published_version") != held.get("published_version"):
        raise AuthoringRefused(f"{label} was published as version {now.get('published_version')} since this plan "
                               f"was made (the plan was for version {held.get('published_version') or 'none'}); "
                               f"re-plan.")


async def async_publication_notes(client: Any, draft: Any) -> Tuple[List[str], List[str]]:
    """(notes, not_checked) about the draft's published element, for validate and preview: an edit since its
    publication is said (reporting, never an error); a target that can't be read is said as not checked."""
    try:
        held = await async_resolve_target(client, draft)
    except AuthoringRefused as exc:
        return [], [f"published version: not read ({exc})"]
    kind, _, _, value = target_of(draft)
    notes = list(held.get("notes") or [])
    if held.get("edited_since"):
        notes.append(edited_note(f"{kind} {value!r}", held["published_version"]))
    return notes, []


# ── The stamp in the document ────────────────────────────────────────────────

def next_version(held: Dict[str, Any]) -> int:
    return (held.get("published_version") or 0) + 1


def stamp_lines(version: int, published_by: str, published_at: Optional[str] = None) -> List[str]:
    """The stamp as Dr.Egeria Dictionary lines (`key: value`, sorted by key)."""
    if not published_by:
        raise AuthoringRefused("A publish is stamped with who published it: the client's user id is needed.")
    return [f"{PUBLISHED_AT_KEY}: {published_at or AT_PLACEHOLDER}", f"{PUBLISHED_BY_KEY}: {published_by}",
            f"{PUBLISHED_VERSION_KEY}: {version}"]


def stamp_step(label: str, held: Dict[str, Any]) -> str:
    n = held.get("published_version")
    if n:
        return f"publish version {n + 1} of {label}; version {n} stays readable for Reports pinned to it"
    if held.get("held"):
        return (f"publish {label} as version 1 (it is held, but was never published through the authoring API: "
                f"its earlier states have no version number and can't be pinned)")
    return f"publish {label} as version 1"


def digest_text(markdown: str) -> str:
    """The plan's markdown as its digest sees it: publishedAt is set when the plan runs, so it's left out."""
    out = []
    for line in markdown.splitlines():
        if line.startswith(f"{PUBLISHED_AT_KEY}: "):
            line = f"{PUBLISHED_AT_KEY}: {AT_PLACEHOLDER}"
        out.append(line)
    return "\n".join(out) + ("\n" if markdown.endswith("\n") else "")


def with_time(markdown: str, at: str) -> str:
    """The plan's markdown with publishedAt set to `at` (done when it runs)."""
    return "\n".join(f"{PUBLISHED_AT_KEY}: {at}" if line.startswith(f"{PUBLISHED_AT_KEY}: ") else line
                     for line in markdown.splitlines()) + ("\n" if markdown.endswith("\n") else "")


__all__ = ["PUBLISHED_VERSION_KEY", "PUBLISHED_AT_KEY", "PUBLISHED_BY_KEY", "STAMP_KEYS", "AUTHORING_KEYS",
           "LOOKUP_PAGE", "NOT_RESOLVED", "stamp_of", "ordered_entries", "published_versions", "publication_entry",
           "edited_since", "edited_note", "target_of", "async_resolve_target", "async_check_unchanged_target",
           "next_version", "stamp_lines", "stamp_step", "digest_text", "with_time", "now_iso"]
