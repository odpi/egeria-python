#!/usr/bin/env python3
"""Audit pyegeria's OMVS clients against the Egeria .http collections.

The .http files under ``pyegeria/http clients/`` are the ground truth for REST
URLs, verbs, and request-body classes (see CLAUDE.md). This script reconciles
every ``_async_*`` method in ``pyegeria/omvs/*.py`` against them and reports:

  * MISSING        - a documented request with no SDK method
  * VERB MISMATCH  - SDK uses a different HTTP verb than the API
  * PATH MISMATCH  - SDK builds a different URL path than the API
  * BODY MISMATCH  - SDK sends a different request-body class than the API
  * ELSEWHERE      - method exists, but in a different OMVS module
  * RENAMED        - method exists in the right module and its verb+path
                     match exactly, just under a name unrelated to the .http
                     @name (no amount of snake_case guessing would find it)
  * LINT           - malformed URLs (``//``, missing separators) in the SDK

Usage
-----
    python scripts/omvs_audit.py [--report PATH] [--service NAME] [--quiet]

Exit status is 1 when any confirmed defect (verb/path/body mismatch or lint)
is found, so this can gate CI.

Note: ``pyegeria/http clients/`` is gitignored. It must be present locally or
the audit cannot run - the script fails loudly rather than reporting a clean
sheet against zero inputs.
"""

from __future__ import annotations

import argparse
import ast
import glob
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field

HTTP_DIR = "pyegeria/http clients"
OMVS_DIR = "pyegeria/omvs"
SERVER_CLIENT = "pyegeria/core/_server_client.py"

# Services documented in .http files that intentionally have no OMVS client.
SKIP_SERVICES = {"data-officer", "devops-pipeline", "multi-language"}

# .http @name -> SDK method name, where the SDK deliberately diverges.
NAME_OVERRIDES = {
    "get_omag__server__platform__origin": "get_platform_origin",
    "get_omag__server__platform__organization": "get_platform_organization",
    "get__platform__security__connection": "get_security_connection",
    "set__platform__security__connection": "set_security_connection",
    "delete__platform__security__connection": "delete_security_connection",
    "get__user__list": "get_security_user_list",
    "get_all_services": "get_registered_all_services",
    "get_governance_services": "get_registered_governance_services",
    "get_common_services": "get_registered_common_services",
    "query_if_a_specific_server_is_known": "is_server_known",
    "get_all_known_servers": "get_known_server_list",
    "get_all_active_servers": "get_active_server_list",
    "query_the_status_of_a_specific_server": "get_active_server_status",
    "start_server_-_using_stored_configuration": "activate_server_stored_config",
    "start_server_-_using_supplied_configuration": "activate_server_supplied_config",
    "move_glossary_term": "move_term",
    "delete_glossary_term": "delete_term",
    "get_glossary_terms_by_name": "get_terms_by_name",
    "get_glossary_term_by_guid": "get_term_by_guid",
    "get_glossary_term_relationship_statuses": "get_glossary_term_rel_statuses",
    "create_glossary_term_from_template": "create_term_copy",
    "setup_term_relationship": "add_relationship_between_terms",
    "update_term_relationship": "update_relationship_between_terms",
    "clear_term_relationship": "remove_relationship_between_terms",
    "set_term_as_abstract_concept": "add_is_abstract_concept",
    "clear_term_as_abstract_concept": "remove_is_abstract_concept",
    "set_term_as_prime_word": "set_is_prime_word",
    "clear_term_as_prime_word": "clear_is_prime_word",
    "set_term_as_modifier": "set_is_modifier",
    "clear_term_as_modifier": "clear_is_modifier",
    "set_term_as_class_word": "set_is_class_word",
    "clear_term_as_class_word": "clear_is_class_word",
    "set_term_as_data_value": "add_is_data_value",
    "clear_term_as_data_value": "remove_is_data_value",
    "set_term_as_activity": "add_activity_description",
    "clear_term_as_activity": "remove_activity_description",
    "set_term_as_context": "add_is_context_definition",
    "clear_term_as_context": "remove_is_context_definition",
    "get_metadata_element_guid_by_unique_name": "get_metadata_guid_by_unique_name",
    "get_governance_action_process_by_guid": "get_governance_action_process",
    "get_governance_action_processes_by_name": "get_governance_action_process_by_name",
    "link_peer_definitions": "link_peer_definition",
    "detach_peer_definitions": "detach_peer_definition",
    "get_actions_for_requester": "get_actions_for_requester",
}

