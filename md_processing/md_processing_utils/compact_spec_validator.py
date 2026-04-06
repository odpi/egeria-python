"""Validation helpers for compact command specification files used by Dr.Egeria."""

from __future__ import annotations

import importlib
import inspect
import json
import pkgutil
import re
from urllib.parse import urlparse
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from pyegeria.omvs.valid_metadata import ValidMetadataManager


_SUPPORTED_PROCESSOR_TYPE_KEYS = {"metadata_element_type", "metadata_element_types"}
_FIND_METHOD_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class SpecFinding:
    severity: str  # "ERROR" | "WARNING"
    file_path: str
    command_name: str
    code: str
    message: str


def _parse_find_constraints(raw_constraints: Any) -> tuple[dict[str, Any], list[SpecFinding]]:
    findings: list[SpecFinding] = []
    if raw_constraints in (None, ""):
        return {}, findings
    if isinstance(raw_constraints, dict):
        return raw_constraints, findings
    if not isinstance(raw_constraints, str):
        findings.append(
            SpecFinding(
                severity="ERROR",
                file_path="",
                command_name="",
                code="FIND_CONSTRAINTS_TYPE_INVALID",
                message=f"find_constraints must be a dict or JSON string, got {type(raw_constraints).__name__}",
            )
        )
        return {}, findings

    text = raw_constraints.strip()
    if not text:
        return {}, findings

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        findings.append(
            SpecFinding(
                severity="ERROR",
                file_path="",
                command_name="",
                code="FIND_CONSTRAINTS_JSON_INVALID",
                message=f"find_constraints is not valid JSON: {exc.msg}",
            )
        )
        return {}, findings

    if not isinstance(parsed, dict):
        findings.append(
            SpecFinding(
                severity="ERROR",
                file_path="",
                command_name="",
                code="FIND_CONSTRAINTS_JSON_NOT_OBJECT",
                message="find_constraints JSON must decode to an object/dict",
            )
        )
        return {}, findings

    return parsed, findings


def _derive_object_type(command_name: str) -> str:
    parts = command_name.split(" ", 1)
    return parts[1] if len(parts) == 2 else ""


def derive_processing_type_name(command_name: str, find_constraints: dict[str, Any]) -> str:
    """Mirror AsyncBaseCommandProcessor type derivation behavior."""
    single = find_constraints.get("metadata_element_type")
    if isinstance(single, str) and single.strip():
        return single.strip()

    multi = find_constraints.get("metadata_element_types", [])
    if isinstance(multi, list):
        for candidate in multi:
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()

    object_type = _derive_object_type(command_name)
    words = [w for w in re.split(r"[^A-Za-z0-9]+", object_type) if w]
    if words:
        return "".join(w[0].upper() + w[1:] for w in words)
    return object_type


