# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Drafts as Dr.Egeria markdown: deterministic, never a Parent ID, every Report parameter explicit.

- A spec is the `Create Report Spec` block `report_spec_publish` writes (the same rows, so the same bytes).
- A Report is one `Create Report` block. Every parameter the draft holds is written out: the common find
  parameters as their own attributes (`Search String`, `Page Size`, ...), any other parameter in `Report
  Parameters`, an analytic routine's in `Analytic Parameters`. A document that writes only some keys was how
  the CDO Report nearly lost its search keys (2026-11-12); 6.2.41 merges on update, and this keeps the
  document whole as well.
- A sheet is `Create Dashboard Sheet`, then one `Link Report to Dashboard Sheet` or `Add Text on Dashboard
  Sheet` per placement, in order.

Membership in a consumer folder is never a Parent ID: it's `Add Member to Collection` (publish_plan), which
Egeria checks before it adds.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from pyegeria.authoring.models import AuthoringRefused, ReportDraft, SheetDraft, SpecDraft, as_draft
from pyegeria.view.report_spec_publish import PublishRefused, _flatten, _list_item, _one_line, section, spec_rows

#: The common find parameters Create Report carries as attributes: snake_case name -> (attribute, style).
#: The same 20 as md_processing.v2.report._REPORT_PARAM_ATTRS, less Report Spec / Output Format.
FIND_PARAMETERS: Dict[str, Tuple[str, str]] = {
    "search_string": ("Search String", "text"),
    "starts_with": ("Starts With", "bool"),
    "ends_with": ("Ends With", "bool"),
    "ignore_case": ("Ignore Case", "bool"),
    # A Valid Value attribute, not a list attribute: written as a JSON list, so reportParameters holds a real
    # list. The executor reads "ACTIVE", "['ACTIVE']" and '["ACTIVE"]' alike (_normalize_report_params).
    "limit_result_by_status": ("Limit Result by Status", "jsonlist"),
    "metadata_element_type_name": ("Metadata Element Type Name", "text"),
    "metadata_element_subtype_names": ("Metadata Element Subtype Names", "list"),
    "skip_relationships": ("Skip Relationships", "list"),
    "include_only_relationships": ("Include Only Relationships", "list"),
    "skip_classified_elements": ("Skip Classified Elements", "list"),
    "include_only_classified_elements": ("Include Only Classified Elements", "list"),
    "governance_zone_filter": ("Governance Zone Filter", "list"),
    "graph_query_depth": ("Graph Query Depth", "int"),
    "effective_time": ("Effective Time", "text"),
    "as_of_time": ("AsOfTime", "text"),
    "output_sort_order": ("Output Sort Order", "text"),
    "order_property_name": ("Order Property Name", "text"),
    "page_size": ("Page Size", "int"),
    "start_from": ("Start From", "int"),
    "anchor_scope_id": ("Anchor Scope ID", "text"),
}

SPEC_FOLDER_PREFIX = "ReportSpecFolder::Consumer::"
DASHBOARD_FOLDER_PREFIX = "DashboardFolder::Consumer::"


def _refuse(exc: PublishRefused) -> AuthoringRefused:
    return AuthoringRefused(str(exc))


def _scalar(field: str, value: Any, style: str) -> str:
    if style == "bool":
        if isinstance(value, str) and value.strip().lower() in ("true", "false"):
            value = value.strip().lower() == "true"
        if not isinstance(value, bool):
            raise AuthoringRefused(f"{field} must be true or false, not {value!r}.")
        return "True" if value else "False"
    if style == "int":
        if isinstance(value, bool) or not isinstance(value, (int, str)) or not str(value).strip().lstrip("-").isdigit():
            raise AuthoringRefused(f"{field} must be a whole number, not {value!r}.")
        return str(int(value))
    if style == "jsonlist":
        items = value if isinstance(value, (list, tuple)) else [value]
        return _one_line(field, json.dumps([str(_list_item(f"An entry of {field}", v)) for v in items]))
    if style == "list":
        items = value if isinstance(value, (list, tuple)) else [value]
        return ", ".join(_list_item(f"An entry of {field}", v) for v in items)
    return _one_line(field, value if isinstance(value, str) else json.dumps(value))