# Attributes holding a bare service marker that gets interpolated into a URL
# (e.g. self.url_marker = "governance-officer"), and the shape their value
# must have to be treated as a literal path segment.
URL_SEGMENT_ATTR_RE = re.compile(r"(url_marker|marker|url_fragment|service_name)$")
URL_SEGMENT_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")

# Transparent wrappers around a URL expression, e.g. str(HttpUrl(f"...")).
URL_WRAPPERS = {"str", "HttpUrl", "AnyUrl", "quote", "urljoin"}

# Helpers that build a trailing "?key=value&..." query string (or "" when no
# params are set) - safe to elide entirely for path comparison, since
# canon_path already splits on "?". Appearing as f"{root}/foo{query_string(...)}"
# with no resolvable value otherwise renders as an opaque "{expr}" glued
# straight onto the path, producing false PATH mismatches
# (solution_architect.py / collection_manager.py's query_string() helper).
QUERY_STRING_FUNCS = {"query_string"}

# Internal helpers that resolve a name/GUID before the real call. They issue
# their own request, so they must not be mistaken for the method's own verb.
LOOKUP_HELPER_RE = re.compile(r"get_guid__|__async_get_guid")

# Known-duplicate endpoints: same verb+path by design, differing only by body.
EXPECTED_DUPLICATE_PATHS = {
    "POST platform-services/server-platform/servers/{}/instance",
}


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def to_snake(name: str) -> str:
    name = name.replace(" ", "_")
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def canon_path(path: str) -> str:
    """Normalise a URL path for comparison.

    Collapses every path parameter to ``{}`` and strips the host/prefix so both
    sides are rooted at the OMVS service segment. Deliberately does NOT strip
    trailing verbs (``/attach`` vs ``/detach``) - that distinction is exactly
    the class of bug this audit exists to catch.
    """
    path = path.split("?", 1)[0]
    # Strip copy/paste junk seen on some .http lines. Deliberately excludes '}'
    # and ']' so a path ending in a parameter ("/{{guid}}") stays intact.
    path = path.rstrip('"\'`),;')
    path = re.sub(r"\{\{[^}]+\}\}", "{}", path)   # {{guid}} -> {}
    path = re.sub(r"\{[^}]*\}", "{}", path)       # {guid}   -> {}
    path = re.sub(r"\{\}(?=\{\})", "", path)      # collapse adjacent params
    m = re.search(r"/api/open-metadata/(.*)", path)
    if m:
        path = m.group(1)
    else:
        m = re.search(r"/open-metadata/(.*)", path)
        if m:
            path = m.group(1)
    return "/" + path.strip("/")


def lint_url(raw: str) -> list[str]:
    """Structural problems detectable without ground truth."""
    problems = []
    body = re.sub(r"^https?://", "", raw)
    if "//" in body:
        problems.append("double slash in path")

    # A path parameter must follow a separator: ".../agreements{guid}" is the
    # concatenation bug that "/agreements" + "{guid}/..." produces. Only flag
    # placeholders that hold an identifier - a trailing "{query_params}" or a
    # dynamic segment like "by-{name}" is legitimate.
    for m in re.finditer(r"(?<=[A-Za-z0-9])\{(\w+)\}", raw):
        var = m.group(1).lower()
        if re.search(r"query|param|filter|suffix|string", var):
            continue
        if raw[m.start() - 1] == "-":          # "by-{name}" style segment
            continue
        if re.search(r"guid|_id$|^id$", var):
            problems.append(f"missing '/' before interpolated '{m.group(1)}'")

    literal = re.sub(r"\{\w*\}", "", body.split("?", 1)[0])
    if "_" in literal:
        problems.append("underscore in path segment (Egeria uses hyphens)")
    return problems