def _validate_type_keys(find_constraints: dict[str, Any]) -> list[SpecFinding]:
    findings: list[SpecFinding] = []

    single = find_constraints.get("metadata_element_type")
    multi = find_constraints.get("metadata_element_types")

    if "metadata_element_type" in find_constraints:
        if not isinstance(single, str) or not single.strip():
            findings.append(
                SpecFinding(
                    severity="ERROR",
                    file_path="",
                    command_name="",
                    code="METADATA_ELEMENT_TYPE_INVALID",
                    message="metadata_element_type must be a non-empty string",
                )
            )

    valid_multi: list[str] = []
    if "metadata_element_types" in find_constraints:
        if not isinstance(multi, list) or not multi:
            findings.append(
                SpecFinding(
                    severity="ERROR",
                    file_path="",
                    command_name="",
                    code="METADATA_ELEMENT_TYPES_INVALID",
                    message="metadata_element_types must be a non-empty list of strings",
                )
            )
        else:
            for item in multi:
                if isinstance(item, str) and item.strip():
                    valid_multi.append(item.strip())
                else:
                    findings.append(
                        SpecFinding(
                            severity="ERROR",
                            file_path="",
                            command_name="",
                            code="METADATA_ELEMENT_TYPES_ITEM_INVALID",
                            message="metadata_element_types contains a non-string or empty value",
                        )
                    )

            # metadata_element_types with a single value is legal, but less clear than metadata_element_type.
            if len(valid_multi) == 1:
                findings.append(
                    SpecFinding(
                        severity="WARNING",
                        file_path="",
                        command_name="",
                        code="METADATA_ELEMENT_TYPES_SINGLETON",
                        message="metadata_element_types has one value; metadata_element_type is clearer",
                    )
                )
            elif len(valid_multi) > 1:
                findings.append(
                    SpecFinding(
                        severity="WARNING",
                        file_path="",
                        command_name="",
                        code="METADATA_ELEMENT_TYPES_FIRST_ONLY",
                        message="processing currently uses only the first metadata_element_types entry",
                    )
                )

    if isinstance(single, str) and single.strip() and valid_multi and single.strip() != valid_multi[0]:
        findings.append(
            SpecFinding(
                severity="WARNING",
                file_path="",
                command_name="",
                code="METADATA_ELEMENT_TYPE_CONFLICT",
                message=(
                    "metadata_element_type and metadata_element_types[0] differ; "
                    "processing resolves metadata_element_type first"
                ),
            )
        )

    ignored = sorted(k for k in find_constraints.keys() if k not in _SUPPORTED_PROCESSOR_TYPE_KEYS)
    if ignored:
        findings.append(
            SpecFinding(
                severity="WARNING",
                file_path="",
                command_name="",
                code="FIND_CONSTRAINTS_KEYS_IGNORED_BY_PROCESSING",
                message=(
                    "processing only uses metadata_element_type / metadata_element_types; "
                    f"other keys ignored: {', '.join(ignored)}"
                ),
            )
        )

    return findings


@lru_cache(maxsize=1)
def _load_omvs_classes() -> dict[str, type]:
    classes: dict[str, type] = {}
    import pyegeria.omvs as omvs_pkg
    from pyegeria.core._server_client import ServerClient

    for module_info in pkgutil.iter_modules(omvs_pkg.__path__):
        module = importlib.import_module(f"pyegeria.omvs.{module_info.name}")
        for class_name, class_obj in inspect.getmembers(module, inspect.isclass):
            if class_obj.__module__ == module.__name__:
                classes[class_name] = class_obj

    # Some compact specs legitimately reference core client methods.
    classes["ServerClient"] = ServerClient

    return classes


def _validate_find_method(command_spec: dict[str, Any]) -> list[SpecFinding]:
    findings: list[SpecFinding] = []
    raw_find_method = command_spec.get("find_method", "")

    if raw_find_method in (None, ""):
        return findings

    if not isinstance(raw_find_method, str):
        findings.append(
            SpecFinding(
                severity="ERROR",
                file_path="",
                command_name="",
                code="FIND_METHOD_INVALID_TYPE",
                message="find_method must be a string when provided",
            )
        )
        return findings

    find_method = raw_find_method.strip()
    if not _FIND_METHOD_PATTERN.match(find_method):
        findings.append(
            SpecFinding(
                severity="WARNING",
                file_path="",
                command_name="",
                code="FIND_METHOD_FORMAT_UNEXPECTED",
                message="find_method should look like 'ClassName.method_name'",
            )
        )
        return findings

    class_name, method_name = find_method.split(".", 1)
    classes = _load_omvs_classes()
    class_obj = classes.get(class_name)
    if class_obj is None:
        findings.append(
            SpecFinding(
                severity="ERROR",
                file_path="",
                command_name="",
                code="FIND_METHOD_CLASS_NOT_FOUND",
                message=f"Class '{class_name}' was not found in pyegeria.omvs or pyegeria.core",
            )
        )
        return findings

    if not hasattr(class_obj, method_name):
        findings.append(
            SpecFinding(
                severity="ERROR",
                file_path="",
                command_name="",
                code="FIND_METHOD_METHOD_NOT_FOUND",
                message=f"Method '{method_name}' was not found on class '{class_name}'",
            )
        )

    return findings