def _map_lines(field: str, values: Dict[str, Any]) -> Optional[str]:
    """A Dr.Egeria Dictionary value: one `key: value` line per entry, sorted. A value that isn't a string is
    written as JSON (Create Report decodes it back to its type)."""
    lines = []
    for key in sorted(values):
        value = values[key]
        if value is None:
            continue
        k = _one_line(f"A {field} name", key)
        if ":" in k:
            raise AuthoringRefused(f"A {field} name cannot contain ':': {k!r}.")
        v = value if isinstance(value, str) else json.dumps(value, sort_keys=True)
        lines.append(f"{k}: {_one_line(f'The {field} value of {k}', v)}")
    return "\n".join(lines) or None


#: The additionalProperties key a Report carries its pinned spec version under (D14).
PINNED_VERSION_KEY = "reportSpecVersion"


def report_rows(draft: ReportDraft, zones: Optional[List[str]] = None) -> List[tuple]:
    """The Create Report rows, every parameter explicit. A pinned spec version (D14) is written as the
    additionalProperties key `reportSpecVersion`."""
    rows: List[tuple] = [("Display Name", _one_line("The Report name", draft.display_name))]
    if draft.qualified_name:
        rows.append(("Qualified Name", _one_line("The Report qualified name", draft.qualified_name)))
    rows += [("Description", _flatten("The description", draft.description)),
             ("Report Spec", _one_line("The report spec", draft.spec)),
             ("Output Format", _one_line("The output format", str(draft.output_format).upper()))]
    other: Dict[str, Any] = {}
    for name in sorted(draft.parameters):
        value = draft.parameters[name]
        if name in FIND_PARAMETERS:
            attribute, style = FIND_PARAMETERS[name]
            if value is None:
                continue
            rows.append((attribute, _scalar(attribute, value, style)))
        else:
            other[name] = value
    rows.append(("Report Parameters", _map_lines("Report Parameter", other)))
    rows.append(("Analytic Parameters", _map_lines("Analytic Parameter", draft.analytic_params)))
    if draft.pinned_version is not None:
        if isinstance(draft.pinned_version, bool) or not isinstance(draft.pinned_version, int) or draft.pinned_version < 1:
            raise AuthoringRefused(f"A pinned version is a whole number from 1, not {draft.pinned_version!r}.")
        rows.append(("Additional Properties", f"{PINNED_VERSION_KEY}: {draft.pinned_version}"))
    if zones:
        rows.append(("Zone Membership", [_list_item("A zone", z) for z in zones]))
    return rows


def report_section(draft: ReportDraft, zones: Optional[List[str]] = None) -> str:
    return section("Create Report", report_rows(draft, zones))


def _content(field: str, text: str) -> str:
    """Markdown held on a text placement: many lines, but none Dr.Egeria would read as a new block."""
    out = []
    for line in str(text).splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            raise AuthoringRefused(f"{field}: a line starting with '#' would start a new Dr.Egeria block "
                                   f"({stripped[:40]!r}); use **bold** for a heading inside a placement.")
        if stripped and set(stripped) <= set("-_*") and len(stripped) >= 3:
            raise AuthoringRefused(f"{field}: a rule line ({stripped!r}) would end the Dr.Egeria block.")
        out.append(line.rstrip())
    while out and not out[-1]:
        out.pop()
    if not any(out):
        raise AuthoringRefused(f"{field} is empty.")
    return "\n".join(out)


