#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Dr.Egeria round-trip probe (BRIEF-DR-EGERIA-ROUNDTRIP-PROBE-2026-11-12), phase 1: property styles.

For every Dr.Egeria Create command, set every property-style attribute to a recognisable value, run the
generated document through `dr_egeria --process` against a SCRATCH Egeria, read each element back and
report which values did not come back (DROPPED / CHANGED / DEFAULTED / NOT FOUND ...).

SCRATCH ONLY. The guard refuses to start unless the URL is exactly https://localhost:19443 (or
127.0.0.1) AND Docker shows the container publishing host port 19443 is `egeria-scratch-roundtrip`
labelled `purpose=roundtrip-probe`, AND its platform origin answers. Ports 9443, 8443 and 7443 are
refused on any host. The refusal happens before any request. See README.md.

    uv run -p 3.13 python scripts/dr_egeria_roundtrip_probe/probe.py --smoke
    uv run -p 3.13 python scripts/dr_egeria_roundtrip_probe/probe.py --run
    uv run -p 3.13 python scripts/dr_egeria_roundtrip_probe/probe.py --run --url https://localhost:9443   # refused
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import glob
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

SCRATCH_URL = "https://localhost:19443"
SCRATCH_HOSTS = {"localhost", "127.0.0.1"}
SCRATCH_PORT = 19443
SCRATCH_CONTAINER = "egeria-scratch-roundtrip"
SCRATCH_LABEL = "purpose=roundtrip-probe"
REFUSED_PORTS = {9443, 8443, 7443}
IMAGE = "odpi/egeria-platform@sha256:002a3ef17b269775797fd9bf590a503b098141094c83839443b79753c44f4060"
VIEW_SERVER = "view-server"


def compact_dir() -> Path:
    """The compact command specs of the md_processing actually installed in this interpreter (so the probe
    can be run from one checkout against another checkout's code)."""
    import md_processing
    return Path(md_processing.__file__).resolve().parent / "data" / "compact_commands"

PHASE1_STYLES = {"Simple", "Simple List", "Simple Int", "Simple Float", "Line List", "Bool", "Valid Value",
                 "Enum", "Dictionary", "Named DICT"}
RELATIONSHIP_STYLES = {"Reference Name", "Reference Name List", "GUID", "QN"}
#: Attributes that steer the command rather than carry a property: never set, listed as SKIPPED (control).
CONTROL_ATTRIBUTES = {
    "Merge Update": "steers update behaviour, not a property",
    "Parent Relationship Type Name": "names the parent relationship (phase 2)",
    "Parent at End1": "names the parent relationship's end (phase 2)",
    "Journal Entry": "creates a note-log entry, a separate element (phase 2)",
    "Effective Time": "a request option (the time to query as of), not a property",
    "External Source GUID": "provenance option (with External Source Name); needs a registered external source",
    "As Of Time": "a request option, not a property",
    "Display Name": "set by the probe's naming convention and checked as such",
    "Template GUID": "names a template element; needs a real target (phase 2)",
    "Placeholder Property Values": "fills a real template's placeholders (phase 2)",
    "For Lineage": "a request option, not a property",
    "For Duplicate Processing": "a request option, not a property",
    "Request ID": "a request option, not a property",
    "Is Own Anchor": "an anchoring option for the create request, not a property",
    "External Source Name": "provenance option; needs a registered external source (phase 2)",
    "Zone Membership": ("needs a real zone: made-up zones make the element unreadable by the probe user "
                        "(OPEN-METADATA-SECURITY-403-020 on the first runs), phase 2"),
}
#: Attributes whose probe value makes Egeria reject the whole create (found on the first run, 2026-11-12,
#: run-20261112T092519Z). Not sent, so the rest of the command can be diffed; each is reported as a
#: REJECTED row with its cause, and the cause is a finding in its own right.
REJECTED = {
    "Parent Relationship Attributes": (
        "pyegeria-side: sent raw as parentRelationshipProperties with no \"class\"; Egeria 400 "
        "InvalidTypeIdException on every create (108 of 110 failures on the first run)"),
    "Template Properties": (
        "pyegeria-side: sent raw as replacementProperties with no \"class\"; Egeria 400 InvalidTypeIdException"),
    "Generic Initial Classifications": (
        "pyegeria-side: sent raw as replacementClassifications with no \"class\"; Egeria 400 InvalidTypeIdException"),
    "Extended Properties": (
        "input-side: an arbitrary key is not a property of the subtype; Egeria 400 OMRS-REPOSITORY-400-028 "
        "(correct behaviour; needs real subtype property names, phase 2)"),
    "Absolute Uncertainty": (
        "pyegeria-side: Simple Float sent as the string \"7.5\"; Egeria's field is a Long, 400 "
        "'Cannot deserialize value of type java.lang.Long from String'"),
    "Relative Uncertainty": (
        "pyegeria-side: Simple Float sent as the string \"7.5\"; Egeria's field is a Long, 400 "
        "'Cannot deserialize value of type java.lang.Long from String'"),
}
#: The pyegeria-side REJECTED attributes: sent by default (they used to break the whole create; F-A made
#: pyegeria send them typed or report them not applied), skipped only with --no-send-rejected.
#: Extended Properties stays skipped: Egeria rejecting an arbitrary key there is correct (input-side).
SENDABLE_REJECTED = {"Parent Relationship Attributes", "Template Properties", "Generic Initial Classifications",
                     "Absolute Uncertainty", "Relative Uncertainty"}
SEND_REJECTED = True  # the default since F-A; --no-send-rejected restores the old skip