def _extract_typedef_names(type_defs: Any) -> set[str]:
    """Extract canonical TypeDef names from Valid Metadata API responses."""
    names: set[str] = set()
    if isinstance(type_defs, str):
        return names

    entries: list[Any] = []

    def _collect_entries(node: Any) -> None:
        if isinstance(node, list):
            for item in node:
                _collect_entries(item)
            return
        if not isinstance(node, dict):
            return
        if "name" in node and isinstance(node.get("name"), str):
            entries.append(node)
        for key in ("typeDefList", "typeDefs", "elements"):
            value = node.get(key)
            if isinstance(value, list):
                _collect_entries(value)

    _collect_entries(type_defs)

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        if isinstance(name, str) and name.strip():
            names.add(name.strip())
    return names


def _extract_typedef_names_by_category(type_defs: Any, allowed_categories: set[str]) -> set[str]:
    """Extract TypeDef names filtered by category/class from mixed type-def payloads."""
    names: set[str] = set()
    if isinstance(type_defs, str):
        return names

    entries: list[Any] = []

    def _collect_entries(node: Any) -> None:
        if isinstance(node, list):
            for item in node:
                _collect_entries(item)
            return
        if not isinstance(node, dict):
            return
        if "name" in node and isinstance(node.get("name"), str):
            entries.append(node)
        for key in ("typeDefList", "typeDefs", "elements"):
            value = node.get(key)
            if isinstance(value, list):
                _collect_entries(value)

    _collect_entries(type_defs)

    allowed = {c.upper() for c in allowed_categories}
    for entry in entries:
        if not isinstance(entry, dict):
            continue

        category = str(entry.get("category", "")).strip().upper()
        class_name = str(entry.get("class", ""))
        category_flat = category.replace("_", "").replace(" ", "")
        class_flat = class_name.lower()
        is_entity = (
            category in {"ENTITY_DEF", "ENTITYDEF"}
            or category_flat == "ENTITYDEF"
            or class_flat.endswith("entitydef")
        )
        is_relationship = (
            category in {"RELATIONSHIP_DEF", "RELATIONSHIPDEF"}
            or category_flat == "RELATIONSHIPDEF"
            or class_flat.endswith("relationshipdef")
        )
        is_classification = (
            category in {"CLASSIFICATION_DEF", "CLASSIFICATIONDEF"}
            or category_flat == "CLASSIFICATIONDEF"
            or class_flat.endswith("classificationdef")
        )

        if ("ENTITY_DEF" in allowed and is_entity) or (
            "RELATIONSHIP_DEF" in allowed and is_relationship
        ) or (
            "CLASSIFICATION_DEF" in allowed and is_classification
        ):
            name = entry.get("name")
            if isinstance(name, str) and name.strip():
                names.add(name.strip())

    return names


def _normalize_bearer_token(raw_token: Any) -> str:
    """Return a sanitized token string suitable for Authorization headers."""
    if not isinstance(raw_token, str):
        return ""

    token = raw_token.strip()
    if len(token) >= 2 and token[0] == token[-1] and token[0] in {'"', "'"}:
        token = token[1:-1].strip()

    return token


def _should_warn_missing_om_type(command_name: str, command_spec: dict[str, Any]) -> bool:
    """Return False for command forms where OM_TYPE is intentionally omitted."""
    family = str(command_spec.get("family", "")).strip().lower()
    find_method = str(command_spec.get("find_method", "")).strip().lower()
    command_l = command_name.strip().lower()

    # Report commands are formatter-driven and may not bind to a single type.
    if family == "report" or command_l == "report":
        return False

    # Dynamic relationship commands can defer the concrete type to command attributes.
    if find_method == "name":
        return False

    return True