# --------------------------------------------------------------------------
# ground truth: .http collections
# --------------------------------------------------------------------------

@dataclass
class HttpRequest:
    name: str
    verb: str
    path: str
    body_class: str | None


def parse_http_file(filepath: str) -> dict[str, HttpRequest]:
    requests: dict[str, HttpRequest] = {}
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    for block in content.split("###"):
        nm = re.search(r"#\s*@name\s+([^(\n\r]+)", block)
        if not nm:
            continue
        um = re.search(r"^(GET|POST|PUT|DELETE|PATCH)\s+(\S+)", block, re.M)
        if not um:
            continue
        bm = re.search(r'"class"\s*:\s*"([^"]+)"', block)
        name = nm.group(1).strip()
        # First definition wins; later ones are usually worked examples of the
        # same endpoint with concrete GUIDs substituted in.
        requests.setdefault(name, HttpRequest(
            name=name,
            verb=um.group(1),
            path=canon_path(um.group(2)),
            body_class=bm.group(1) if bm else None,
        ))
    return requests


# --------------------------------------------------------------------------
# subject: pyegeria OMVS clients
# --------------------------------------------------------------------------

def discover_helper_verbs(path: str) -> dict[str, str]:
    """Map ``_async_*_request`` helpers to the verb they actually issue.

    Derived from the source rather than hardcoded, so the audit stays correct
    when helpers change. (Historically every helper is POST - a hardcoded
    table in an earlier version wrongly mapped the get_* helpers to GET, which
    is how a batch of GET-vs-POST defects went undetected.)
    """
    verbs: dict[str, str] = {}
    if not os.path.exists(path):
        return verbs
    tree = ast.parse(open(path, encoding="utf-8").read())
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        found = set()
        for node in ast.walk(fn):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "_async_make_request"
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)):
                found.add(node.args[0].value.replace("POST-DATA", "POST").upper())
        if len(found) == 1:
            verbs[fn.name] = found.pop()
    return verbs


def discover_helper_bodies(path: str) -> dict[str, frozenset[str]]:
    """Map each ``_async_*_request`` helper to the body models it accepts.

    A method that delegates to a helper sends *that helper's* model, whatever
    its own ``body`` annotation claims - so this is what must be compared
    against the ``"class"`` in the .http file.

    The value is a *set*, because several helpers accept a union (e.g.
    ``dict | UpdateElementRequestBody | UpdateClassificationRequestBody``).
    Picking a single name out of a union produced false mismatches.
    """
    bodies: dict[str, frozenset[str]] = {}
    if not os.path.exists(path):
        return bodies
    tree = ast.parse(open(path, encoding="utf-8").read())
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for a in list(fn.args.args) + list(fn.args.kwonlyargs):
            if a.arg == "body" and a.annotation is not None:
                names = re.findall(r"\b(\w+RequestBody)\b", ast.unparse(a.annotation))
                if names:
                    bodies[fn.name] = frozenset(names)
    return bodies


@dataclass
class PyMethod:
    name: str
    verb: str | None
    path: str | None
    raw_url: str | None
    body_class: frozenset[str] | None
    lint: list[str] = field(default_factory=list)


