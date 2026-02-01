from __future__ import annotations

from typing import Iterable

from md_processing.command_mapping import setup_dispatcher
from md_processing.md_processing_utils.common_md_proc_utils import (
    EGERIA_USAGE_LEVEL,
    parse_upsert_command,
    parse_view_command,
)
from md_processing.md_processing_utils.common_md_utils import split_tb_string
from md_processing.md_processing_utils.extraction_utils import extract_command_plus
from md_processing.md_processing_utils.md_processing_constants import COMMAND_DEFINITIONS, get_command_spec


class FakeEgeriaClient:
    def __init__(self, exists: bool | None = None) -> None:
        self._exists = exists

    def get_elements_by_property_value(self, element_name, property_names, open_metadata_type_name=None):
        if not element_name:
            return "No elements found"
        if self._exists is False:
            return "No elements found"
        if self._exists is True:
            return [{
                "elementHeader": {"guid": f"guid::{element_name}"},
                "properties": {"qualifiedName": f"qn::{element_name}", "displayName": element_name},
            }]
        if str(element_name).startswith("NEW "):
            return "No elements found"
        return [{
            "elementHeader": {"guid": f"guid::{element_name}"},
            "properties": {"qualifiedName": f"qn::{element_name}", "displayName": element_name},
        }]

    def __create_qualified_name__(self, *parts):
        return "::".join([str(part) for part in parts if part is not None])

    def __get_guid__(self, qualified_name=None):
        return f"guid::{qualified_name}"


def commands_for_module(module_name: str) -> list[str]:
    dispatcher = setup_dispatcher()
    return sorted([
        command
        for command, handler in dispatcher._registry.items()
        if getattr(handler, "__module__", "") == module_name
    ])


def build_command_block(command: str) -> str | None:
    spec, status = resolve_command_spec(command)
    if status != "ok":
        return None
    attributes = spec.get("Attributes", [])

    action, _ = _split_command(command)
    lines = [f"# {command}"]

    for attr in attributes:
        for key, meta in attr.items():
            if not meta.get("input_required", False):
                continue
            if not _is_supported_attribute(meta, action):
                continue
            lines.append(f"## {key}")
            lines.append(_value_for_attribute(meta, key, action))

    lines.append("___")
    return "\n".join(lines)


def required_attribute_keys(command: str) -> list[str]:
    spec, status = resolve_command_spec(command)
    if status != "ok":
        return []
    attributes = spec.get("Attributes", [])
    action, _ = _split_command(command)

    required_keys = []
    for attr in attributes:
        for key, meta in attr.items():
            if meta.get("input_required", False) and _is_supported_attribute(meta, action):
                required_keys.append(key)
    return required_keys


def parse_command(command: str, txt: str, client: FakeEgeriaClient) -> dict | None:
    _, object_type, action = extract_command_plus(txt)
    if action in ["Create", "Update"]:
        return parse_upsert_command(client, object_type, action, txt)
    return parse_view_command(client, object_type, action, txt)


def _is_supported_attribute(meta: dict, action: str) -> bool:
    if action == "Update" and meta.get("inUpdate", True) is False:
        return False
    level = meta.get("level", "Basic")
    if EGERIA_USAGE_LEVEL == "Basic" and level != "Basic":
        return False
    if EGERIA_USAGE_LEVEL == "Advanced" and level in ["Expert", "Invisible"]:
        return False
    if EGERIA_USAGE_LEVEL == "Expert" and level == "Invisible":
        return False
    return True


def _value_for_attribute(meta: dict, key: str, action: str) -> str:
    style = meta.get("style", "Simple")
    if style in ["Simple Int", "Ordered Int"]:
        return "1"
    if style in ["Simple List", "Reference Name List"]:
        return "Existing One; Existing Two"
    if style in ["Dictionary", "Named DICT", "Dictionary List"]:
        return "key: value"
    if style == "Valid Value":
        valid_values = meta.get("valid_values", "")
        values = split_tb_string(valid_values) if valid_values else []
        return values[0] if values else "ACTIVE"
    if style == "Bool":
        return "true"
    if style == "GUID":
        return "guid-123"
    if style in ["QN", "ID"]:
        prefix = "NEW" if action == "Create" else "Existing"
        return f"{prefix} {key}"
    if style in ["Reference Name", "Reference Name List"]:
        return f"Existing {key}"
    return f"Example {key}"


def resolve_command_spec(command: str) -> tuple[dict | None, str]:
    action, object_type = _split_command(command)
    if action in ["Create", "Update"] and object_type:
        spec = get_command_spec(f"Create {object_type}")
    else:
        spec = get_command_spec(command)
    if spec is None:
        spec = _find_spec_by_alternate_name(command)
        if spec is None:
            return None, "missing_spec"
    verb = spec.get("verb")
    if verb and action not in _verb_synonyms(verb):
        return spec, "verb_mismatch"
    return spec, "ok"


def _split_command(command: str) -> tuple[str, str]:
    parts = command.split(maxsplit=1)
    action = parts[0]
    object_type = parts[1] if len(parts) > 1 else ""
    return action, object_type


def _verb_synonyms(verb: str) -> set[str]:
    synonyms = {
        "Create": {"Create", "Update"},
        "Link": {"Link", "Attach", "Detach", "Unlink"},
        "View": {"View", "List"},
    }
    return synonyms.get(verb, {verb})


def _find_spec_by_alternate_name(command: str) -> dict | None:
    command_norm = _normalize_command_text(command)
    action, object_type = _split_command(command_norm)
    command_terms = _normalize_command_text(object_type)
    command_variants = {
        _normalize_command_text(f"{variant} {object_type}".strip())
        for variant in _action_variants(action)
    }
    command_variants.add(command_norm)

    for spec in COMMAND_DEFINITIONS.get("Command Specifications", {}).values():
        if not isinstance(spec, dict):
            continue
        alternate_names = spec.get("alternate_names", "")
        if not alternate_names:
            continue
        for alt in alternate_names.split(";"):
            alt_norm = _normalize_command_text(alt)
            if alt_norm in command_variants or alt_norm == command_terms:
                return spec
    return None


def _normalize_command_text(text: str) -> str:
    normalized = text.replace("->", " to ")
    normalized = " ".join(normalized.split())
    return normalized.strip()


def _action_variants(action: str) -> set[str]:
    synonyms = {
        "Create": {"Create", "Update"},
        "Update": {"Create", "Update"},
        "Link": {"Link", "Attach", "Add"},
        "Attach": {"Link", "Attach", "Add"},
        "Add": {"Link", "Attach", "Add"},
        "Detach": {"Detach", "Unlink", "Remove"},
        "Unlink": {"Detach", "Unlink", "Remove"},
        "Remove": {"Detach", "Unlink", "Remove"},
        "View": {"View", "List"},
        "List": {"View", "List"},
    }
    return synonyms.get(action, {action})
