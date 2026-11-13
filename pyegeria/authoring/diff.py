# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""diff(a, b): a structured comparison of two drafts of the same kind.

Areas: field, column, parameter, analytic parameter, placement. **Breaking** (needs confirming before a
promote, design note §1d): a removed column or placement, a changed parameter type, a changed target type.
A changed analytic routine is flagged breaking too: everything that reads the spec's columns depends on it.

A removed placement and a placement reorder are reported, but publishing doesn't apply them to a sheet that
already exists (Dr.Egeria's sheet commands add and update only); their `why` says so.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from pyegeria.authoring.models import AuthoringRefused, Change, Diff, ReportDraft, SheetDraft, SpecDraft, as_draft


NOT_PUBLISHED_REMOVE = ("publishing an update doesn't remove it: the placement stays on the existing sheet "
                        "(Dr.Egeria's sheet commands add and update only)")
NOT_PUBLISHED_ORDER = ("publishing an update doesn't reorder an existing sheet: placements keep their positions "
                       "(Dr.Egeria's sheet commands add and update only)")


def _fields(diff: Diff, a: Any, b: Any, names: List[str], breaking: Tuple[str, ...] = ()) -> None:
    for name in names:
        before, after = getattr(a, name, None), getattr(b, name, None)
        if before != after:
            diff.changes.append(Change(area="field", name=name, change="changed", before=before, after=after,
                                       breaking=name in breaking,
                                       why="the elements it runs over change" if name in breaking else None))


def _columns(fs) -> Dict[str, Dict[str, Any]]:
    """{key: {"name", "formats": [...], ...}} across every format row."""
    out: Dict[str, Dict[str, Any]] = {}
    for fmt in fs.formats or []:
        types = list(getattr(fmt, "types", None) or [])
        for col in getattr(fmt, "attributes", None) or []:
            data = col if isinstance(col, dict) else col.model_dump(exclude_none=True)
            key = data.get("key")
            if not key:
                continue
            entry = out.setdefault(key, {**{k: v for k, v in data.items() if k != "key"}, "formats": []})
            entry["formats"] = sorted(set(entry["formats"]) | set(types))
    return out


def _keyed(diff: Diff, area: str, before: Dict[str, Any], after: Dict[str, Any], *, removed_breaks: bool,
           type_breaks: bool = False) -> None:
    for key in sorted(set(before) | set(after)):
        if key not in after:
            diff.changes.append(Change(area=area, name=key, change="removed", before=before[key],
                                       breaking=removed_breaks,
                                       why=f"anything that reads this {area} loses it" if removed_breaks else None))
        elif key not in before:
            diff.changes.append(Change(area=area, name=key, change="added", after=after[key]))
        elif before[key] != after[key]:
            typed = type_breaks and type(before[key]) is not type(after[key])
            diff.changes.append(Change(area=area, name=key, change="changed", before=before[key], after=after[key],
                                       breaking=typed,
                                       why=f"its type changed ({type(before[key]).__name__} -> "
                                           f"{type(after[key]).__name__})" if typed else None))


def _action(fs) -> Dict[str, Any]:
    action = fs.action
    if action is None:
        return {}
    return action if isinstance(action, dict) else action.model_dump(exclude_none=True)


def diff(a: Any, b: Any) -> Diff:
    a, b = as_draft(a), as_draft(b)
    if a.kind != b.kind:
        raise AuthoringRefused(f"Two drafts of the same kind are compared, not a {a.kind} and a {b.kind}.")
    d = Diff()
    if isinstance(a, SpecDraft):
        _fields(d, a, b, ["label", "qualified_name"])
        _fields(d, a.format_set, b.format_set, ["target_type", "heading", "description", "family", "aliases"],
                breaking=("target_type",))
        _keyed(d, "column", _columns(a.format_set), _columns(b.format_set), removed_breaks=True)
        act_a, act_b = _action(a.format_set), _action(b.format_set)
        for name in ("function", "analytic_function"):
            if act_a.get(name) != act_b.get(name):
                routine = name == "analytic_function"
                d.changes.append(Change(area="field", name=f"action.{name}", change="changed", before=act_a.get(name),
                                        after=act_b.get(name), breaking=routine,
                                        why="a different routine produces different columns" if routine else None))
        params_a = {p: "required" for p in act_a.get("required_params") or []}
        params_a.update({p: "optional" for p in act_a.get("optional_params") or []})
        params_b = {p: "required" for p in act_b.get("required_params") or []}
        params_b.update({p: "optional" for p in act_b.get("optional_params") or []})
        _keyed(d, "parameter", params_a, params_b, removed_breaks=False)
        return d
    if isinstance(a, ReportDraft):
        _fields(d, a, b, ["display_name", "qualified_name", "description", "spec", "output_format", "pinned_version"])
        _keyed(d, "parameter", a.parameters, b.parameters, removed_breaks=False, type_breaks=True)
        _keyed(d, "analytic parameter", a.analytic_params, b.analytic_params, removed_breaks=False, type_breaks=True)
        return d
    _fields(d, a, b, ["name", "heading", "description", "family", "perspectives"])
    pa = {p.name: p.model_dump(exclude={"name"}) for p in a.placements}
    pb = {p.name: p.model_dump(exclude={"name"}) for p in b.placements}
    _keyed(d, "placement", pa, pb, removed_breaks=True)
    for c in d.changes:
        if c.area == "placement" and c.change == "removed":
            c.why = f"{c.why}; but {NOT_PUBLISHED_REMOVE}" if c.why else NOT_PUBLISHED_REMOVE
    order_a = [p.name for p in a.placements if p.name in pb]
    order_b = [p.name for p in b.placements if p.name in pa]
    if order_a != order_b:
        d.changes.append(Change(area="placement", name="(order)", change="changed", before=order_a, after=order_b,
                                why=NOT_PUBLISHED_ORDER))
    return d