def fetch_valid_om_types(
    server: str,
    url: str,
    user_id: str | None,
    user_pwd: str | None,
) -> set[str]:
    """Fetch valid entity/relationship/classification type names from Egeria."""
    diagnostics: list[str] = []

    def _fetch_once(target_url: str) -> set[str]:
        client = ValidMetadataManager(server, target_url, user_id=user_id, user_pwd=user_pwd)
        try:
            if user_id and user_pwd:
                # Valid metadata endpoints are commonly token-protected in local Egeria setups.
                raw_token = client.create_egeria_bearer_token(user_id, user_pwd)
                token = _normalize_bearer_token(raw_token)
                if not token or token.upper() == "FAILED":
                    raise RuntimeError(
                        "Failed to create a usable bearer token for valid metadata OM type fetch"
                    )
                # Ensure outgoing auth header uses normalized token content.
                client.set_bearer_token(token)

            entity_defs = client.get_all_entity_defs(output_format="JSON")
            relationship_defs = client.get_all_relationship_defs(output_format="JSON")
            classification_defs = client.get_all_classification_defs(output_format="JSON")

            entity_names = _extract_typedef_names(entity_defs)
            relationship_names = _extract_typedef_names(relationship_defs)
            classification_names = _extract_typedef_names(classification_defs)

            # Fallback: some environments return empty split endpoints but populate combined type-def endpoint.
            if not entity_names or not relationship_names or not classification_names:
                all_types = client.get_all_entity_types(output_format="JSON")
                if not entity_names:
                    entity_names = _extract_typedef_names_by_category(all_types, {"ENTITY_DEF"})
                if not relationship_names:
                    relationship_names = _extract_typedef_names_by_category(all_types, {"RELATIONSHIP_DEF"})
                if not classification_names:
                    classification_names = _extract_typedef_names_by_category(all_types, {"CLASSIFICATION_DEF"})
            diagnostics.append(
                f"url={target_url} entity_count={len(entity_names)} relationship_count={len(relationship_names)} classification_count={len(classification_names)}"
            )
            return entity_names | relationship_names | classification_names
        finally:
            client.close_session()

    discovered = _fetch_once(url)
    if discovered:
        return discovered

    parsed = urlparse(url)
    host = parsed.hostname or ""
    if host not in {"localhost", "127.0.0.1"}:
        raise RuntimeError(
            "Zero OM types discovered from valid metadata APIs. "
            + " | ".join(diagnostics)
        )

    alternate_host = "127.0.0.1" if host == "localhost" else "localhost"
    alternate_url = url.replace(host, alternate_host, 1)
    discovered = _fetch_once(alternate_url)
    if discovered:
        return discovered

    raise RuntimeError(
        "Zero OM types discovered from valid metadata APIs. "
        + " | ".join(diagnostics)
    )


def validate_compact_spec_file(
    file_path: str | Path,
    valid_om_types: set[str] | None = None,
    validate_derived_match: bool = False,
) -> list[SpecFinding]:
    path = Path(file_path)
    findings: list[SpecFinding] = []

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [
            SpecFinding(
                severity="ERROR",
                file_path=str(path),
                command_name="",
                code="FILE_READ_OR_JSON_ERROR",
                message=str(exc),
            )
        ]

    commands = payload.get("commands", {}) if isinstance(payload, dict) else {}
    if not isinstance(commands, dict):
        return [
            SpecFinding(
                severity="ERROR",
                file_path=str(path),
                command_name="",
                code="COMMANDS_SECTION_INVALID",
                message="Expected 'commands' to be a dictionary",
            )
        ]

    for command_name, command_spec in commands.items():
        if not isinstance(command_spec, dict):
            findings.append(
                SpecFinding(
                    severity="ERROR",
                    file_path=str(path),
                    command_name=str(command_name),
                    code="COMMAND_SPEC_INVALID",
                    message="Command definition must be a dictionary",
                )
            )
            continue

        parsed, parse_findings = _parse_find_constraints(command_spec.get("find_constraints"))
        for f in parse_findings:
            findings.append(
                SpecFinding(
                    severity=f.severity,
                    file_path=str(path),
                    command_name=str(command_name),
                    code=f.code,
                    message=f.message,
                )
            )

        if parsed:
            for f in _validate_type_keys(parsed):
                findings.append(
                    SpecFinding(
                        severity=f.severity,
                        file_path=str(path),
                        command_name=str(command_name),
                        code=f.code,
                        message=f.message,
                    )
                )

        derived_type = derive_processing_type_name(str(command_name), parsed)
        raw_om_type = command_spec.get("OM_TYPE")
        om_type = raw_om_type.strip() if isinstance(raw_om_type, str) else ""
        if not om_type:
            if _should_warn_missing_om_type(str(command_name), command_spec):
                findings.append(
                    SpecFinding(
                        severity="WARNING",
                        file_path=str(path),
                        command_name=str(command_name),
                        code="OM_TYPE_MISSING",
                        message="OM_TYPE is missing; include it to align specs with runtime type resolution",
                    )
                )
        else:
            if om_type.upper() == "CLASSIFICATION":
                findings.append(
                    SpecFinding(
                        severity="WARNING",
                        file_path=str(path),
                        command_name=str(command_name),
                        code="OM_TYPE_CLASSIFICATION_PLACEHOLDER",
                        message=(
                            "OM_TYPE uses placeholder 'CLASSIFICATION'; runtime classification name should come "
                            "from command attributes"
                        ),
                    )
                )
            elif valid_om_types is not None and om_type not in valid_om_types:
                findings.append(
                    SpecFinding(
                        severity="ERROR",
                        file_path=str(path),
                        command_name=str(command_name),
                        code="OM_TYPE_INVALID",
                        message=(
                            f"OM_TYPE '{om_type}' is not a valid Egeria entity/relationship/classification type "
                            "from get_all_entity_defs/get_all_relationship_defs/get_all_classification_defs"
                        ),
                    )
                )

        if validate_derived_match and om_type and derived_type and om_type != derived_type:
            findings.append(
                SpecFinding(
                    severity="ERROR",
                    file_path=str(path),
                    command_name=str(command_name),
                    code="OM_TYPE_MISMATCH",
                    message=(
                        f"OM_TYPE '{om_type}' does not match derived processing type "
                        f"'{derived_type}'"
                    ),
                )
            )

        for f in _validate_find_method(command_spec):
            findings.append(
                SpecFinding(
                    severity=f.severity,
                    file_path=str(path),
                    command_name=str(command_name),
                    code=f.code,
                    message=f.message,
                )
            )

    return findings