def _flatten(node: ast.AST, roots: dict[str, str]) -> str:
    """Render a URL expression to a literal path with ``{}`` for each variable.

    Handles the three shapes used across the OMVS clients: f-strings, ``+``
    concatenation, and plain constants - including nesting of all three.
    Regex cannot do this reliably (multi-line f-strings silently yielded an
    empty path in an earlier version, masking every mismatch in the module).
    """
    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.JoinedStr):
        return "".join(_flatten(v, roots) for v in node.values)
    if isinstance(node, ast.FormattedValue):
        return _flatten(node.value, roots)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _flatten(node.left, roots) + _flatten(node.right, roots)
    if isinstance(node, ast.Name):
        if node.id in roots:
            return roots[node.id]
        return "{%s}" % node.id
    if isinstance(node, ast.Attribute):
        if isinstance(node.value, ast.Name) and node.value.id == "self":
            if node.attr == "platform_url":
                return ""
            if node.attr in roots:
                return roots[node.attr]
        return "{%s}" % node.attr
    if isinstance(node, ast.Call):
        fname = (node.func.id if isinstance(node.func, ast.Name)
                 else getattr(node.func, "attr", None))
        # A module-level helper that just returns the service root, e.g.
        # url = f"{base_path(self, self.view_server)}/metadata-elements/{guid}".
        # Its args (self, view_server) are irrelevant here - both already
        # collapse to "" / "{}" - so look it up by name, not by call shape.
        if fname in roots:
            return roots[fname]
        if fname in QUERY_STRING_FUNCS:
            return ""
        # Unwrap URL-normalising wrappers, e.g. str(HttpUrl(f"...")).
        if fname in URL_WRAPPERS and node.args:
            return _flatten(node.args[0], roots)
        # e.g. name.lower() - name the receiver so lint can classify it
        if isinstance(node.func, ast.Attribute):
            return _flatten(node.func.value, roots)
        return "{expr}"
    return "{expr}"


def resolve_roots(tree: ast.AST) -> dict[str, str]:
    """Resolve the service-root URL prefixes assigned in __init__.

    Detected by *value*, not by name: any ``self.<attr>`` assigned a string
    containing ``/open-metadata/`` is a service root. Name-matching missed
    ``self.base_url`` in connection_maker.py, which made all 34 of its
    endpoints report a bogus path mismatch.
    """
    roots: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for t in targets:
            if not (isinstance(t, ast.Attribute)
                    and isinstance(t.value, ast.Name) and t.value.id == "self"
                    and node.value is not None):
                continue
            if t.attr == "platform_url":
                continue
            value = _flatten(node.value, roots)
            if "/open-metadata/" in value or re.search(
                    r"(command_root|command_base|base_path|command_url)$", t.attr):
                roots[t.attr] = value
            # A bare service marker interpolated straight into a URL, e.g.
            # self.url_marker = "governance-officer". Restricted to constants
            # that look like a URL path segment so identity/credential
            # attributes are never substituted into a path.
            elif (URL_SEGMENT_ATTR_RE.search(t.attr)
                  and isinstance(node.value, ast.Constant)
                  and isinstance(node.value.value, str)
                  and URL_SEGMENT_RE.fullmatch(node.value.value)):
                roots[t.attr] = node.value.value
    return roots


def resolve_module_root_funcs(tree: ast.Module) -> dict[str, str]:
    """Resolve module-level helper functions that just return the service root.

    Several modules (metadata_expert, governance_officer, solution_architect)
    define ``def base_path(client, view_server): return f"{client.platform_url}
    /servers/{view_server}/api/open-metadata/<service>"`` and call it as
    ``f"{base_path(self, self.view_server)}/..."``. Its own args are irrelevant
    - only the literal path segments in its return value matter - so this
    resolves by function name for lookup in ``_flatten``'s Call handling.
    """
    funcs: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        returns = [n for n in ast.walk(node) if isinstance(n, ast.Return) and n.value is not None]
        if len(returns) != 1:
            continue
        value = _flatten(returns[0].value, {})
        if "/open-metadata/" in value:
            funcs[node.name] = value
    return funcs


