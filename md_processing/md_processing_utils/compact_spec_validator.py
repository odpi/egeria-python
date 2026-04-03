"""Validation helpers for compact command specification files used by Dr.Egeria."""

from __future__ import annotations

import importlib
import inspect
import json
import pkgutil
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


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

    for module_info in pkgutil.iter_modules(omvs_pkg.__path__):
        module = importlib.import_module(f"pyegeria.omvs.{module_info.name}")
        for class_name, class_obj in inspect.getmembers(module, inspect.isclass):
            if class_obj.__module__ == module.__name__:
                classes[class_name] = class_obj

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
                message=f"Class '{class_name}' was not found in pyegeria.omvs",
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


def validate_compact_spec_file(file_path: str | Path) -> list[SpecFinding]:
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
            rows.append(
                {
                    "file_path": str(file_path),
                    "command_name": str(command_name),
                    "derived_processing_type": derived_type,
                }
            )

    rows.sort(key=lambda r: (Path(r["file_path"]).name.lower(), r["command_name"].lower()))
    return rows


def validate_compact_specs(path: str | Path) -> list[SpecFinding]:
    target = Path(path)
    if target.is_file():
        return validate_compact_spec_file(target)

    findings: list[SpecFinding] = []
    seen_commands: dict[str, str] = {}

    for file_path in sorted(target.glob("*.json")):
        file_findings = validate_compact_spec_file(file_path)
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