#: Attributes that are properties of a link to a parent, so they need a parent to check (phase 2).
LINK_PROPERTY_ATTRIBUTES = {
    a: "a property of the AttributeForSchema / NestedSchemaAttribute link to the parent; needs a parent (phase 2)"
    for a in ("Element Position", "Min Cardinality", "Max Cardinality")}

#: Where an attribute is stored when it is not `properties.<camelCase>` -- one row per known place.
LOCATIONS = {
    "Zone Membership": ("header.zoneMembership.classificationProperties.zoneMembership",
                        "zones are the ZoneMembership classification in the element header"),
    "Confidence Classification": ("cls:Confidence", "a governance classification in the header, stored as a level"),
    "Confidentiality Classification": ("cls:Confidentiality", "a governance classification, stored as a level"),
    "Criticality Classification": ("cls:Criticality", "a governance classification, stored as a level"),
    "Impact Classification": ("cls:Impact", "a governance classification, stored as a level"),
    "Retention Classification": ("cls:Retention", "a governance classification, stored as a basis"),
    "Security Tags": ("cls:SecurityTags", "the SecurityTags classification in the header"),
    "Policy Management Point": ("cls:PolicyManagementPoint", "a classification in the header"),
    "Search Keywords": ("rel.searchKeywords.displayName",
                        "keywords are SearchKeyword elements (SearchKeywordProperties.displayName) linked to the element"),
    # glossary-term flags and naming markers are header classifications in Egeria 6 (F-B group 1)
    "Is Abstract Concept": ("cls:AbstractConcept", "a classification of the term"),
    "Is Activity Description": ("cls:ActivityDescription", "a classification of the term"),
    "Term Activity Type": ("cls:ActivityDescription", "ActivityDescription.activityType"),
    "Is Context": ("cls:ContextDefinition", "a classification of the term"),
    "Context Description": ("cls:ContextDefinition", "ContextDefinition.description"),
    "Context Scope": ("cls:ContextDefinition", "ContextDefinition.scope"),
    "Is Data Value": ("cls:DataValueMeaning", "a classification of the term"),
    "Class Word Classification": ("cls:ClassWord", "a naming-standard classification of the term"),
    "Modifier Classification": ("cls:Modifier", "a naming-standard classification of the term"),
    "Prime Word Classification": ("cls:PrimeWord", "a naming-standard classification of the term"),
    "Is Taxonomy": ("cls:Taxonomy", "a collection-kind classification of the glossary"),
    "Project Approach": ("cls:ProjectClassification", "ProjectClassification.approach"),
    "Project Management Style": ("cls:ProjectClassification", "ProjectClassification.managementStyle"),
    "Project Results Usage": ("cls:ProjectClassification", "ProjectClassification.resultsUsage"),
    "Project Type": ("clsvalue:", "the classification the value names (Campaign, Task, ...)"),
    "Is Canonical": ("cls:CanonicalVocabulary", "a collection-kind classification of the glossary"),
}

#: Attributes Dr.Egeria sends as Egeria's governance-domain number (GovernanceDomains: DATA = 1, ...), not the name.
DOMAIN_ATTRIBUTES = {"Domain Identifier", "Role Domain Identifier"}


def domain_number(name):
    """A governance-domain name ("Data", "All Domains", "IT Infrastructure") as the number Egeria stores."""
    from pyegeria.core._globals import GovernanceDomains
    key = re.sub(r"[^A-Z0-9]+", "_", str(name).upper()).strip("_")
    key = {"ALL_DOMAINS": "ALL"}.get(key, key)
    member = GovernanceDomains.__members__.get(key)
    return member.value if member else name


# ── Guard ──

class Refused(SystemExit):
    pass


def guard(url: str) -> None:
    """Refuse anything but the scratch platform, before any request to it."""
    p = urlparse(url)
    port = p.port or (443 if p.scheme == "https" else 80)
    if port in REFUSED_PORTS:
        raise Refused(f"REFUSED: {url} uses port {port}, a laz/quickstart port; this probe runs only against "
                      f"the scratch platform {SCRATCH_URL}")
    if p.scheme != "https" or p.hostname not in SCRATCH_HOSTS or port != SCRATCH_PORT or p.path not in ("", "/"):
        raise Refused(f"REFUSED: {url} is not the scratch platform {SCRATCH_URL}")
    out = subprocess.run(["docker", "ps", "--filter", f"label={SCRATCH_LABEL}", "--filter", f"publish={SCRATCH_PORT}",
                          "--format", "{{.Names}}"], capture_output=True, text=True).stdout.split()
    if out != [SCRATCH_CONTAINER]:
        raise Refused(f"REFUSED: no running container {SCRATCH_CONTAINER} labelled {SCRATCH_LABEL} publishes port "
                      f"{SCRATCH_PORT} (docker shows {out})")
    ctx = ssl.create_default_context()
    ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
    origin = urllib.request.urlopen(f"{url}/open-metadata/platform-services/server-platform/origin",
                                    context=ctx, timeout=10).read().decode()
    if "Egeria OMAG Server Platform" not in origin:
        raise Refused(f"REFUSED: {url} origin is {origin!r}")


def scratch_image() -> str:
    """The image (with digest) the scratch container runs."""
    proc = subprocess.run(["docker", "inspect", "-f", "{{.Config.Image}}", SCRATCH_CONTAINER],
                          capture_output=True, text=True)
    return proc.stdout.strip() or IMAGE