def parse_py_file(filepath: str, helper_verbs: dict[str, str],
                  helper_bodies: dict[str, str] | None = None) -> dict[str, PyMethod]:
    content = open(filepath, encoding="utf-8").read()
    try:
        tree = ast.parse(content)
    except SyntaxError as exc:                      # pragma: no cover
        print(f"  ! skipping {filepath}: {exc}", file=sys.stderr)
        return {}

    roots = resolve_roots(tree)
    roots.update(resolve_module_root_funcs(tree))
    methods: dict[str, PyMethod] = {}
    sync_names: list[str] = []

    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not fn.name.startswith("_async_"):
            if not fn.name.startswith("_"):
                sync_names.append(fn.name)
            continue

        raw_url = path = body_class = None
        direct_verb = helper_verb = helper_body = None
        lint: list[str] = []
        helper_bodies = helper_bodies or {}

        # What the method's own signature claims - the fallback when it does
        # not delegate to a helper.
        for a in list(fn.args.args) + list(fn.args.kwonlyargs):
            if a.arg == "body" and a.annotation is not None:
                names = re.findall(r"\b(\w+RequestBody)\b", ast.unparse(a.annotation))
                if names:
                    body_class = frozenset(names)

        # Local variables assigned a URL prefix inside the method body, rather
        # than in __init__ (resolve_roots only sees self.<attr> assignments
        # there) - covers two shapes seen in the OMVS clients:
        #   base = f"{self.platform_url}/servers/{...}/api/open-metadata/..."
        #   possible_query_params = query_string([...])
        # both later interpolated straight into the url f-string. Scoped to
        # this function only.
        fn_roots = dict(roots)
        for node in ast.walk(fn):
            if not (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)):
                continue
            target = node.targets[0].id
            if isinstance(node.value, ast.Call):
                callee = (node.value.func.id if isinstance(node.value.func, ast.Name) else None)
                if callee in QUERY_STRING_FUNCS:
                    fn_roots[target] = ""
            else:
                value = _flatten(node.value, fn_roots)
                if "/open-metadata/" in value:
                    fn_roots[target] = value

        for node in ast.walk(fn):
            # url = ...
            if (raw_url is None and isinstance(node, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "url" for t in node.targets)):
                raw_url = _flatten(node.value, fn_roots)
                lint = lint_url(raw_url)
                path = canon_path(raw_url)

            # verb: a direct _async_make_request wins over any helper, because
            # some methods first call a GUID-resolution helper (which issues its
            # own unrelated request) before making the real call.
            if isinstance(node, ast.Call):
                fname = (node.func.attr if isinstance(node.func, ast.Attribute)
                         else getattr(node.func, "id", None))
                if fname == "_async_make_request" and node.args:
                    a0 = node.args[0]
                    if direct_verb is None and isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                        direct_verb = a0.value.replace("POST-DATA", "POST").upper()
                elif (fname in helper_verbs
                      and not LOOKUP_HELPER_RE.search(fname or "")):
                    if helper_verb is None:
                        helper_verb = helper_verbs[fname]
                    if helper_body is None and fname in helper_bodies:
                        helper_body = helper_bodies[fname]

        methods[fn.name] = PyMethod(
            name=fn.name, verb=direct_verb or helper_verb, path=path,
            raw_url=raw_url, body_class=helper_body or body_class, lint=lint,
        )

    for sm in sync_names:
        methods.setdefault(sm, PyMethod(sm, None, None, None, None))

    return methods


# --------------------------------------------------------------------------
# audit
# --------------------------------------------------------------------------

