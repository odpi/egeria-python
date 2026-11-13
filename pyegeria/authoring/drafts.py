# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Making drafts, and keeping them (D16).

- `new_draft(kind, **fields)`: a new draft of a kind.
- `new_from(prototype=(kind, label) | template=name, new_label=...)`: a copy of an existing artifact (or a
  template), renamed, with `derived_from` recorded. A spec prototype is read from pyegeria's registry (read
  only, nothing registered); a held Report or sheet is read from Egeria as the caller (`client`).
- `DraftStore`: where drafts are kept (D16, decided: Egeria, private, 30-day prune). `EgeriaDraftStore`, the
  default for apps, keeps the draft as the element itself in the author's private zone; `LocalDraftStore`
  (a directory per user, given by the caller) is for tests and offline use.
"""
from __future__ import annotations

import copy
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple, Union

from pyegeria.authoring.models import (
    KINDS, AuthoringRefused, ReportDraft, SheetDraft, SheetPlacement, SpecDraft, as_draft, draft_key,
)
from pyegeria.view._output_format_models import Column, Format, FormatSet

AnyDraft = Union[SpecDraft, ReportDraft, SheetDraft]


def new_draft(kind: str, **fields: Any) -> AnyDraft:
    """A new draft of `kind` ("spec", "report" or "sheet") from its fields. A spec takes `label` and
    `format_set` (a FormatSet or its dict)."""
    if kind not in KINDS:
        raise AuthoringRefused(f"A draft is one of {', '.join(KINDS)}, not {kind!r}.")
    return as_draft({"kind": kind, **fields})


# ── Templates (the built-in tier: blanks with guidance) ──────────────────────

def _template_spec(label: str) -> SpecDraft:
    fs = FormatSet(target_type="Referenceable", heading=label, description="Describe what this report answers.",
                   formats=[Format(types=["ALL"], attributes=[
                       Column(name="Display Name", key="display_name"),
                       Column(name="Qualified Name", key="qualified_name"),
                       Column(name="Description", key="description")])],
                   action={"function": "ClassificationExplorer.find_elements_by_property_value",
                           "required_params": ["search_string"], "optional_params": ["page_size"],
                           "spec_params": {}})
    return SpecDraft(label=label, format_set=fs)


TEMPLATES: Dict[str, Tuple[str, Any]] = {
    "find-spec": ("spec", _template_spec),
    "report": ("report", lambda label: ReportDraft(display_name=label, spec="Referenceable", output_format="TABLE",
                                                   parameters={"search_string": "*", "page_size": 25})),
    "sheet": ("sheet", lambda label: SheetDraft(name=label, heading=label, placements=[
        SheetPlacement(text="**What this sheet shows**\n\nDescribe the sheet here.", name="About this sheet",
                       span="full", emphasis="panel")])),
}


def _rename(draft: AnyDraft, new_label: str) -> AnyDraft:
    if isinstance(draft, SpecDraft):
        fs = draft.format_set.model_copy(deep=True)
        fs.aliases = []   # an alias of the prototype would make two specs answer to one name
        return SpecDraft(label=new_label, format_set=fs)
    if isinstance(draft, ReportDraft):
        data = draft.model_dump(exclude={"qualified_name", "guid", "base_version", "derived_from"})
        return ReportDraft(**{**data, "display_name": new_label})
    data = draft.model_dump(exclude={"guid", "base_version", "derived_from"})
    return SheetDraft(**{**data, "name": new_label, "heading": new_label})


def _spec_from_registry(label: str) -> SpecDraft:
    from pyegeria.view.base_report_formats import lookup_report_spec
    fs, _tier, found = lookup_report_spec(label)
    if fs is None:
        raise AuthoringRefused(f"No report spec named {label!r} is known here to copy (pyegeria's registry, "
                               f"its Egeria-held and local tiers).")
    return SpecDraft(label=found or label, format_set=fs.model_copy(deep=True))


async def async_new_from(*, prototype: Optional[Tuple[str, str]] = None, template: Optional[str] = None,
                         new_label: str, client: Any = None) -> AnyDraft:
    """A copy of a prototype `(kind, label)` or a template, named `new_label`, with `derived_from` recorded.
    A held Report or sheet prototype is read from Egeria as the caller (`client`)."""
    if (prototype is None) == (template is None):
        raise AuthoringRefused("Give one of prototype=(kind, label) or template=name.")
    if not (new_label or "").strip():
        raise AuthoringRefused("A new draft needs a new name (new_label).")
    if template is not None:
        if template not in TEMPLATES:
            raise AuthoringRefused(f"No template {template!r}; the templates are {', '.join(sorted(TEMPLATES))}.")
        draft = TEMPLATES[template][1](new_label)
        draft.derived_from = f"template:{template}"
        return draft
    kind, label = prototype
    if kind == "spec":
        source = _spec_from_registry(label)
    elif kind in ("report", "sheet"):
        if client is None:
            raise AuthoringRefused(f"Copying a held {kind} reads it from Egeria as you: a client is needed.")
        from pyegeria.authoring.lifecycle import async_load_held
        source = await async_load_held(kind, label, client)
    else:
        raise AuthoringRefused(f"A prototype is one of {', '.join(KINDS)}, not {kind!r}.")
    if draft_key(source) == new_label:
        raise AuthoringRefused(f"The copy needs a name of its own: {new_label!r} is the prototype's.")
    draft = _rename(source, new_label)
    draft.derived_from = f"prototype:{kind}:{label}"
    return draft


def new_from(*, prototype: Optional[Tuple[str, str]] = None, template: Optional[str] = None, new_label: str,
             client: Any = None) -> AnyDraft:
    from pyegeria.core.async_runner import run_sync
    return run_sync(async_new_from(prototype=prototype, template=template, new_label=new_label, client=client))


# ── Draft storage (D16) ───────────────────────────────────────────────────────

class DraftStore(Protocol):
    """Where a user's drafts are kept. Every call names the user: a draft is personal (§1b tier 1)."""
    def save(self, user_id: str, draft: AnyDraft) -> str: ...
    def load(self, user_id: str, kind: str, name: str) -> Optional[AnyDraft]: ...
    def list(self, user_id: str, kind: Optional[str] = None) -> List[Dict[str, str]]: ...
    def delete(self, user_id: str, kind: str, name: str) -> bool: ...


