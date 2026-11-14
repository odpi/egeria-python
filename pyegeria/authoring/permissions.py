"""Can this user edit this spec, Report or sheet? (P2, for "Edit in Studio"; the owner's decision C, the
Architect's ruling (b), RULINGS-SD-DCAT-BATCH-2026-11-14-late.)

Egeria has no "may I edit this?" API, so the answer is three-way and read as the user:
- **yes**: the user's own private draft (zoned exactly ``[<userId>]``); or a held artifact whose element the user
  created (``versions.createdBy``) or owns (the Ownership classification names their user id). For a published
  one, editing means a new draft from it (new_from) and later publishing a new version, which Egeria still
  authorises on update.
- **no**: a built-in spec (pyegeria's own, not in Egeria; copy it to a new draft), or nothing the user can read in
  Egeria (absent, or not visible to them: Egeria doesn't tell those apart).
- **unknown**: everything else, e.g. a steward with rights through a role (Egeria exposes no rights source), an
  owner named by something other than a user id, or a read that didn't give an answer. The Portal hides the link
  on unknown and logs `why`; Studio still checks on open and at publish.

Nothing is cached: every call reads as `client`.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from pyegeria.authoring.models import ANSWER_REFUSED, ANSWER_UNKNOWN, KINDS, AuthoringRefused

YES, NO, UNKNOWN = "yes", "no", "unknown"
CAN_EDIT_ANSWERS = (YES, NO, UNKNOWN)


def _answer(answer: str, why: str) -> Dict[str, str]:
    return {"answer": answer, "why": why}


def _header(el: Dict[str, Any]) -> Dict[str, Any]:
    return (el or {}).get("elementHeader") or {}


def _owner(el: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """The Ownership classification's properties: its own header key in Egeria 6, else in the classification
    lists (older shapes)."""
    header = _header(el)
    candidates = [header.get("ownership")]
    for key in ("otherClassifications", "classifications"):
        candidates += [c for c in (header.get(key) or []) if isinstance(c, dict)
                       and c.get("classificationName") == "Ownership"]
    for c in candidates:
        if isinstance(c, dict) and isinstance(c.get("classificationProperties"), dict):
            return c["classificationProperties"]
    return None


async def _read(kind: str, ref: str, client: Any) -> Optional[Dict[str, Any]]:
    """The element as the user, None when Egeria holds none they can see. Raises AuthoringRefused (answer
    unknown or refused) for a read that can't say, and lets any other error through."""
    from pyegeria.authoring.lifecycle import _by_qualified_name, _report_element
    if kind == "spec":
        from md_processing.v2.report import find_report_spec_element
        return await find_report_spec_element(client, ref)
    if kind == "report":
        return await _report_element(client, ref)
    return await _by_qualified_name(client, ref if ref.startswith("Dashboard::") else f"Dashboard::{ref}")


def _is_builtin_spec(label: str) -> bool:
    from pyegeria.view.base_report_formats import lookup_report_spec
    for prefix in ("ReportSpec::", "ReportType::"):
        if label.startswith(prefix):
            label = label[len(prefix):]
    fs, _tier, _label = lookup_report_spec(f"builtin:{label}")
    return fs is not None


async def async_can_edit(kind: str, ref: str, client: Any) -> Dict[str, str]:
    """``{"answer": "yes"|"no"|"unknown", "why": <words>}`` for `kind` ("spec", "report" or "sheet") named `ref`
    (a label, display name or qualified name), read from Egeria as `client`'s user. Never raises for a read;
    raises AuthoringRefused only for a bad kind, an empty ref, or no client."""
    if kind not in KINDS:
        raise AuthoringRefused(f"can_edit works on one of {', '.join(KINDS)}, not {kind!r}.")
    if not ref:
        raise AuthoringRefused("can_edit needs the artifact's name.")
    user = getattr(client, "user_id", None) if client is not None else None
    if not user:
        raise AuthoringRefused("can_edit reads Egeria as you: a signed-in client is needed.")
    try:
        el = await _read(kind, ref, client)
    except AuthoringRefused as exc:
        if getattr(exc, "answer", ANSWER_REFUSED) == ANSWER_UNKNOWN:
            return _answer(UNKNOWN, f"Whether Egeria holds it couldn't be told: {exc}")
        return _answer(UNKNOWN, str(exc))   # e.g. two Reports with that display name
    except Exception as exc:  # noqa: BLE001 -- a failed read is unknown, never "no"
        return _answer(UNKNOWN, f"It couldn't be read ({type(exc).__name__}): nothing is assumed.")

    if el is None:
        if kind == "spec" and _is_builtin_spec(ref):
            return _answer(NO, f"{ref!r} is a built-in spec (pyegeria's own, not in Egeria): copy it to a new "
                               f"draft to change it.")
        return _answer(NO, f"Egeria holds no {kind} {ref!r} that you can see.")

    from pyegeria.view.egeria_spec_cache import _zones
    zones = _zones(el)
    if zones == [user]:
        return _answer(YES, "It's your private draft.")
    versions = _header(el).get("versions") or {}
    if versions.get("createdBy") == user:
        return _answer(YES, "You created it." + (" Editing makes a new draft; publishing it makes a new version."
                                                 if user not in zones else ""))
    owner = _owner(el)
    if owner and owner.get("owner") == user and owner.get("ownerPropertyName") in (None, "", "userId"):
        return _answer(YES, "You own it (Ownership). Editing makes a new draft; publishing it makes a new version.")
    if owner and owner.get("owner") and owner.get("ownerPropertyName") not in (None, "", "userId"):
        return _answer(UNKNOWN, f"Its owner is named by {owner.get('ownerPropertyName')} ({owner.get('owner')!r}), "
                                f"not a user id, so whether that's you isn't read here; Studio checks on open and "
                                f"at publish.")
    return _answer(UNKNOWN, "You didn't create it and Ownership doesn't name you; Egeria exposes no other edit "
                            "rights (e.g. a steward's role), so Studio checks on open and at publish.")


def can_edit(kind: str, ref: str, client: Any) -> Dict[str, str]:
    """Sync form of async_can_edit."""
    from pyegeria.core.async_runner import run_sync
    return run_sync(async_can_edit(kind, ref, client))