def collect_derived_processing_types(path: str | Path) -> list[dict[str, str]]:
    """Return derived processing type name per command for validator reporting."""
    target = Path(path)
    file_paths = [target] if target.is_file() else sorted(target.glob("*.json"))
    rows: list[dict[str, str]] = []

    for file_path in file_paths:
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        commands = payload.get("commands", {}) if isinstance(payload, dict) else {}
        if not isinstance(commands, dict):
            continue

        for command_name, command_spec in commands.items():
            if not isinstance(command_spec, dict):
                continue
            parsed, _ = _parse_find_constraints(command_spec.get("find_constraints"))
            derived_type = derive_processing_type_name(str(command_name), parsed)
            om_type = command_spec.get("OM_TYPE")
            rows.append(
                {
                    "file_path": str(file_path),
                    "command_name": str(command_name),
                    "om_type": om_type.strip() if isinstance(om_type, str) else "",
                    "derived_processing_type": derived_type,
                }
            )

    rows.sort(key=lambda r: (Path(r["file_path"]).name.lower(), r["command_name"].lower()))
    return rows


def validate_compact_specs(
    path: str | Path,
    valid_om_types: set[str] | None = None,
    validate_derived_match: bool = False,
) -> list[SpecFinding]:
    target = Path(path)
    if target.is_file():
        return validate_compact_spec_file(
            target,
            valid_om_types=valid_om_types,
            validate_derived_match=validate_derived_match,
        )

    findings: list[SpecFinding] = []
    seen_commands: dict[str, str] = {}

    for file_path in sorted(target.glob("*.json")):
        file_findings = validate_compact_spec_file(
            file_path,
            valid_om_types=valid_om_types,
            validate_derived_match=validate_derived_match,
        )
        findings.extend(file_findings)

        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
            commands = payload.get("commands", {}) if isinstance(payload, dict) else {}
            if isinstance(commands, dict):
                for command_name in commands.keys():
                    prior = seen_commands.get(command_name)
                    if prior and prior != str(file_path):
                        findings.append(
                            SpecFinding(
                                severity="WARNING",
                                file_path=str(file_path),
                                command_name=str(command_name),
                                code="DUPLICATE_COMMAND_NAME",
                                message=f"Command also defined in {Path(prior).name}",
                            )
                        )
                    else:
                        seen_commands[command_name] = str(file_path)
        except Exception:
            # Parsing errors are already captured by validate_compact_spec_file.
            pass

    return findings