_USER_OK = re.compile(r"[A-Za-z0-9][A-Za-z0-9._@-]{0,127}")


def _slug(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-.")[:120]
    if not slug:
        raise AuthoringRefused(f"Can't make a file name from {name!r}.")
    return slug


class LocalDraftStore:
    """Drafts as JSON files: `<root>/<user>/<kind>/<slug>.json`. The caller chooses `root` (the API never
    picks a shared default) and passes the user id it signed in; a user id that isn't a plain name is
    refused, so one user can't reach another's directory."""

    def __init__(self, root: Union[str, Path]):
        self.root = Path(root).expanduser()

    def _dir(self, user_id: str, kind: str) -> Path:
        if not _USER_OK.fullmatch(user_id or ""):
            raise AuthoringRefused(f"Not a user id this store accepts: {user_id!r}.")
        if kind not in KINDS:
            raise AuthoringRefused(f"A draft is one of {', '.join(KINDS)}, not {kind!r}.")
        return self.root / user_id / kind

    def _path(self, user_id: str, kind: str, name: str) -> Path:
        return self._dir(user_id, kind) / f"{_slug(name)}.json"

    def save(self, user_id: str, draft: AnyDraft) -> str:
        draft = as_draft(draft)
        path = self._path(user_id, draft.kind, draft_key(draft))
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps({"name": draft_key(draft), "draft": draft.model_dump(mode="json")},
                                  indent=2, sort_keys=True))
        os.replace(tmp, path)
        return str(path)

    def load(self, user_id: str, kind: str, name: str) -> Optional[AnyDraft]:
        path = self._path(user_id, kind, name)
        if not path.is_file():
            return None
        return as_draft(json.loads(path.read_text())["draft"])

    def list(self, user_id: str, kind: Optional[str] = None) -> List[Dict[str, str]]:
        out = []
        for k in ([kind] if kind else list(KINDS)):
            d = self._dir(user_id, k)
            for f in sorted(d.glob("*.json")) if d.is_dir() else []:
                try:
                    out.append({"kind": k, "name": json.loads(f.read_text())["name"]})
                except (OSError, ValueError, KeyError):
                    out.append({"kind": k, "name": f.stem, "note": "unreadable draft file"})
        return out

    def delete(self, user_id: str, kind: str, name: str) -> bool:
        path = self._path(user_id, kind, name)
        if path.is_file():
            path.unlink()
            return True
        return False


