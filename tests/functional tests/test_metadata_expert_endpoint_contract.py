"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Static contract checks for MetadataExpert endpoint templates.

This test compares URL templates built in `pyegeria/omvs/metadata_expert.py`
with endpoint templates declared in
`pyegeria/http clients/Egeria-api-metadata-expert.http`.

Behavior:
- Path mismatches fail the test.
- Query mismatches are tolerated (optional), but listed for review.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
EXPERT_FILE = ROOT / "pyegeria" / "omvs" / "metadata_expert.py"
HTTP_CONTRACT_FILE = ROOT / "pyegeria" / "http clients" / "Egeria-api-metadata-expert.http"

# Optional tolerance: do not fail on query mismatches, only list them.
TOLERATE_QUERY_MISMATCH = True

_BASE_MARKER = "{BASE}"
_PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}|\{[^}]+\}")


def _normalize_token(value: str) -> str:
    """Normalize placeholders and dynamic fragments to a stable token form."""
    value = value.strip()
    return _PLACEHOLDER_RE.sub("{X}", value)


def _split_path_query(value: str) -> Tuple[str, str]:
    if "?" in value:
        path, query = value.split("?", 1)
        return path, query
    return value, ""


def _expr_to_template(node: ast.AST) -> str:
    """Render a URL expression AST node to a normalized template string."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value

    if isinstance(node, ast.JoinedStr):
        parts: List[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                inner = value.value
                if isinstance(inner, ast.Attribute) and inner.attr == "command_root":
                    parts.append(_BASE_MARKER)
                elif isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name) and inner.func.id == "base_path":
                    parts.append(_BASE_MARKER)
                else:
                    parts.append("{X}")
        return "".join(parts)

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _expr_to_template(node.left)
        right = _expr_to_template(node.right)
        return f"{left}{right}"

    return ""


def _extract_metadata_expert_url_templates() -> Dict[str, Set[str]]:
    """Return method->set(endpoint suffix templates) from metadata_expert.py."""
    source = EXPERT_FILE.read_text(encoding="utf-8")
    module = ast.parse(source)
    results: Dict[str, Set[str]] = {}

    metadata_expert_cls = None
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == "MetadataExpert":
            metadata_expert_cls = node
            break

    if metadata_expert_cls is None:
        return results

    for func in metadata_expert_cls.body:
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        for child in ast.walk(func):
            if not isinstance(child, ast.Assign):
                continue

            targets = [t.id for t in child.targets if isinstance(t, ast.Name)]
            if "url" not in targets:
                continue

            template = _expr_to_template(child.value)
            if not template:
                continue

            if "/api/open-metadata/metadata-expert" in template:
                suffix = template.split("/api/open-metadata/metadata-expert", 1)[1]
            elif template.startswith(_BASE_MARKER):
                suffix = template[len(_BASE_MARKER) :]
            else:
                continue

            results.setdefault(func.name, set()).add(suffix)

    return results


def _extract_contract_suffix_templates() -> Set[str]:
    """Extract endpoint suffix templates from the metadata-expert .http contract file."""
    source = HTTP_CONTRACT_FILE.read_text(encoding="utf-8")
    # Match request lines like:
    # POST {{baseURL}}/servers/{{viewServer}}/api/open-metadata/metadata-expert/...
    return set(
        re.findall(
            r"^\s*(?:GET|POST)\s+\{\{baseURL\}\}/servers/\{\{viewServer\}\}/api/open-metadata/metadata-expert([^\s]*)",
            source,
            flags=re.MULTILINE,
        )
    )


def _build_contract_index(contract_suffixes: Set[str]) -> Dict[str, Set[str]]:
    """Create normalized path->query index for contract endpoints."""
    index: Dict[str, Set[str]] = {}
    for suffix in contract_suffixes:
        path, query = _split_path_query(suffix)
        npath = _normalize_token(path)
        nquery = _normalize_token(query)
        index.setdefault(npath, set()).add(nquery)
    return index


def _compare_templates() -> dict:
    method_templates = _extract_metadata_expert_url_templates()
    contract_suffixes = _extract_contract_suffix_templates()
    contract_index = _build_contract_index(contract_suffixes)

    path_mismatches: List[Tuple[str, str]] = []
    query_mismatches: List[Tuple[str, str, str]] = []

    for method_name, templates in method_templates.items():
        for suffix in sorted(templates):
            path, query = _split_path_query(suffix)
            npath = _normalize_token(path)
            nquery = _normalize_token(query)

            if npath not in contract_index:
                path_mismatches.append((method_name, suffix))
                continue

            if nquery and nquery not in contract_index[npath]:
                query_mismatches.append((method_name, suffix, ", ".join(sorted(contract_index[npath]))))

    return {
        "method_templates": method_templates,
        "contract_suffixes": contract_suffixes,
        "path_mismatches": path_mismatches,
        "query_mismatches": query_mismatches,
    }


def test_metadata_expert_endpoint_paths_match_contract():
    report = _compare_templates()

    # Basic sanity check to ensure the extractor sees substantial coverage.
    discovered = sum(len(v) for v in report["method_templates"].values())
    assert discovered >= 20, "Endpoint extractor found too few URL templates; check parser logic."

    mismatches = report["path_mismatches"]
    assert not mismatches, (
        "MetadataExpert path mismatches vs HTTP contract:\n"
        + "\n".join(f"- {method}: {template}" for method, template in mismatches)
    )


def test_metadata_expert_endpoint_query_mismatches_report_only():
    report = _compare_templates()
    query_mismatches = report["query_mismatches"]

    if query_mismatches:
        print("Potential query mismatches (review list):")
        for method, template, expected in query_mismatches:
            print(f"- {method}: {template} | contract query options: {expected}")

    if not TOLERATE_QUERY_MISMATCH:
        assert not query_mismatches, (
            "MetadataExpert query mismatches vs HTTP contract:\n"
            + "\n".join(
                f"- {method}: {template} | expected query options: {expected}"
                for method, template, expected in query_mismatches
            )
        )