def sheet_sections(draft: SheetDraft, zones: Optional[List[str]] = None) -> List[str]:
    name = _one_line("The sheet name", draft.name)
    blocks = [section("Create Dashboard Sheet", [
        ("Display Name", name),
        ("Dashboard Sheet Heading", _one_line("The sheet heading", draft.heading)),
        ("Dashboard Sheet Description", _flatten("The sheet description", draft.description)),
        ("Dashboard Sheet Family", _one_line("The sheet family", draft.family) if draft.family else None),
        ("Zone Membership", [_list_item("A zone", z) for z in zones or []])])]
    for i, p in enumerate(draft.placements, start=1):
        common = [("Placement Span", p.span), ("Placement Emphasis", p.emphasis),
                  ("Placement Perspectives", [_list_item(f"A perspective of placement {i}", x) for x in p.perspectives])]
        if p.report is not None:
            blocks.append(section("Link Report to Dashboard Sheet", [
                ("Dashboard Sheet Name", name), ("Report Name", _one_line(f"Placement {i}'s Report", p.report)),
                *common,
                ("Placement Detail Spec", _one_line(f"Placement {i}'s detail spec", p.detail_spec)
                 if p.detail_spec else None)]))
        else:
            blocks.append(section("Add Text on Dashboard Sheet", [
                ("Dashboard Sheet Name", name), ("Placement Name", _one_line(f"Placement {i}'s name", p.name)),
                ("MD Content", _content(f"Placement {i}'s text", p.text)), *common]))
    return blocks


def serialize(draft: Union[SpecDraft, ReportDraft, SheetDraft, Dict[str, Any]], *,
              title: Optional[str] = None, zones: Optional[Iterable[str]] = None) -> str:
    """The draft as one deterministic Dr.Egeria document (Create blocks only: Dr.Egeria upserts a Create
    whose element exists, so the same document creates or updates). Raises AuthoringRefused with words for
    a value that can't be written safely (a line break, a rule, a heading). `zones` puts the element in those
    zones (a draft saved private to its author, D16)."""
    draft = as_draft(draft)
    zones = sorted(set(zones or []))
    try:
        if isinstance(draft, SpecDraft):
            head = title or f"# Report spec {draft.label}"
            body = [section("Create Report Spec", spec_rows(draft.label, draft.format_set, zones))]
        elif isinstance(draft, ReportDraft):
            head = title or f"# Report {draft.display_name}"
            body = [report_section(draft, zones)]
        else:
            head = title or f"# Dashboard sheet {draft.name}"
            body = sheet_sections(draft, zones)
    except PublishRefused as exc:
        raise _refuse(exc) from exc
    return "\n".join([f"{head}\n", *body])


def report_parameter_maps(draft: ReportDraft, *, camel_copy: bool = True) -> Dict[str, Any]:
    """What a Report's parameters become on the element (D7): `reportParameters`, the typed JSON document,
    and, unless `camel_copy` is off, the camelCase `additionalProperties` keys today's readers use. Computed
    by Dr.Egeria's own Report functions from the serialized document's attributes, so it's what processing
    writes, not a second implementation."""
    from md_processing.v2.report import _report_additional_properties, report_parameters_document
    attributes = parsed_attributes(serialize(draft))["Create Report"]
    return {"reportParameters": report_parameters_document(attributes),
            "additionalProperties": _report_additional_properties(attributes) if camel_copy else {}}


def parsed_attributes(markdown: str) -> Dict[str, Dict[str, Any]]:
    """Each command of a document, parsed by Dr.Egeria offline (no Egeria reads): {command: attributes}.
    A repeated command keeps its last block; use parsed_commands for every block."""
    return {name: attrs for name, attrs in parsed_commands(markdown)}


def parsed_commands(markdown: str) -> List[Tuple[str, Dict[str, Any]]]:
    """[(command, attributes)] for every block of a document, parsed by Dr.Egeria with no client."""
    from pyegeria.core.async_runner import run_sync
    from md_processing.v2.extraction import UniversalExtractor
    from md_processing.v2.parsing import AttributeFirstParser
    from md_processing.md_processing_utils.md_processing_constants import get_command_spec, load_commands
    if not get_command_spec("Create Report"):
        load_commands()
    out = []
    for cmd in UniversalExtractor(markdown).extract_commands():
        if not (cmd.verb or "").strip():
            continue   # the document's own "# title": not a command
        parser = AttributeFirstParser(cmd, client=None, directive="validate")
        parsed = run_sync(parser.parse())
        out.append((f"{cmd.verb} {cmd.object_type}", (parsed or {}).get("attributes") or {}))
    return out


def has_parent_id(markdown: str) -> bool:
    """True if the document names a Parent ID anywhere (the serializer never does)."""
    return any(line.strip().lower().startswith("### parent id") for line in markdown.splitlines())
