# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Publish a report spec to Egeria, and withdraw it: the shared, app-neutral part.

Lifted from Egeria Advisor's `advisor/egeria_spec_publish.py` (trellis, brief B6) so the Portal and EA
build and check the same documents (BRIEF-SPEC-PUBLISH-STAGED-2026-11-12, stage 1a). This module holds
**no credentials, does no web or app work and touches no cache**: each app supplies

- the spec to publish (a `FormatSet`) and the **consumer folders** it goes to
  (EA: `Consumer::EgeriaAdvisor` +/- `Consumer::Portal`; the Portal: `Consumer::Portal` +/- EA's);
- a **runner**, `run(markdown, directive) -> dict | JSON str`, that runs a Dr.Egeria document **as the
  signed-in user** (EA: `DrEgeriaActionAgent.execute(..., egeria_credentials=...)`; the Portal: its
  in-process Dr.Egeria API with the user's token). This module never authenticates;
- whether restricted publish is proven on its platform (`restricted_publish_status(proof)`), from its
  own setting (EA: `ADVISOR_RESTRICTED_PUBLISH_PROVEN`);
- what "already held in Egeria" means to it (`held_in_egeria(..., shared_tier=, restricted_reader=)`).

**The document.** One `Create Report Spec` (`Update Report Spec` when the label is already held), then
`Add Member to Collection` for each consumer folder. Public carries no zones; restricted carries
`Zone Membership`. A blank Zone Membership on an Update leaves old zones in place (pyegeria 6.2.30), so
re-publishing a restricted spec as public adds `Declassify Zone Membership`.

**Never a Parent ID** on the spec command, Create or Update (a Parent ID on an Update can delete an
unrelated same-type relationship): folder membership is only ever `Add Member to Collection`, which
Egeria checks before it adds (no duplicate membership on a re-publish).

**The steps** are fixed: **preview** (the document, nothing sent), **validate** (Dr.Egeria's validate
run), the user **confirms**, then **process**. The process step is given the digest of the document the
user previewed; the app rebuilds the document and `run_document` refuses if it differs.

**Withdraw** is `Remove Member from Collection` from each folder (the spec element stays in Egeria).

After a successful process, `run_document` returns `after`: what the app must do to its own cache
(`after_publish`); it never syncs anything itself.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

ADVISOR_FOLDER = "ReportSpecFolder::Consumer::EgeriaAdvisor"
PORTAL_FOLDER = "ReportSpecFolder::Consumer::Portal"
#: The consumer folders known today (report-spec consumer folders, phase 1).
CONSUMER_FOLDERS = (ADVISOR_FOLDER, PORTAL_FOLDER)
STEPS = ("preview", "validate", "process")

_ZONE_OK = re.compile(r"[A-Za-z0-9][A-Za-z0-9 _.:-]{0,127}")   # used with fullmatch: no trailing newline
_RULE = re.compile(r"(-{3,}|_{3,}|\*{3,})")

NOT_PROVEN = ("Restricted publish is not yet proven on this platform: Egeria's zone check on report specs has "
              "not been shown live here, so a 'restricted' spec might be visible to everyone. Publish it as "
              "public, or wait for the zone proof.")
CONFIRM_FIRST = "Confirm first: the document runs as you, and writes to Egeria."
CHANGED = ("The document changed since you previewed it (the spec, or what Egeria holds); "
           "preview it again before confirming.")

Runner = Callable[[str, str], Union[Dict[str, Any], str]]


class PublishRefused(ValueError):
    """The request cannot be turned into a document, or run: the words say why."""


# ── Restricted publish gate (D5) ─────────────────────────────────────────────

def restricted_publish_status(proof: Optional[str]) -> Dict[str, Any]:
    """{"enabled", "message", "proof"}. Restricted publish stays off until the live zone proof (a user
    without the zone cannot see a zoned ReportSpec; one with it can) has been captured on the app's
    platform; `proof` is where the app records it (EA reads ADVISOR_RESTRICTED_PUBLISH_PROVEN)."""
    proof = (proof or "").strip()
    if proof:
        return {"enabled": True, "message": None, "proof": proof}
    return {"enabled": False, "message": NOT_PROVEN, "proof": None}


# ── One-line values ───────────────────────────────────────────────────────────

def _one_line(field: str, value: Any) -> str:
    """A value written into the Dr.Egeria document as one attribute line, or PublishRefused.

    Dr.Egeria splits the document with str.splitlines(), which also breaks on U+0085, U+2028, U+2029,
    \\x0b, \\x0c and \\x1c-\\x1e. A value holding any of those could start its own "## Command" or
    "### Zone Membership" line, and a lone rule ("---") or a leading ">" changes how the block is read:
    a restricted spec could be published as public. So: exactly one line, not a rule, not a heading or
    quote."""
    text = str(value)
    if len(text.splitlines()) != 1 or text != text.splitlines()[0]:
        raise PublishRefused(f"{field} must be a single line of text (line breaks of any kind are refused).")
    stripped = text.strip()
    if not stripped:
        raise PublishRefused(f"{field} is empty.")
    if _RULE.fullmatch(stripped) or stripped.startswith((">", "#")):
        raise PublishRefused(f"{field} cannot be a rule ('---') or start with '>' or '#': {stripped[:40]!r}.")
    return stripped


def _list_item(field: str, value: Any) -> str:
    """One entry of a list attribute: one line, and no comma (Dr.Egeria splits lists on commas)."""
    text = _one_line(field, value)
    if "," in text:
        raise PublishRefused(f"{field} cannot contain a comma (it would become two entries): {text[:40]!r}.")
    return text


def _flatten(field: str, value: Any) -> Optional[str]:
    """Free text (a description) folded onto one line: every kind of line break becomes a space."""
    if value in (None, ""):
        return None
    folded = " ".join(str(value).split())
    return _one_line(field, folded) if folded else None


def spec_qualified_name(label: str) -> str:
    return f"ReportSpec::{label}"


def check_label(label: str) -> str:
    if not (label or "").strip():
        raise PublishRefused("A report spec name is needed.")
    return _one_line("The report spec name", label)


def check_zones(visibility: str, zones: Optional[Iterable[Any]], *,
                restricted: Optional[Dict[str, Any]] = None) -> List[str]:
    """The zones a spec is published with: [] for public; the sorted, de-duplicated zone names for
    restricted. `restricted` is the app's `restricted_publish_status(...)`; without it restricted
    publish is not proven, and refused."""
    if visibility not in ("public", "restricted"):
        raise PublishRefused(f"Visibility must be 'public' or 'restricted', not {visibility!r}.")
    cleaned, bad = set(), []
    for z in zones or []:
        if not isinstance(z, str):
            bad.append(repr(z))
        elif _ZONE_OK.fullmatch(z.strip()):
            cleaned.add(z.strip())
        elif z.strip():
            bad.append(repr(z))
    if bad:
        raise PublishRefused(f"Not a zone name (letters, digits, space, _ . : - only, one line): {', '.join(bad)}.")
    out = sorted(cleaned)
    if visibility == "public":
        if out:
            raise PublishRefused("A public spec carries no zones; choose 'Restricted to zones' to set them.")
        return []
    if not out:
        raise PublishRefused("Restricted needs at least one zone.")
    if not (restricted or restricted_publish_status(None))["enabled"]:
        raise PublishRefused(NOT_PROVEN)
    return out


def check_folders(folders: Optional[Iterable[Any]], *, allowed: Optional[Iterable[str]] = None,
                  allowed_words: str = "the configured consumer folders", action: str = "Publish") -> List[str]:
    """The consumer folders, in order, de-duplicated; each one line. With `allowed`, any other is refused."""
    out: List[str] = []
    for f in folders or []:
        name = _list_item("A consumer folder", f)
        if name not in out:
            out.append(name)
    if not out:
        raise PublishRefused(f"{action} needs at least one consumer folder.")
    if allowed is not None:
        allowed = list(allowed)
        bad = [f for f in out if f not in allowed]
        if bad:
            raise PublishRefused(f"{action} works on {allowed_words} only, not {', '.join(bad)}.")
    return out


# ── The spec as document attributes ───────────────────────────────────────────

def microflow_json(fs) -> str:
    """The spec's microflow, as one ASCII line (every non-ASCII character, U+2028 too, is a \\u escape)."""
    from pyegeria.view.microflow import format_set_to_microflow
    try:
        mf = format_set_to_microflow(fs)
    except Exception as exc:  # noqa: BLE001 -- the words go to the user
        raise PublishRefused(f"This spec cannot be written as a microflow: {exc}") from exc
    return _one_line("The microflow", json.dumps(json.loads(mf.to_json()), ensure_ascii=True, separators=(",", ":")))


def output_types(fs) -> List[str]:
    out: List[str] = []
    for fmt in getattr(fs, "formats", None) or []:
        for t in getattr(fmt, "types", None) or []:
            if t and t.upper() not in out:
                out.append(t.upper())
    return out


# ── Held in Egeria? ──────────────────────────────────────────────────────────

def held_in_egeria(label: str, *, shared_tier: Optional[Callable[[str], Any]] = None,
                   restricted_reader: Optional[Callable[[], Dict[str, Any]]] = None,
                   app: str = "this tool") -> Dict[str, Any]:
    """{"held": bool, "zones": [...], "how": words}: whether Egeria already holds `label`, as far as the
    app can tell, and what was and was not read.

    - `shared_tier(label)`: the app's Egeria-held tier lookup (truthy when held, public). Default:
      pyegeria's `egeria_spec_cache.egeria_tier_info`.
    - `restricted_reader()`: the signed-in user's restricted (zoned) specs, `{"specs": [{"label",
      "zones"}, ...]}`. Without one, restricted specs are "not read", and `how` says so.

    Dr.Egeria upserts a Create whose qualified name exists, so a miss here is never a duplicate."""
    tier_note = ""
    try:
        if shared_tier is None:
            from pyegeria.view.egeria_spec_cache import egeria_tier_info as shared_tier
        if shared_tier(label):
            return {"held": True, "zones": [], "how": f"held in Egeria ({app}'s shared tier)"}
    except Exception as exc:  # noqa: BLE001 -- carried into "how"
        tier_note = f"; {app}'s shared tier could not be read ({exc})"
    if restricted_reader is None:
        return {"held": False, "zones": [],
                "how": f"not known: restricted specs not read ({app} reads none){tier_note}"}
    try:
        got = restricted_reader() or {}
    except Exception as exc:  # noqa: BLE001 -- a refused token is the process step's to report
        return {"held": False, "zones": [], "how": f"not known: restricted specs not read ({exc}){tier_note}"}
    for s in got.get("specs") or []:
        if s.get("label") == label:
            return {"held": True, "zones": list(s.get("zones") or []), "how": "held in Egeria, restricted"}
    return {"held": False, "zones": [], "how": f"not held in Egeria as far as {app} can see{tier_note}"}


# ── Documents ─────────────────────────────────────────────────────────────────

def _section(title: str, rows: List[tuple]) -> str:
    lines = [f"## {title}"]
    for name, value in rows:
        if value in (None, "", []):
            continue
        if isinstance(value, list):
            value = ", ".join(value)
        lines += [f"### {name}", str(value)]
    return "\n".join(lines) + "\n\n___\n"


def document_digest(markdown: str) -> str:
    return hashlib.sha256(markdown.encode()).hexdigest()[:16]


def spec_rows(label: str, fs, zones: Optional[List[str]] = None) -> List[tuple]:
    """The `Create/Update Report Spec` attribute rows for `fs` as `label` (never a Parent ID). Shared by
    build_publish_document and pyegeria.authoring's serializer, so both write the same document."""
    label = check_label(label)
    target = getattr(fs, "target_type", None)
    rows = [("Display Name", label), ("Qualified Name", spec_qualified_name(label)),
            ("Description", _flatten("The description", getattr(fs, "description", None))),
            ("Content Status", "ACTIVE"),
            ("Aliases", [_list_item("An alias", a) for a in (getattr(fs, "aliases", None) or [])]),
            ("Target Type Name", _one_line("The target type", target) if target else None),
            ("Output Types", [_list_item("An output type", t) for t in output_types(fs)]),
            ("Microflow", microflow_json(fs))]
    if zones:
        rows.append(("Zone Membership", list(zones)))
    return rows


def section(title: str, rows: List[tuple]) -> str:
    """One Dr.Egeria command block: `## title`, then `### name` / value per non-empty row, then a rule."""
    return _section(title, rows)


def build_publish_document(label: str, fs, *, folders: Iterable[str], visibility: str = "public",
                           zones: Optional[Iterable[str]] = None, held: Optional[Dict[str, Any]] = None,
                           restricted: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The Dr.Egeria document that publishes `fs` as `label` into `folders`, with a plain summary.

    Returns {"label", "qualified_name", "verb", "visibility", "zones", "folders", "markdown", "digest",
    "steps", "held"}; `markdown` is the document and `steps` says in words what it does."""
    label = check_label(label)
    zones = check_zones(visibility, zones, restricted=restricted)
    folders = check_folders(folders)
    held = held or {"held": False, "zones": []}
    verb = "Update" if held.get("held") else "Create"
    qn = spec_qualified_name(label)
    # Never a Parent ID here (Create or Update): membership is the Add Member below.
    doc = [f"# Publish report spec {label}\n", _section(f"{verb} Report Spec", spec_rows(label, fs, zones))]
    steps = [f"{verb} the ReportSpec {qn}" + (f", restricted to zones {', '.join(zones)}" if zones else ", public")]
    if visibility == "public" and held.get("zones"):
        doc.append(_section("Declassify Zone Membership", [("Target Element", qn)]))
        steps.append(f"remove its zones ({', '.join(held['zones'])}): it was restricted, it becomes public")
    for folder in folders:
        doc.append(_section("Add Member to Collection", [("Element Id", qn), ("Collection Id", folder)]))
        steps.append(f"add it to {folder}")
    markdown = "\n".join(doc)
    return {"label": label, "qualified_name": qn, "verb": verb, "visibility": visibility, "zones": zones,
            "folders": folders, "markdown": markdown, "digest": document_digest(markdown), "steps": steps,
            "held": held}


def build_withdraw_document(label: str, folders: Iterable[str], *, allowed: Optional[Iterable[str]] = None,
                            allowed_words: str = "the configured consumer folders") -> Dict[str, Any]:
    """`Remove Member from Collection` for each folder; the spec element itself stays in Egeria."""
    label = check_label(label)
    qn = spec_qualified_name(label)
    folders = check_folders(folders, allowed=allowed, allowed_words=allowed_words, action="Withdraw")
    doc = [f"# Withdraw report spec {label}\n"]
    doc += [_section("Remove Member from Collection", [("Element Id", qn), ("Collection Id", f)]) for f in folders]
    markdown = "\n".join(doc)
    return {"label": label, "qualified_name": qn, "folders": folders, "markdown": markdown,
            "digest": document_digest(markdown),
            "steps": [f"remove {qn} from {f} (the spec element itself stays in Egeria)" for f in folders]}


def check_unchanged(previewed_digest: Optional[str], plan: Union[Dict[str, Any], str]) -> None:
    """Refuse when the rebuilt document (a plan or its markdown) is not the one the user previewed."""
    current = plan["digest"] if isinstance(plan, dict) else document_digest(plan)
    if previewed_digest != current:
        raise PublishRefused(CHANGED)


# ── Running it ────────────────────────────────────────────────────────────────

_SUMMARY_KEYS = ("success", "output", "validation_errors", "execution_errors", "commands_total",
                 "commands_succeeded", "commands_failed", "commands_detail", "auth_required", "auth_reason")


def summarise(env: Dict[str, Any]) -> Dict[str, Any]:
    """The parts of a Dr.Egeria run result a user is shown."""
    return {k: env.get(k) for k in _SUMMARY_KEYS if k in env}


def _call(run: Runner, markdown: str, directive: str) -> Dict[str, Any]:
    raw = run(markdown, directive)
    if isinstance(raw, dict):
        return raw
    try:
        out = json.loads(raw)
    except (TypeError, ValueError):
        out = None
    if isinstance(out, dict):
        return out
    return {"success": False, "output": str(raw), "execution_errors": [{"message": "unreadable result"}]}


def after_publish(plan: Dict[str, Any]) -> Dict[str, Any]:
    """What the app must do after a successful process: drop its cached copy and per-user listings of
    the label, and sync its Egeria-held specs, so the catalog and "Used by" show the change. Each app
    owns its cache; this only says what to do."""
    return {"invalidate": [plan["label"]], "sync": True,
            "why": f"{plan['qualified_name']} changed in Egeria; refresh this app's copy of its report specs."}


def run_document(plan: Dict[str, Any], *, step: str, run: Optional[Runner] = None, confirmed: bool = False,
                 digest: Optional[str] = None) -> Dict[str, Any]:
    """One step of a publish or withdraw `plan` (from build_publish_document / build_withdraw_document).

    - preview: the plan; nothing runs.
    - validate: `run(markdown, "validate")`.
    - process: refused unless `confirmed`, and unless `digest` is the previewed plan's (the app rebuilt
      the plan from the current spec and Egeria state); then `run(markdown, "process")`, and on success
      `after` (after_publish) for the app to act on.

    `run` is the app's: it runs the document as the signed-in user and returns Dr.Egeria's result (a
    dict, or its JSON text)."""
    if step not in STEPS:
        raise PublishRefused(f"Step must be one of {', '.join(STEPS)}, not {step!r}.")
    if step == "preview":
        return {**plan, "step": "preview", "result": None}
    if run is None:
        raise PublishRefused(f"The {step} step needs a runner (the app runs the document as the signed-in user).")
    if step == "validate":
        return {**plan, "step": "validate", "result": summarise(_call(run, plan["markdown"], "validate"))}
    if not confirmed:
        raise PublishRefused(CONFIRM_FIRST)
    check_unchanged(digest, plan)
    env = _call(run, plan["markdown"], "process")
    out = {**plan, "step": "process", "result": summarise(env)}
    if env.get("success"):
        out["after"] = after_publish(plan)
    return out


__all__ = ["ADVISOR_FOLDER", "PORTAL_FOLDER", "CONSUMER_FOLDERS", "STEPS", "NOT_PROVEN", "PublishRefused",
           "restricted_publish_status", "spec_qualified_name", "check_label", "check_zones", "check_folders",
           "microflow_json", "output_types", "held_in_egeria", "spec_rows", "section", "build_publish_document",
           "build_withdraw_document", "document_digest", "check_unchanged", "summarise", "after_publish",
           "run_document"]