_ELEMENT_TYPE = {"spec": "ReportSpec", "report": "Report", "sheet": "Dashboard"}
PRUNE_DAYS = 30
#: The draft marker on a Report (additionalProperties); a spec carries contentStatus DRAFT instead.
DRAFT_MARKER = ("authoringState", "draft")


def _parse_time(value: Any):
    from datetime import datetime, timezone
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000 if value > 1e11 else value, tz=timezone.utc)
    text = str(value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _is_marked(kind: str, el: Dict[str, Any]) -> bool:
    """Whether an element carries the draft marker (a sheet has none: its zone alone says it's a draft)."""
    props = el.get("properties") or {}
    if kind == "spec":
        return str(props.get("contentStatus") or "").upper() == "DRAFT"
    if kind == "report":
        return (props.get("additionalProperties") or {}).get(DRAFT_MARKER[0]) == DRAFT_MARKER[1]
    return True


class EgeriaDraftStore:
    """Drafts held in Egeria, zoned private to their author (D16, decided "Egeria, private, 30-day prune").

    - **The draft is the element itself** (a ReportSpec, a Report, a Dashboard sheet chain) with its real
      qualified name, zoned `[<author's userId>]` and nothing else (ANSWER-DRAFT-PRIVATE-ZONE-2026-11-13,
      code-verified on the build laz runs): Egeria's validateZoneAccess grants a zone named for a user to that
      user only, and the search pushdown leaves other users' drafts out of their searches. No marker zone: a
      control defined for it later would expose every user's drafts. The anchor is zoned (the Dashboard,
      ReportSpec or Report); its children inherit through Anchors.
    - **Marked as a draft on the element:** a spec with contentStatus DRAFT, a Report with additionalProperties
      `authoringState: draft`. A sheet has no carrier Dr.Egeria writes yet (Create Dashboard Sheet sets the
      Dashboard's own additionalProperties), so a sheet draft is known by its zone alone.
    - **A userId that names a governance zone is refused** (that user would read the zone's elements), as is
      one in `controlled_zones` (zones the app knows carry a security control).
    - **Written as the author:** every write is a Dr.Egeria document run through the caller's runner (`run`),
      and the client must be signed in as the user whose draft it is.
    - **Never over a published element:** saving a draft whose element is already held outside the author's
      private zone is refused (it would change what others see); make a copy with new_from, or promote.
    - **Never filed into a consumer folder:** a saved draft is only its element. Promotion files it.
    - **Promotion clears the zone:** promotion_plan() is the publish plan with Declassify Zone Membership (a
      blank Zone Membership would keep the zone), marking the element ACTIVE / published. After promoting a
      sheet, check that another user's search finds its placements, not only the sheet (anchor zones).
    - **prune_drafts(older_than_days=30)** removes the author's unpromoted drafts created more than 30 days
      ago, as the author. It can't see, and never sweeps, anyone else's drafts.
    """

    def __init__(self, client: Any, run: Any = None, *, controlled_zones: Any = ()):
        self.client = client
        self.run = run
        self.controlled_zones = set(controlled_zones or ())
        self._zone_checked: Dict[str, bool] = {}

    # ---------------------------------------------------------------- helpers

    @staticmethod
    def zone(user_id: str) -> str:
        """The author's private zone: their user id."""
        return user_id

    async def _check_zone_name(self, user_id: str) -> None:
        """Refuse a user id that is also a governance zone's name (or one the app says is controlled)."""
        if self._zone_checked.get(user_id):
            return
        if user_id in self.controlled_zones:
            raise AuthoringRefused(f"User id {user_id!r} is also the name of a controlled zone, so a draft zoned "
                                   f"[{user_id}] wouldn't be private. Drafts can't be kept in Egeria for this user.")
        try:
            found = await self.client.classification_manager._async_get_elements_by_property_value(
                user_id, ["zoneName", "qualifiedName"], metadata_element_type="GovernanceZone", starts_with=False,
                ends_with=False, ignore_case=False, page_size=10, graph_query_depth=0)
        except Exception:  # noqa: BLE001 -- "not found" answers are exceptions on some paths
            found = []
        names = {((e.get("properties") or {}).get("zoneName") or "") for e in found
                 if isinstance(e, dict)} if isinstance(found, list) else set()
        if user_id in names:
            raise AuthoringRefused(f"User id {user_id!r} is also the name of a governance zone, so a draft zoned "
                                   f"[{user_id}] wouldn't be private. Drafts can't be kept in Egeria for this user.")
        self._zone_checked[user_id] = True

    def _author(self, user_id: str) -> str:
        signed_in = getattr(self.client, "user_id", None)
        if not user_id or user_id != signed_in:
            raise AuthoringRefused(f"Drafts are written and read as their author: this client is signed in as "
                                   f"{signed_in!r}, not {user_id!r}.")
        return self.zone(user_id)

    async def _element(self, kind: str, name: str) -> Optional[Dict[str, Any]]:
        from pyegeria.authoring.lifecycle import _by_qualified_name, _report_element
        if kind == "spec":
            from md_processing.v2.report import find_report_spec_element
            return await find_report_spec_element(self.client, name)
        if kind == "report":
            return await _report_element(self.client, name)
        return await _by_qualified_name(self.client, f"Dashboard::{name}")

    @staticmethod
    def _zones(el: Dict[str, Any]) -> List[str]:
        from pyegeria.view.egeria_spec_cache import _zones
        return _zones(el)

    # ---------------------------------------------------------------- the store

    async def async_save(self, user_id: str, draft: AnyDraft) -> str:
        """Create or update the draft's element in the author's private zone. Returns its qualified name."""
        from pyegeria.authoring.serialize import serialize
        from pyegeria.view.report_spec_publish import _call
        zone = self._author(user_id)
        draft = as_draft(draft)
        if self.run is None:
            raise AuthoringRefused("Saving a draft to Egeria runs a document as you: a runner is needed.")
        await self._check_zone_name(user_id)
        held = await self._element(draft.kind, draft_key(draft))
        if held is not None and zone not in self._zones(held):
            raise AuthoringRefused(f"{draft.kind} {draft_key(draft)!r} is already held in Egeria outside your private "
                                   f"draft zone ({', '.join(self._zones(held)) or 'public'}): saving the draft there "
                                   f"would change what others see. Copy it with new_from, or promote the draft.")
        env = _call(self.run, serialize(draft, zones=[zone], as_draft_element=True), "process")
        if not env.get("success"):
            words = "; ".join(str(e.get("message", e)) if isinstance(e, dict) else str(e)
                              for e in (env.get("execution_errors") or env.get("validation_errors") or [])[:3])
            raise AuthoringRefused(f"The draft was not saved: {words or 'Dr.Egeria did not succeed'}.")
        if isinstance(draft, SpecDraft):
            return draft.qualified_name
        if isinstance(draft, SheetDraft):
            return f"Dashboard::{draft.name}"
        return draft.qualified_name or draft.display_name

    async def async_load(self, user_id: str, kind: str, name: str) -> Optional[AnyDraft]:
        """The author's draft `name`, or None when no element by that name is in their private zone."""
        from pyegeria.authoring.lifecycle import async_load_held
        zone = self._author(user_id)
        el = await self._element(kind, name)
        if el is None or zone not in self._zones(el):
            return None
        return await async_load_held(kind, name, self.client)

    async def async_list(self, user_id: str, kind: Optional[str] = None) -> List[Dict[str, Any]]:
        """The author's drafts: every ReportSpec, Report and Dashboard in their private zone, read as them."""
        zone = self._author(user_id)
        out: List[Dict[str, Any]] = []
        for k in ([kind] if kind else list(KINDS)):
            start = 0
            while True:
                page = await self.client.classification_manager._async_find_elements_by_property_value(
                    ".*", ["qualifiedName"], metadata_element_type=_ELEMENT_TYPE[k], starts_with=False,
                    governance_zone_filter=[zone], graph_query_depth=0, start_from=start, page_size=50)
                raw = [e for e in page if isinstance(e, dict) and e.get("elementHeader")] if isinstance(page, list) else []
                if not raw:   # only an empty page ends the read (a short page isn't the last page)
                    break
                start += len(raw)
                for el in (e for e in raw if zone in self._zones(e)):
                    props = el.get("properties") or {}
                    versions = (el.get("elementHeader") or {}).get("versions") or {}
                    name = props.get("displayName") or props.get("qualifiedName")
                    if k == "sheet" and str(props.get("qualifiedName", "")).startswith("Dashboard::"):
                        name = props["qualifiedName"].split("::", 1)[1]
                    out.append({"kind": k, "name": name, "qualified_name": props.get("qualifiedName"),
                                "guid": el["elementHeader"].get("guid"),
                                "created": versions.get("createTime"), "updated": versions.get("updateTime"),
                                "marked": _is_marked(k, el)})
        return out

    async def async_delete(self, user_id: str, kind: str, name: str) -> bool:
        """Delete the author's draft (only an element in their private zone), as the author."""
        zone = self._author(user_id)
        el = await self._element(kind, name)
        if el is None or zone not in self._zones(el):
            return False
        guid = el["elementHeader"]["guid"]
        if kind == "sheet":
            from md_processing.v2.dashboard_sheet import DashboardSheetEgeriaWriter
            return bool(await DashboardSheetEgeriaWriter(self.client).delete_sheet(name))
        if kind == "report":
            await self.client.asset_maker._async_delete_asset(guid)
        else:
            await self.client.metadata_expert._async_delete_metadata_element(guid)
        return True

    async def async_prune_drafts(self, user_id: str, older_than_days: int = PRUNE_DAYS, *,
                                 dry_run: bool = False) -> Dict[str, Any]:
        """Remove the author's drafts created more than `older_than_days` ago (a promoted draft is no longer in
        the private zone, so it's never pruned). Run as the author only."""
        from datetime import datetime, timedelta, timezone
        cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
        drafts = await self.async_list(user_id)
        out: Dict[str, Any] = {"removed": [], "kept": [], "not_dated": [], "not_marked": [], "dry_run": dry_run,
                               "older_than_days": older_than_days}
        for d in drafts:
            when = _parse_time(d.get("created"))
            if not d.get("marked", True):
                out["not_marked"].append(d["name"])   # in the zone without the draft marker: never removed
            elif when is None:
                out["not_dated"].append(d["name"])   # never removed on a guess
            elif when < cutoff:
                if not dry_run:
                    await self.async_delete(user_id, d["kind"], d["name"])
                out["removed"].append(f"{d['kind']}:{d['name']}")
            else:
                out["kept"].append(f"{d['kind']}:{d['name']}")
        return out

    async def async_promotion_plan(self, user_id: str, kind: str, name: str, *, folders: Any = ()) -> Dict[str, Any]:
        """The publish plan for the author's draft: it clears the private zone and files it in `folders`."""
        from pyegeria.authoring.lifecycle import publish_plan
        draft = await self.async_load(user_id, kind, name)
        if draft is None:
            raise AuthoringRefused(f"You have no {kind} draft named {name!r} in your private zone.")
        return publish_plan(draft, folders=folders, held={"held": True, "zones": [self.zone(user_id)]})

    # ---------------------------------------------------------------- sync forms (DraftStore)

    def _sync(self, coro):
        from pyegeria.core.async_runner import run_sync
        return run_sync(coro)

    def save(self, user_id: str, draft: AnyDraft) -> str:
        return self._sync(self.async_save(user_id, draft))

    def load(self, user_id: str, kind: str, name: str) -> Optional[AnyDraft]:
        return self._sync(self.async_load(user_id, kind, name))

    def list(self, user_id: str, kind: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._sync(self.async_list(user_id, kind))

    def delete(self, user_id: str, kind: str, name: str) -> bool:
        return self._sync(self.async_delete(user_id, kind, name))

    def prune_drafts(self, user_id: str, older_than_days: int = PRUNE_DAYS, *, dry_run: bool = False) -> Dict[str, Any]:
        return self._sync(self.async_prune_drafts(user_id, older_than_days, dry_run=dry_run))

    def promotion_plan(self, user_id: str, kind: str, name: str, *, folders: Any = ()) -> Dict[str, Any]:
        return self._sync(self.async_promotion_plan(user_id, kind, name, folders=folders))


def draft_store(backend: str = "egeria", **kwargs: Any) -> DraftStore:
    """The store for a backend: "egeria" (the default for apps: client=, run=) or "local" (root=)."""
    if backend == "local":
        if not kwargs.get("root"):
            raise AuthoringRefused("The local draft store needs a directory (root) from the caller.")
        return LocalDraftStore(kwargs["root"])
    if backend == "egeria":
        return EgeriaDraftStore(kwargs.get("client"), kwargs.get("run"),
                                controlled_zones=kwargs.get("controlled_zones", ()))
    raise AuthoringRefused(f"No draft store {backend!r}; there are 'egeria' and 'local'.")