def audit(service_filter: str | None, report_path: str, quiet: bool,
          http_dir: str = HTTP_DIR) -> int:
    if not os.path.isdir(http_dir):
        sys.exit(
            f"ERROR: '{http_dir}' not found.\n"
            "This directory is gitignored and holds the audit's ground truth.\n"
            "It is absent in fresh worktrees - point --http-dir (or "
            "PYEGERIA_HTTP_DIR) at a checkout that has it."
        )

    http_files = sorted(glob.glob(f"{http_dir}/Egeria-api-*.http"))
    extra = f"{http_dir}/Egeria-platform-services.http"
    if os.path.exists(extra):
        http_files.append(extra)
    if not http_files:
        sys.exit(f"ERROR: no .http collections found under '{http_dir}'.")

    helper_verbs = discover_helper_verbs(SERVER_CLIENT)
    helper_bodies = discover_helper_bodies(SERVER_CLIENT)

    http_by_service = {}
    for hf in http_files:
        svc = (os.path.basename(hf)
               .replace("Egeria-api-", "").replace("Egeria-", "").replace(".http", ""))
        http_by_service[svc] = parse_http_file(hf)

    py_by_service = {}
    for pf in sorted(glob.glob(f"{OMVS_DIR}/*.py")):
        svc = os.path.basename(pf).replace(".py", "").replace("_omvs", "").replace("_", "-")
        py_by_service[svc] = parse_py_file(pf, helper_verbs, helper_bodies)

    # feedback-manager has no dedicated pyegeria/omvs/*.py module - Egeria's
    # comment/tag/like/rating/note-log API is implemented once, directly on
    # the shared ServerClient base class in _server_client.py, and inherited
    # by every OMVS subclient rather than duplicated per-module. Merge those
    # methods into the feedback-manager bucket so they're checked as that
    # service's own coverage, not reported as an entire missing module.
    if os.path.exists(SERVER_CLIENT):
        shared = parse_py_file(SERVER_CLIENT, helper_verbs, helper_bodies)
        py_by_service.setdefault("feedback-manager", {}).update(shared)

    flat = {m: (svc, d) for svc, ms in py_by_service.items() for m, d in ms.items()}

    # Reverse index: (verb, path) -> [(svc, method_name), ...]. Name-based
    # matching misses methods that exist and are correctly wired but whose
    # snake_case name doesn't resemble the .http @name at all (e.g. ground
    # truth's "addSecurityTags" implemented as set_security_tags_classification).
    # This catches those before they're wrongly reported MISSING.
    by_path: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    for svc, ms in py_by_service.items():
        for m, d in ms.items():
            if d.verb and d.path:
                by_path[(d.verb, d.path)].append((svc, m))

    counts = defaultdict(int)
    lines: list[str] = []
    defects = 0

    # ---- lint pass -------------------------------------------------------
    lint_rows = []
    for svc, ms in py_by_service.items():
        if service_filter and service_filter != svc:
            continue
        for m, d in ms.items():
            for problem in d.lint:
                lint_rows.append(f"- `{svc}.py` `{m}`: {problem}\n      `{d.raw_url}`")
    if lint_rows:
        lines.append("## URL Lint (malformed SDK URLs)\n")
        lines.extend(lint_rows)
        lines.append("")
        defects += len(lint_rows)
        counts["lint"] = len(lint_rows)

    # ---- duplicate pass --------------------------------------------------
    dupes = defaultdict(list)
    for svc, ms in py_by_service.items():
        for m, d in ms.items():
            if d.path and d.verb:
                dupes[f"{d.verb} {d.path}"].append((svc, m))
    dupe_rows = []
    for key, occ in sorted(dupes.items()):
        if len(occ) > 1 and key not in EXPECTED_DUPLICATE_PATHS:
            dupe_rows.append(f"- `{key}`")
            dupe_rows += [f"  - `{s}.py`: `{m}`" for s, m in occ]
    if dupe_rows:
        lines.append("## Duplicate endpoints (same verb + path)\n")
        lines.append("_Review only - cross-service overlap is often intentional._\n")
        lines.extend(dupe_rows)
        lines.append("")

    # ---- coverage pass ---------------------------------------------------
    for svc, requests in sorted(http_by_service.items()):
        if svc in SKIP_SERVICES:
            continue
        if service_filter and service_filter != svc:
            continue

        lines.append(f"\n### Service: {svc}\n")
        py_methods = py_by_service.get(svc, {})

        for name, req in requests.items():
            if name == "Token":
                continue
            snake = to_snake(name)
            cands = [snake, f"_async_{snake}"]
            for prefix in ("glossary_", "asset_", "location_", "project_",
                           "collection_", "actor_"):
                if snake.startswith(prefix):
                    stem = snake[len(prefix):]
                    cands += [stem, f"_async_{stem}"]
            if snake in NAME_OVERRIDES:
                ov = NAME_OVERRIDES[snake]
                cands += [ov, f"_async_{ov}"]

            match = next((c for c in cands if c in py_methods), None)

            if not match:
                elsewhere = next((c for c in cands if c in flat), None)
                by_path_hit = by_path.get((req.verb, req.path))
                if elsewhere:
                    counts["elsewhere"] += 1
                    lines.append(f"- {name}: ELSEWHERE -> `{flat[elsewhere][0]}.py`")
                elif by_path_hit:
                    counts["renamed"] += 1
                    hits = ", ".join(f"`{s}.py`:`{m}`" for s, m in by_path_hit)
                    lines.append(f"- {name}: RENAMED -> {hits}")
                else:
                    counts["missing"] += 1
                    lines.append(f"- {name}: MISSING  (`{req.verb} {req.path}`)")
                continue

            check = match if match.startswith("_async_") else f"_async_{match}"
            d = py_methods.get(check) or py_methods[match]

            issues = []
            if d.verb and d.verb != req.verb:
                issues.append(f"VERB {d.verb} != {req.verb}")
            if d.path and d.path != req.path:
                issues.append(f"PATH\n      SDK: {d.path}\n      API: {req.path}")
            # Mismatch only when the documented class is not among those the
            # SDK path accepts (several helpers accept a union).
            if (d.body_class and req.body_class
                    and "RequestBody" in req.body_class
                    and req.body_class not in d.body_class):
                issues.append(
                    f"BODY sends {'|'.join(sorted(d.body_class))} != {req.body_class}")

            if issues:
                counts["mismatch"] += 1
                defects += 1
                lines.append(f"- {name}: MISMATCH `{match}`")
                lines += [f"    - {i}" for i in issues]
            else:
                counts["ok"] += 1
                if not quiet:
                    lines.append(f"- {name}: OK")

    header = [
        "# OMVS Audit Report",
        "",
        f"Ground truth: `{HTTP_DIR}` ({len(http_files)} collections)",
        f"Subject: `{OMVS_DIR}` ({len(py_by_service)} modules)",
        "",
        "| Result | Count |",
        "|---|---|",
        f"| OK | {counts['ok']} |",
        f"| Mismatch (verb/path/body) | {counts['mismatch']} |",
        f"| Missing | {counts['missing']} |",
        f"| Renamed (implemented, verb+path matches under a different name) | {counts['renamed']} |",
        f"| Found in another module | {counts['elsewhere']} |",
        f"| URL lint | {counts['lint']} |",
        "",
    ]

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(header + lines) + "\n")

    print(f"Audit complete -> {report_path}")
    print(f"  OK={counts['ok']} mismatch={counts['mismatch']} "
          f"missing={counts['missing']} elsewhere={counts['elsewhere']} "
          f"lint={counts['lint']}")
    return 1 if defects else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", default="omvs_audit_report.md", help="output path")
    ap.add_argument("--service", help="audit a single service, e.g. location-arena")
    ap.add_argument("--quiet", action="store_true", help="omit OK rows from the report")
    ap.add_argument(
        "--http-dir",
        default=os.environ.get("PYEGERIA_HTTP_DIR", HTTP_DIR),
        help="path to the .http ground-truth collections (gitignored; "
             "defaults to $PYEGERIA_HTTP_DIR or the in-repo location)",
    )
    args = ap.parse_args()
    return audit(args.service, args.report, args.quiet, args.http_dir)


if __name__ == "__main__":
    sys.exit(main())