def scratch_setup() -> dict:
    """The scratch platform's repository and the archives its metadata store loaded (results header)."""
    pg = subprocess.run(["docker", "inspect", "-f", "{{.State.Status}}", "egeria-scratch-roundtrip-pg"],
                        capture_output=True, text=True).stdout.strip()
    info = {"repository": "postgres" if pg == "running" else "memory", "content_packs": []}
    pointer = Path("~/.re-gate/roundtrip-probe/.current_scratch").expanduser()
    try:
        folder = Path(pointer.read_text().strip())
        config = folder / "data/servers/simple-metadata-store/config/simple-metadata-store.config"
        connections = json.loads(config.read_text())["repositoryServicesConfig"]["openMetadataArchiveConnections"]
        info["content_packs"] = [c.get("endpoint", {}).get("networkAddress", "").split("/")[-1] for c in connections]
    except (OSError, ValueError, KeyError):
        info["content_packs"] = ["unknown"]
    return info


def laz_started_at():
    """StartedAt of laz's Egeria container when this host has one: a read-only inspect, recorded so a
    run can show it never touched laz."""
    proc = subprocess.run(["docker", "inspect", "-f", "{{.State.StartedAt}}", "quickstart-egeria-main"],
                          capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else None


def scratch_password(user: str) -> str:
    """The user's password from the scratch container's own (the image's demo) secrets; never printed."""
    if os.environ.get("PROBE_PASSWORD"):
        return os.environ["PROBE_PASSWORD"]
    script = (f"awk '/^      {user}:/{{f=1}} f && /clearPassword:/{{sub(/.*clearPassword: */,\"\"); print; exit}}' "
              "/deployments/secrets/coco-user-directory.omsecrets")
    pw = subprocess.run(["docker", "exec", SCRATCH_CONTAINER, "sh", "-c", script],
                        capture_output=True, text=True).stdout.strip()
    if not pw:
        raise SystemExit(f"no password for {user} in the scratch container's secrets")
    return pw


def probe_env(url: str, user: str, password: str, root: Path) -> dict:
    """A clean environment: nothing EGERIA_*/PYEGERIA_* inherited, the scratch settings set explicitly."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("EGERIA_", "PYEGERIA_"))}
    env.update({"EGERIA_PLATFORM_URL": url, "EGERIA_VIEW_SERVER_URL": url, "EGERIA_VIEW_SERVER": VIEW_SERVER,
                "EGERIA_USER": user, "EGERIA_USER_PASSWORD": password, "PYEGERIA_ROOT_PATH": str(root),
                "DR_EGERIA_OUTBOX_PATH": "outbox", "EGERIA_WIDTH": "100000", "PYEGERIA_CONFIG_DIRECTORY": str(root),
                # local (non-Egeria) stores and caches stay inside the run folder, never the user's ~/.pyegeria
                # (the first run wrote a Dashboard Sheet into ~/.pyegeria/dashboard_sheets.json)
                "HOME": str(root / "home"),
                "PYEGERIA_DASHBOARD_SHEETS_STORE": str(root / "home" / ".pyegeria" / "dashboard_sheets.json"),
                "PYEGERIA_USER_REPORT_SPECS_DIR": str(root / "home" / ".pyegeria" / "report_specs")})
    (root / "home" / ".pyegeria").mkdir(parents=True, exist_ok=True)
    return env


def command_error(log_text: str, qn: str) -> str:
    """The Egeria/Dr.Egeria error that follows this command's first request body in the log."""
    at = log_text.find(f'"{qn}"')
    if at < 0:
        return ""
    tail = log_text[at:at + 40000]
    nxt = tail.find("DEBUG CMD:")
    tail = tail[:nxt] if nxt > 0 else tail
    for pattern in (r'"exceptionErrorMessage":"((?:[^"\\]|\\.){0,240})', r"Egeria Message\s*│\s*(.{0,240}?)\s*│",
                    r"(Validation failed:.{0,200})", r"(Execution failed:.{0,200})"):
        m = re.search(pattern, tail)
        if m:
            return m.group(1).strip()
    return ""


# ── Commands and values ──

def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", text.title())


def create_commands():
    """[(family, command, spec)] for every Create command, resolved by key, display name or alternate."""
    from md_processing.md_processing_utils.md_processing_constants import get_command_spec, load_commands
    load_commands()
    out = []
    for f in sorted(compact_dir().glob("*.json")):
        data = json.loads(f.read_text())
        family = data.get("family") or f.stem
        for key, c in (data.get("commands") or {}).items():
            if c.get("verb") != "Create":
                continue
            alts = c.get("alternate_names") or []
            alts = alts if isinstance(alts, list) else alts.split(";")
            spec = None
            for cand in [key, c.get("display_name")] + list(alts):
                if cand and str(cand).strip() and get_command_spec(str(cand).strip()):
                    spec = get_command_spec(str(cand).strip())
                    break
            out.append((family, key, spec))
    return out


def is_date(attr) -> bool:
    return attr.get("style") == "Simple" and bool(re.search(r"(Date|Time|Effective From|Effective To)$", attr["name"]))


def plan(attr, cslug: str):
    """(kind, markdown value, expected) for an attribute, or (SKIP verdict, None, reason)."""
    name, style = attr["name"], attr.get("style") or "Simple"
    if name in CONTROL_ATTRIBUTES:
        return "SKIPPED (control)", None, CONTROL_ATTRIBUTES[name]
    if name in REJECTED and not (SEND_REJECTED and name in SENDABLE_REJECTED):
        return "REJECTED (breaks the create)", None, REJECTED[name]
    if name in LINK_PROPERTY_ATTRIBUTES:
        return "SKIPPED (relationship – phase 2)", None, LINK_PROPERTY_ATTRIBUTES[name]
    if style in RELATIONSHIP_STYLES or attr.get("existing_element"):
        return "SKIPPED (relationship – phase 2)", None, f"style {style}" + (", existing_element" if attr.get("existing_element") else "")
    if style not in PHASE1_STYLES:
        return "SKIPPED (not a phase-1 style)", None, f"style {style}"
    base = f"RTP {cslug} {slug(name)}"
    default = attr.get("default_value")
    if name == "Effective From":
        return "date", "2020-01-02", "2020-01-02"
    if name == "Effective To" or is_date(attr):
        return "date", "2031-01-02", "2031-01-02"
    if style == "Simple":
        return "text", base, base
    if style in ("Simple List", "Line List"):
        items = [f"{base}-1", f"{base}-2"]
        return "list", "\n".join(f"- {i}" for i in items) if style == "Simple List" else "\n".join(items), items
    if style == "Simple Int":
        return "int", "7", 7
    if style == "Simple Float":
        return "float", "7.5", 7.5
    if style == "Bool":
        want = not (str(default).strip().lower() in ("true", "yes", "1"))
        return "bool", "true" if want else "false", want
    if style in ("Valid Value", "Enum"):
        vals = [str(v) for v in (attr.get("valid_values") or []) if str(v).strip() and str(v).upper() != "DELETED"]
        # the second value in the list, so a stored value is told apart from the default (brief §2)
        candidates = [v for v in vals if v != str(default)]
        if not candidates:
            return "SKIPPED (no non-default valid value)", None, f"valid values {vals}"
        choice = vals[1] if len(vals) > 1 and vals[1] != str(default) else candidates[0]
        return "valid", choice, choice
    if style in ("Dictionary", "Named DICT"):
        return "dict", f"rtpKey: {base}", {"rtpKey": base}
    return "SKIPPED (not a phase-1 style)", None, f"style {style}"


#: A value valid for exactly one status enum, so where it lands says which field Dr.Egeria chose.
STATUS_PROBE_VALUES = {"contentStatus": "DRAFT", "activityStatus": "IN_PROGRESS",
                       "deploymentStatus": "UNDER_DEVELOPMENT"}


def status_plan(spec: dict, attribute_names: set):
    """Where Dr.Egeria puts the generic `Status` for this command's type, and the value to send.

    Dr.Egeria maps `Status` onto the type's own status field (md_processing_utils.element_status,
    driven by element_status_fields.STATUS_FIELDS_BY_PROPERTIES_CLASS); the header element status
    can't be set on create. The command's own Content/Activity/Deployment Status attributes would win
    the field, so Status is tested on a second, Status-only element (see build_family_doc). Returns
    (kind, md, expected, location) or a SKIPPED row.
    """
    from md_processing.md_processing_utils.element_status import EXPLICIT_STATUS_ATTRIBUTES, _PREFERENCE
    from md_processing.md_processing_utils.element_status_fields import STATUS_FIELDS_BY_PROPERTIES_CLASS
    cls = f"{spec.get('OM_TYPE') or ''}Properties"
    fields = STATUS_FIELDS_BY_PROPERTIES_CLASS.get(cls)
    note = ""
    if fields is None:  # a type the table doesn't know: Dr.Egeria's fallback is contentStatus
        fields, note = ("contentStatus",), f" ({cls} not in the status table; Dr.Egeria falls back to contentStatus)"
    if not fields:
        return "SKIPPED (no status property)", None, f"{cls} has no status property", None
    free = [f for f in _PREFERENCE if f in fields]
    value = STATUS_PROBE_VALUES[free[0]]
    return "valid", value, value, f"properties.{free[0]}" + note


def build_family_doc(family: str, commands, out_dir: Path, tag: str = ""):
    """The family's Dr.Egeria document and its per-command plan."""
    lines, plans = [f"# RTP round-trip probe: {family}", ""], []
    for _fam, command, spec in commands:
        cslug = slug(command)
        qn = f"RTP::{tag}::{cslug}" if tag else f"RTP::{cslug}"
        display = f"RTP {cslug} DisplayName {tag}".rstrip()
        rows, block, status_row = [], [], None
        for attr in spec.get("Attributes", []):
            if attr["name"] in ("Qualified Name",):
                continue
            if attr["name"] == "Status" and attr["name"] not in CONTROL_ATTRIBUTES:
                planned = {a["name"] for a in spec.get("Attributes", []) if plan(a, cslug)[1] is not None}
                kind, md, expected, location = status_plan(spec, planned)
                status_row = ({"attribute": "Status", "style": attr.get("style"), "kind": kind,
                               "sent": expected if md is not None else None,
                               "reason": expected if md is None else None, "property": None,
                               "variable": attr.get("variable_name"), "default": attr.get("default_value"),
                               "location": location}, md)
                continue
            kind, md, expected = plan(attr, cslug)
            rows.append({"attribute": attr["name"], "style": attr.get("style"), "kind": kind,
                         "sent": expected if md is not None else None, "reason": expected if md is None else None,
                         "property": attr.get("property_name") or None, "variable": attr.get("variable_name"),
                         "default": attr.get("default_value"), "location": None})
            if md is not None:
                block += [f"### {attr['name']}", md, ""]
        lines += ["___", "", f"## {command}", "", "### Display Name", display, "", "### Qualified Name", qn, ""] + block
        plans.append({"family": family, "command": command, "qualified_name": qn, "display_name": display,
                      "rows": rows})
        if status_row:
            row, md = status_row
            if md is None:
                plans[-1]["rows"].append(row)
            else:
                # Status alone (no Content/Activity/Deployment Status, which would win the field): its own element
                from md_processing.md_processing_utils.element_status import EXPLICIT_STATUS_ATTRIBUTES
                explicit = {f"### {a}" for a in EXPLICIT_STATUS_ATTRIBUTES}
                kept, skip = [], False
                for line in block:
                    if line.startswith("### "):
                        skip = line in explicit
                    if not skip:
                        kept.append(line)
                sqn, sdisplay = f"{qn}::Status", f"RTP {cslug} StatusProbe {tag}".rstrip()
                lines += ["___", "", f"## {command}", "", "### Display Name", sdisplay, "", "### Qualified Name",
                          sqn, ""] + kept + ["### Status", md, ""]
                plans.append({"family": family, "command": command, "qualified_name": sqn,
                              "display_name": sdisplay, "rows": [row], "status_probe": True})
    lines += ["___", ""]
    doc = out_dir / f"{slug(family)}.md"
    doc.write_text("\n".join(lines), encoding="utf-8")
    return doc, plans


# ── Read back and compare ──

def camel(var: str) -> str:
    parts = (var or "").split("_")
    return parts[0] + "".join(p.title() for p in parts[1:]) if parts else ""


def classification(element: dict, name: str):
    """The properties of the header classification called `name` (any slot), or None."""
    def walk(node):
        if isinstance(node, dict):
            if node.get("classificationName") == name:
                return node.get("classificationProperties") or {"present": True}
            for v in node.values():
                hit = walk(v)
                if hit is not None:
                    return hit
        elif isinstance(node, list):
            for v in node:
                hit = walk(v)
                if hit is not None:
                    return hit
        return None
    return walk(element.get("elementHeader") or {})


def dig(element: dict, path: str, sent=None):
    if path.startswith("clsvalue:"):
        return classification(element, str(sent)) if sent else None
    if path.startswith("cls:"):
        return classification(element, path[4:])
    if path.startswith("rel."):
        _, rel, key = path.split(".", 2)
        items = element.get(rel) or []
        return [((i.get("relatedElement") or {}).get("properties") or {}).get(key) for i in items] or None
    node = element
    for part in path.split("."):
        node = (element.get("elementHeader") if part == "header" and node is element else
                (node.get(part) if isinstance(node, dict) else None))
        if node is None:
            return None
    return node


def find_value(node, wanted, path=""):
    """Where `wanted` appears anywhere in the element JSON (for NOT FOUND hints)."""
    if isinstance(node, dict):
        for k, v in node.items():
            hit = find_value(v, wanted, f"{path}.{k}" if path else k)
            if hit:
                return hit
    elif isinstance(node, list):
        if wanted in node:
            return path
        for i, v in enumerate(node):
            hit = find_value(v, wanted, f"{path}[{i}]")
            if hit:
                return hit
    elif node == wanted:
        return path
    return None


def norm(kind, value):
    if value is None:
        return None
    if kind == "list" and isinstance(value, list):
        return sorted(str(v) for v in value)   # the order Egeria returns linked elements in isn't meaningful
    if kind == "date":
        return str(value)[:10]
    if kind == "valid":
        return re.sub(r"[^a-z0-9]", "", str(value).lower())
    if kind == "int":
        try:
            return int(value)
        except (TypeError, ValueError):
            return value
    if kind == "float":
        try:
            return float(value)
        except (TypeError, ValueError):
            return value
    if kind == "bool":
        return value if isinstance(value, bool) else str(value).lower() in ("true", "1", "yes")
    return value


def verdict(row, element):
    kind, sent = row["kind"], row["sent"]
    if row.get("location"):
        path = row["location"].split(" ")[0]
        got = dig(element, path)
    elif row["attribute"] in LOCATIONS:
        path = LOCATIONS[row["attribute"]][0]
        got = dig(element, path, sent)
    else:
        key = row["property"] or camel(row["variable"])
        path = f"properties.{key}"
        got = (element.get("properties") or {}).get(key)
    if got in (None, "", [], {}):
        probe = sent[0] if isinstance(sent, list) else (next(iter(sent.values())) if isinstance(sent, dict) else sent)
        seen = find_value(element, probe) if isinstance(probe, str) else None
        if seen:
            return "NOT FOUND", None, f"not at {path}; seen at {seen}"
        return "DROPPED", None, f"absent at {path}"
    if path.startswith(("cls:", "clsvalue:")):
        stored = {k: v for k, v in got.items() if k not in ("class", "typeName")}
        if row["attribute"] == "Security Tags":
            ok = set(map(str, sent if isinstance(sent, list) else [sent])) <= set(map(str, stored.get("securityLabels") or []))
            return ("MATCH" if ok else "CHANGED"), stored, path
        return "MATCH", stored, f"{path} present (Dr.Egeria sends the valid value as a level number)"
    if row["attribute"] in DOMAIN_ATTRIBUTES and str(got) == str(domain_number(sent)):
        return "MATCH", got, f"{path} (domain {sent!r} is stored as {got})"
    if norm(kind, got) == norm(kind, sent):
        return "MATCH", got, path
    if kind == "dict" and isinstance(got, dict) and isinstance(sent, dict) \
            and all(str(got.get(k)) == str(v) for k, v in sent.items()):
        return "MATCH", got, f"{path} (sent keys present, with others Dr.Egeria adds)"
    if row["default"] not in (None, "") and norm(kind, got) == norm(kind, row["default"]):
        return "DEFAULTED", got, path
    return "CHANGED", got, path


# ── Raw store (repository-services: what Egeria stored, bypassing the bean converters) ──

def raw_value(value: dict):
    """A repository-services InstancePropertyValue as plain Python."""
    if not isinstance(value, dict):
        return value
    cat = value.get("instancePropertyCategory")
    if cat == "PRIMITIVE":
        return value.get("primitiveValue")
    if cat == "ENUM":
        return value.get("symbolicName")
    if cat == "ARRAY":
        items = ((value.get("arrayValues") or {}).get("instanceProperties") or {})
        return [raw_value(items[k]) for k in sorted(items, key=lambda k: int(k) if str(k).isdigit() else k)]
    if cat in ("MAP", "STRUCT"):
        inner = value.get("mapValues") or value.get("attributes") or {}
        return {k: raw_value(v) for k, v in (inner.get("instanceProperties") or {}).items()}
    return value.get("primitiveValue", value)


def raw_properties(instance_properties: dict | None) -> dict:
    return {k: raw_value(v) for k, v in ((instance_properties or {}).get("instanceProperties") or {}).items()}


def parse_raw_entity(response: dict) -> dict | None:
    """{properties, effectiveFromTime, effectiveToTime, classifications{name: properties}} from an
    EntityDetailResponse, or None when it carries no entity."""
    entity = (response or {}).get("entity")
    if not isinstance(entity, dict):
        return None
    props = entity.get("properties") or {}
    return {"properties": raw_properties(props),
            "effectiveFromTime": props.get("effectiveFromTime"), "effectiveToTime": props.get("effectiveToTime"),
            "classifications": {c.get("name"): raw_properties(c.get("properties"))
                                for c in entity.get("classifications") or []}}


def fetch_raw_entity(url: str, user: str, headers: dict, guid: str):
    """The stored entity from the scratch metadata store (POST with a GetRequest body; GET is 405)."""
    import httpx
    endpoint = (f"{url}/servers/simple-metadata-store/open-metadata/repository-services/users/{user}"
                f"/instances/entity/{guid}")
    try:
        r = httpx.post(endpoint, json={"class": "GetRequest"}, headers={"Authorization": headers["Authorization"]},
                       verify=False, timeout=30)
        data = r.json()
    except Exception as exc:  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"[:120]
    parsed = parse_raw_entity(data)
    return parsed, (None if parsed else f"no entity (HTTP {r.status_code}: {data.get('exceptionErrorMessage', '')[:80]})")


def stored_raw(row: dict, path: str, raw: dict | None, why: str | None):
    """('yes', value) / ('no', None) / ('not checked', reason) for one attribute in the raw entity."""
    if raw is None:
        return "not checked", why or "no raw entity"
    if row["attribute"] in ("Effective From", "Effective To"):
        value = raw["effectiveFromTime" if row["attribute"] == "Effective From" else "effectiveToTime"]
        return ("yes", value) if value not in (None, "") else ("no", None)
    if path.startswith("cls:"):
        name = path[4:]
        return ("yes", raw["classifications"][name]) if name in raw["classifications"] else ("no", None)
    if path.startswith("rel.") or path.startswith("header."):
        return "not checked", "a relationship or header field, not an entity property"
    key = path.split(".", 1)[1] if path.startswith("properties.") else path
    value = raw["properties"].get(key)
    return ("yes", value) if value not in (None, "", [], {}) else ("no", None)


def split_verdict(verdict_: str, stored: str) -> str:
    """DROPPED splits on the raw store: not stored at all, or stored and not returned by the read."""
    if verdict_ == "DROPPED":
        return {"yes": "NOT RETURNED (stored)", "no": "DROPPED (not stored)"}.get(
            stored, "DROPPED (raw read not applicable)")
    return verdict_


# ── Running ──

def not_applied_reports(log_text: str) -> dict[str, dict[str, str]]:
    """{qualified name: {attribute: reason}} from Dr.Egeria's "Processing Warnings" section, where a command
    lists each `not applied: <attribute>: <reason>` under `-- <verb> <object> (<qualified name>) --`."""
    out: dict[str, dict[str, str]] = {}
    current = None
    for line in log_text.splitlines():
        m = re.match(r"^-- .+ \((.+)\) --\s*$", line.strip())
        if m:
            current = out.setdefault(m.group(1), {})
            continue
        m = re.match(r"^- not applied: ([^:]+): (.+)$", line.strip())
        if m and current is not None:
            current.setdefault(m.group(1).strip(), m.group(2).strip())
    return out


def run_dr_egeria(doc: Path, env: dict, url: str, user: str, log: Path) -> str:
    cmd = [sys.executable, "-m", "commands.cat.dr_egeria", str(doc), "--process", "--advanced", "--debug",
           "--server", VIEW_SERVER, "--url", url, "--userid", user, "--summary-only"]
    proc = subprocess.run(cmd, env=env, cwd=str(log.parent), capture_output=True, text=True, timeout=3600)
    log.write_text(proc.stdout + "\n--- stderr ---\n" + proc.stderr, encoding="utf-8")
    return proc.stdout + proc.stderr


def command_segment(log_text: str, display: str) -> str:
    """The log between this command's `DEBUG CMD` marker and the next one (its create and follow-up calls)."""
    at = log_text.find(f"display_name='{display}'")
    if at < 0:
        return ""
    nxt = log_text.find("DEBUG CMD:", at)
    return log_text[at:nxt if nxt > 0 else len(log_text)]


def bodies_for(log_text: str, qn: str, display: str = ""):
    """Request bodies for this command: every body in its log segment (create plus follow-up classify
    calls, which carry a GUID rather than the qualified name), and any body elsewhere carrying the QN."""
    out, dec = [], json.JSONDecoder()
    segment = command_segment(log_text, display) if display else ""
    for text, need_qn in ((segment, False), (log_text, True)):
        for m in re.finditer(r"\[DEBUG\] Body:\s*\n", text):
            try:
                body, _ = dec.raw_decode(text[m.end():].lstrip())
            except ValueError:
                continue
            if (not need_qn or qn in json.dumps(body)) and body not in out:
                out.append(body)
    return out


def summary_row(log_text: str, command: str, display: str, by_command: bool = True):
    """(status, message, guid) from Dr.Egeria's summary table row for this command, or None."""
    for line in log_text.splitlines():
        cells = [c.strip() for c in line.split("│")]
        if len(cells) > 6 and cells[1] == command and display in cells:
            msg = cells[-2] if cells[-1] == "" else cells[-1]
            guid = re.search(r"GUID: ([A-Za-z]*-?[0-9a-f]{8}-[0-9a-f-]{27})", msg)
            return cells[3], msg, guid.group(1) if guid else None, (cells[6] if len(cells) > 6 else "")
    if not by_command:
        return None
    for line in log_text.splitlines():  # some processors show their own name (e.g. Kafka Server Name), not ours
        cells = [c.strip() for c in line.split("│")]
        if len(cells) > 6 and cells[1] == command and cells[3] in ("SUCCESS", "FAILURE"):
            msg = cells[-2] if cells[-1] == "" else cells[-1]
            guid = re.search(r"GUID: ([A-Za-z]*-?[0-9a-f]{8}-[0-9a-f-]{27})", msg)
            return cells[3], msg, guid.group(1) if guid else None, (cells[6] if len(cells) > 6 else "")
    return None


def side(row, bodies):
    """pyegeria-side (the value is not in the request body under the expected key) or Egeria-side (it is,
    and did not come back). Key-aware: a value found only under another key is reported with that key."""
    if not bodies:
        return "unknown (no request body captured)"
    text = json.dumps(bodies)
    loc = LOCATIONS.get(row["attribute"], ("",))[0]
    if loc.startswith("cls:"):  # sent as a classify call carrying a level, not the valid-value name
        present = re.search(rf'"class": "{loc[4:]}(Classification)?Properties"', text) is not None
        return "Egeria-side (in the request body)" if present else "pyegeria-side (not in the request body)"
    key = row["property"] or camel(row["variable"])
    if (row.get("location") or "").startswith("properties."):
        key = row["location"].split(" ")[0].split(".", 1)[1]
    sent = row["sent"]
    probe = sent[0] if isinstance(sent, list) else (next(iter(sent.values())) if isinstance(sent, dict) else sent)
    hits = []

    def walk(node, k=None):
        if isinstance(node, dict):
            for kk, vv in node.items():
                walk(vv, kk)
        elif isinstance(node, list):
            for vv in node:
                walk(vv, k)
        elif k is not None and str(node).lower() == str(probe).lower():
            hits.append(k)
        elif k is not None and isinstance(probe, str) and isinstance(node, str) and probe.lower() in node.lower():
            hits.append(k)

    for b in bodies:
        walk(b)
    if isinstance(probe, str):
        # dict values are found under their own key (rtpKey): the attribute's key is the parent
        if isinstance(sent, dict) and "rtpKey" in hits:
            hits = [key] if f'"{key}"' in text else ["(a dictionary under another key)"]
    if key in hits:
        return f"Egeria-side (in the request body as {key})"
    if hits and isinstance(probe, str):  # a bool/number equal to some other field's value proves nothing
        other = sorted(set(hits))
        return f"pyegeria-side? (sent as {', '.join(other)}, not {key}: check the key against the Java bean)"
    return "pyegeria-side (not in the request body)"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=SCRATCH_URL)
    ap.add_argument("--user", default="garygeeke")
    ap.add_argument("--out", default="~/.re-gate/roundtrip-probe")
    ap.add_argument("--smoke", action="store_true", help="create one glossary and read it back")
    ap.add_argument("--run", action="store_true", help="the full phase-1 run")
    ap.add_argument("--families", default="", help="comma-separated family filter (default: all)")
    ap.add_argument("--gate", action="store_true", help="after --run, compare with the baseline (see gate.py)")
    ap.add_argument("--baseline", help="baseline file (default: baseline/<egeria digest>.json)")
    ap.add_argument("--known-gaps", help="known gaps file (default: known-gaps.json beside this script)")
    ap.add_argument("--rebaseline", action="store_true", help="after --run, write the baseline from this run")
    ap.add_argument("--send-rejected", dest="send_rejected", action="store_true", default=True,
                    help="send the pyegeria-side REJECTED attributes (the default)")
    ap.add_argument("--no-send-rejected", dest="send_rejected", action="store_false",
                    help="skip them, as before F-A")
    args = ap.parse_args(argv)

    guard(args.url)  # before anything else touches the platform
    global SEND_REJECTED
    SEND_REJECTED = args.send_rejected
    from pyegeria import EgeriaTech
    import importlib.metadata as md
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(args.out).expanduser()
    run_dir = out / f"run-{stamp}"
    (run_dir / "docs").mkdir(parents=True, exist_ok=True)
    password = scratch_password(args.user)
    env = probe_env(args.url, args.user, password, run_dir)
    print(f"probe: url={args.url} server={VIEW_SERVER} user={args.user} pyegeria={md.version('pyegeria')} "
          f"run={run_dir}")
    client = EgeriaTech(VIEW_SERVER, args.url, args.user, password)
    client.create_egeria_bearer_token()

    if args.smoke:
        doc = run_dir / "docs" / "smoke.md"
        doc.write_text("## Create Glossary\n\n### Display Name\nRTP Smoke Glossary\n\n### Qualified Name\n"
                       f"RTP::Smoke::{stamp}\n\n### Description\nRTP smoke test\n")
        text = run_dr_egeria(doc, env, args.url, args.user, run_dir / "smoke.log")
        el = client.get_element_by_unique_name(f"RTP::Smoke::{stamp}", output_format="JSON")
        ok = isinstance(el, dict) and (el.get("properties") or {}).get("description") == "RTP smoke test"
        print("smoke:", "PASS" if ok else "FAIL", (el.get("elementHeader", {}).get("guid") if isinstance(el, dict) else el))
        if not ok:
            print(text[-3000:])
        return 0 if ok else 1

    if not args.run:
        ap.error("choose --smoke or --run")
    start = dt.datetime.now(dt.timezone.utc)
    laz_before = laz_started_at()
    commands = create_commands()
    wanted = {f.strip() for f in args.families.split(",") if f.strip()}
    results, families = [], {}
    for fam, command, spec in commands:
        if wanted and fam not in wanted:
            continue
        if spec is None:
            results.append({"family": fam, "command": command, "attribute": "", "style": "", "sent": None,
                            "read": None, "verdict": "UNRESOLVED", "note": "command name did not resolve"})
            continue
        families.setdefault(fam, []).append((fam, command, spec))
    for fam, cmds in families.items():
        doc, plans = build_family_doc(fam, cmds, run_dir / "docs", stamp)
        log_text = run_dr_egeria(doc, env, args.url, args.user, run_dir / f"{slug(fam)}.log")
        for p in plans:
            row = summary_row(log_text, p["command"], p["display_name"], by_command=not p.get("status_probe"))
            try:
                el = client.get_element_by_unique_name(p["qualified_name"], output_format="JSON")
                if not isinstance(el, dict) and row and row[2]:
                    # some processors derive their own qualified name: read back by the GUID they reported
                    el = client.get_element_by_guid(row[2], output_format="JSON")
            except Exception as exc:  # noqa: BLE001
                el = f"{type(exc).__name__}: {exc}"
            if not isinstance(el, dict):
                err = command_error(log_text, p["qualified_name"]) or ""
                if row:
                    err = f"{row[0]}: {row[1]}" + (f" | {err}" if err else "")
                    if row[0] == "SUCCESS":
                        err = f"created but not readable back: {str(el)[:200]} | {err}"
                err = err or str(el)[:200]
                failed = "AUTH" if re.search(r"not authori[sz]ed|\b403\b|-403-", err, re.I) else "CREATE-FAILED"
                skipped = collections.Counter(r["kind"] for r in p["rows"] if r["kind"].startswith(("SKIPPED", "REJECTED")))
                results.append({"family": fam, "command": p["command"],
                                "attribute": "Status" if p.get("status_probe") else "", "style": "", "sent": None,
                                "read": None, "verdict": failed, "note": err[:300],
                                "skipped": dict(skipped)})
                continue
            bodies = bodies_for(log_text, p["qualified_name"], p["display_name"])
            reports = not_applied_reports(log_text)
            reported = dict(reports.get(row[3], {}) if row and len(row) > 3 else {})
            reported.update(reports.get(p["qualified_name"], {}))  # processors that derive their own QN
            raw, raw_why, guid = None, None, (el.get("elementHeader") or {}).get("guid")
            fetched = False
            for row in p["rows"]:
                if row["kind"].startswith(("SKIPPED", "REJECTED")):
                    results.append({"family": fam, "command": p["command"], "attribute": row["attribute"],
                                    "style": row["style"], "sent": None, "read": None, "verdict": row["kind"],
                                    "note": row["reason"]})
                    continue
                v, got, note = verdict(row, el)
                if v != "MATCH" and row["attribute"] in reported:
                    # Dr.Egeria said it didn't send this, and why: an answer, not a silent drop
                    v, note = "NOT APPLIED (reported)", reported[row["attribute"]]
                r = {"family": fam, "command": p["command"], "attribute": row["attribute"], "style": row["style"],
                     "sent": row["sent"], "read": got, "verdict": v, "note": note}
                if v != "MATCH":
                    if not fetched:
                        raw, raw_why = fetch_raw_entity(args.url, args.user, client.headers, guid) if guid else (
                            None, "no GUID")
                        fetched = True
                    path = note.split(" ")[-1] if v == "DROPPED" else note.split(" ")[0]
                    if v == "NOT FOUND":
                        path = note.split(";")[0].replace("not at ", "")
                    state, value = stored_raw(row, path, raw, raw_why)
                    r["stored"] = f"{state} {json.dumps(value, default=str)[:120]}" if state == "yes" else (
                        state if state == "no" else f"not checked ({value})")
                    r["verdict"] = v = split_verdict(v, state)
                if v.startswith(("DROPPED", "NOT RETURNED", "CHANGED", "DEFAULTED")):
                    r["side"] = side(row, bodies)
                results.append(r)
    end = dt.datetime.now(dt.timezone.utc)
    meta = {"image": scratch_image(), **scratch_setup(), "laz_started_at_before": laz_before, "laz_started_at_after": laz_started_at(),
            "option": "A (simple-metadata-store + view-server)", "pyegeria": md.version("pyegeria"),
            "user": args.user, "send_rejected": SEND_REJECTED, "start": start.isoformat(timespec="seconds"), "end": end.isoformat(timespec="seconds"),
            "commands": sum(len(c) for c in families.values()), "run_dir": str(run_dir)}
    results_file = out / f"RESULTS-{stamp}.json"
    results_file.write_text(json.dumps({"meta": meta, "rows": results}, indent=1, default=str))
    print(f"results: {results_file} ({len(results)} rows)")
    if args.gate or args.rebaseline:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import gate
        return gate.gate_results(results_file, Path(args.baseline).expanduser() if args.baseline else None,
                                 Path(args.known_gaps).expanduser() if args.known_gaps else gate.KNOWN_GAPS,
                                 args.rebaseline)
    return 0


if __name__ == "__main__":
    sys.exit(main())
