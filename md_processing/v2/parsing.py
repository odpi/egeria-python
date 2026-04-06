"""
Standardized parsing logic for Dr.Egeria v2 commands.
Implements the Attribute-First (Spec-Agnostic) parsing strategy.
"""
import asyncio
import re
from difflib import get_close_matches
from typing import Any, Dict, List, Optional
from loguru import logger

import pyegeria.core._globals as pyeg_globals
from md_processing.md_processing_utils.md_processing_constants import get_command_spec, load_commands
import md_processing.md_processing_utils.md_processing_constants as md_constants
from md_processing.md_processing_utils.common_md_utils import normalize_value
from .extraction import DrECommand
from .utils import parse_key_value

class AttributeFirstParser:
    """
    Parses a DrECommand by mapping its raw attributes to the canonical command specification.
    """
    _valid_values_cache = {}  # key: (prop_name, type_name) -> list[dict]
    
    def __init__(self, command: DrECommand, client: Optional[Any] = None, directive: str = "process"):
        self.command = command
        self.client = client
        self.directive = directive
        self.spec = get_command_spec(f"{command.verb} {command.object_type}")
        self.parsed_attributes = {}
        self.errors = []
        self.warnings = []

    async def parse(self) -> Dict[str, Any]:
        if not self.spec:
            logger.error(f"No specification found for command: {self.command.verb} {self.command.object_type}")
            self.errors.append(f"No specification found for command: {self.command.verb} {self.command.object_type}")
            return {}

        # Spec can use "Attributes" or "attributes"
        spec_attrs = self.spec.get("Attributes", self.spec.get("attributes", []))
        logger.debug(f"Found {len(spec_attrs)} spec attributes for {self.command.verb} {self.command.object_type}")
        
        # Create a mapping of Label -> Spec Object
        label_map = {}
        for attr_obj in spec_attrs:
            if not isinstance(attr_obj, dict):
                continue
            
            # Check for flattened structure first (common in compact specs)
            if "name" in attr_obj and isinstance(attr_obj.get("variable_name"), str):
                self._add_to_label_map(label_map, attr_obj["name"], attr_obj)
            else:
                # Handle nested structure: {"canonical_name": {details}}
                for canonical_name, details in attr_obj.items():
                    if isinstance(details, dict):
                        self._add_to_label_map(label_map, canonical_name, details)

        logger.debug(f"Label map keys: {list(label_map.keys())}")

        # Map provided attributes
        for raw_label, raw_value in self.command.attributes.items():
            match = label_map.get(raw_label.lower())
            if not match:
                # Fallback: if it's not in the spec but contains a GUID or is a link command, preserve it anyway
                # This is useful for link commands with flexible attributes like "Blueprint Parent".
                is_link_cmd = self.command.verb.lower() in {"link", "attach", "add", "unlink", "detach", "remove"}
                if is_link_cmd or "(guid:" in raw_value or re.search(r'[0-9a-f]{8}-[0-9a-f]{4}', raw_value, re.I):
                    details = {"style": "ID", "variable_name": raw_label.lower().replace(" ", "_")}
                    canonical_name = raw_label
                else:
                    close_keys = get_close_matches(raw_label.lower(), list(label_map.keys()), n=3, cutoff=0.72)
                    suggestions = []
                    for key in close_keys:
                        canonical = label_map[key][0]
                        if canonical not in suggestions:
                            suggestions.append(canonical)
                    if suggestions:
                        msg = f"Unknown attribute label: '{raw_label}'. Did you mean: {', '.join(suggestions)}?"
                    else:
                        msg = f"Unknown attribute label: '{raw_label}'"
                    logger.warning(msg)
                    self.warnings.append(msg)
                    continue
            else:
                canonical_name, details = match
            # print(f"DEBUG: Processing {canonical_name}, style={details.get('style')}, value={raw_value}")
            pre_warnings = len(self.warnings)
            parsed_value = await self._process_attribute_value(raw_value, details)
            if parsed_value is not None:
                # Use canonical_name for compatibility with legacy helpers (e.g. 'Description')
                self.parsed_attributes[canonical_name] = {
                    "value": parsed_value,
                    "valid": True,
                    "exists": True,
                    "style": details.get("style", "Simple"),
                    "existing_element": details.get("existing_element", ""),
                    "status": "INFO" if len(self.warnings) == pre_warnings else "WARNING"
                }

        # Check for required attributes and apply defaults
        verb_lower = self.command.verb.lower()
        is_update = verb_lower in {"update", "modify", "patch"}
        
        # Only apply defaults for "creation-like" or "establishment" verbs
        # We skip for updates (to keep them sparse) and for read/delete operations.
        skip_defaults_verbs = {
            "update", "modify", "patch", 
            "delete", "remove", "detach", "unlink",
            "view", "list", "search", "find", "display", "run", "provenance"
        }
        apply_defaults = verb_lower not in skip_defaults_verbs
        
        for attr_obj in spec_attrs:
            if not isinstance(attr_obj, dict):
                continue
            
            # Identify the canonical name and details
            if "name" in attr_obj and "variable_name" in attr_obj:
                # Flattened structure
                canonical_name = attr_obj["name"]
                details = attr_obj
            else:
                # Nested structure: {"canonical_name": {details}}
                canonical_items = list(attr_obj.items())
                if not canonical_items:
                    continue
                canonical_name, details = canonical_items[0]
                if not isinstance(details, dict):
                    continue

            # If it's an update operation, check if the attribute should even be in an update.
            # If inUpdate is false, then we shouldn't require it during update.
            input_required = details.get("input_required", False)
            if is_update:
                if not details.get("inUpdate", True):
                    input_required = False
                    # If the user provided it, we might want to skip it from parsed_attributes too
                    # but it's already in there from the first loop.
                    # We should probably remove it if it's not allowed in update.
                    if canonical_name in self.parsed_attributes:
                        del self.parsed_attributes[canonical_name]
                    continue
            
            if input_required and canonical_name not in self.parsed_attributes:
                provided_labels = list(self.command.attributes.keys())
                msg = f"Missing required attribute: '{canonical_name}'"
                if provided_labels:
                    msg += f". Provided attributes: {', '.join(provided_labels)}"
                    close_labels = get_close_matches(canonical_name.lower(), [lbl.lower() for lbl in provided_labels], n=2, cutoff=0.72)
                    if close_labels:
                        original = [lbl for lbl in provided_labels if lbl.lower() in set(close_labels)]
                        if original:
                            msg += f". Check label spelling/casing near: {', '.join(original)}"
                self.errors.append(msg)
            
            # Apply default value if missing or empty and we are in a creation-like operation
            existing = self.parsed_attributes.get(canonical_name)
            is_empty = False
            if existing:
                val = existing.get("value")
                if val is None or (isinstance(val, (str, list)) and not val):
                    is_empty = True

            if (canonical_name not in self.parsed_attributes or is_empty) and apply_defaults:
                default_value = details.get("default_value")
                if default_value is not None and str(default_value).strip() != "" and apply_defaults:
                    logger.debug(f"Applying default value '{default_value}' for {canonical_name}")
                    parsed_default = await self._process_attribute_value(str(default_value), details)
                    if parsed_default is not None:
                         self.parsed_attributes[canonical_name] = {
                            "value": parsed_default,
                            "valid": True,
                            "exists": canonical_name in self.parsed_attributes,
                            "style": details.get("style", "Simple"),
                            "existing_element": details.get("existing_element", ""),
                            "status": "INFO",
                            "is_default": True
                        }

        qn_obj = self.parsed_attributes.get("Qualified Name", self.parsed_attributes.get("qualified_name"))
        qn_value = qn_obj.get("value") if isinstance(qn_obj, dict) else qn_obj

        return {
            "attributes": self.parsed_attributes,
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "qualified_name": qn_value
        }

    def _add_to_label_map(self, label_map: Dict[str, Any], canonical_name: str, details: Dict[str, Any]):
        """Helper to index an attribute by its canonical name and all alternate labels."""
        # Ensure variable_name and name are present so _process_attribute_value can inspect them
        if "variable_name" not in details:
            details["variable_name"] = canonical_name.lower().replace(" ", "_")
        if "name" not in details:
            details["name"] = canonical_name

        label_map[canonical_name.lower()] = (canonical_name, details)
        # Also register snake_case version of canonical_name
        label_map[canonical_name.lower().replace(" ", "_")] = (canonical_name, details)
        alt_labels = details.get("attr_labels", "")
        if alt_labels:
            if isinstance(alt_labels, str):
                # Labels can be comma or semicolon separated
                labels = re.split(r'[,;]', alt_labels)
            elif isinstance(alt_labels, list):
                labels = alt_labels
            else:
                labels = [str(alt_labels)]

            for label in labels:
                l = str(label).strip().lower()
                if l:
                    label_map[l] = (canonical_name, details)

    async def _process_attribute_value(self, value: str, details: dict) -> Any:
        if value is None:
            return None
        value = value.strip()
        style = details.get("style", "Simple")
        
        if style == "Simple" or style == "ID" or style == "Reference Name":
            val = value
            if not val:
                # If it's a date-like attribute, return None to satisfy Pydantic/SDK
                name = details.get("name", "")
                if any(x in name for x in ["Time", "Date", "From", "To"]):
                    return None
            return val
            
        elif style in {"Boolean", "Bool"}:
            v = str(value).lower()
            return v in {"true", "yes", "1", "on"}
            
        elif style == "Dictionary" or style == "KeyValue":
            return parse_key_value(value)
            
        elif style in {"Enum", "Enumeration"}:
            v = value
            if not v:
                return v

            enum_type_name = details.get("enum_type")
            if not enum_type_name and details.get("name") == "Domain Identifier":
                enum_type_name = "GovernanceDomains"

            resolved_val = None
            if enum_type_name:
                # Look up in _globals or md_constants
                enum_obj = getattr(pyeg_globals, enum_type_name, None)
                if enum_obj is None:
                    enum_obj = getattr(md_constants, enum_type_name, None)

                if enum_obj is not None:
                    if isinstance(enum_obj, type) and issubclass(enum_obj, pyeg_globals.Enum):
                        resolved_val = pyeg_globals.resolve_enum(enum_obj, v)
                    elif isinstance(enum_obj, (list, set, tuple)):
                        v_norm = normalize_value(v)
                        for item in enum_obj:
                            if normalize_value(str(item)) == v_norm:
                                resolved_val = item
                                break

            if resolved_val is not None:
                return resolved_val

            # Fallback to hardcoded list in spec
            valid_values = details.get("valid_values", [])
            v_norm = normalize_value(v)
            for vv in valid_values:
                if normalize_value(vv) == v_norm:
                    return vv

            # Mismatch handling
            msg = f"Value '{v}' is not a valid enum value for '{enum_type_name or details.get('name', 'attribute')}'"
            if self.directive == "validate":
                self.warnings.append(msg)
            else:
                self.errors.append(msg)
            return v

        elif style in {"Valid Value", "ValidValue"}:
            v = value
            if not v:
                return v

            if self.client:
                # Resolve property name (e.g., "Resource Use" -> "resourceUse")
                prop_name = details.get("property_name") or details.get("name")
                if not details.get("property_name") and prop_name:
                    parts = re.split(r'[\s_]+', str(prop_name))
                    prop_name = parts[0].lower() + ''.join(x.capitalize() for x in parts[1:])
                
                type_name = details.get("type_name")
                if not type_name:
                    type_name = None
                map_name = details.get("map_name")

                try:
                    vm_client = getattr(self.client, "valid_metadata", self.client)
                    valid = None
                    
                    # 1. Attempt direct validation call
                    if map_name and hasattr(vm_client, "_async_validate_metadata_map_value"):
                        valid = await vm_client._async_validate_metadata_map_value(prop_name, type_name, map_name, v)
                    elif hasattr(vm_client, "_async_validate_metadata_value"):
                        valid = await vm_client._async_validate_metadata_value(prop_name, type_name, v)
                    
                    if valid is True:
                        return v
                    elif valid is False:
                        # Egeria is the source of truth - failure here might just mean it's a DisplayName
                        # Or it might truly be invalid. We check the list as a fallback.
                        pass
                    
                    # 2. Check Cache for the list (to handle DisplayName -> PreferredValue mapping)
                    cache_key = (prop_name, type_name)
                    if cache_key not in self._valid_values_cache:
                        if hasattr(vm_client, "_async_get_valid_metadata_values"):
                            self._valid_values_cache[cache_key] = await vm_client._async_get_valid_metadata_values(prop_name, type_name)
                        else:
                            self._valid_values_cache[cache_key] = []
                    
                    valid_elements = self._valid_values_cache[cache_key]
                    if isinstance(valid_elements, list) and len(valid_elements) > 0:
                        v_norm = normalize_value(v)
                        for el in valid_elements:
                            pref_val = el.get("preferredValue")
                            disp_name = el.get("displayName")
                            if (pref_val and normalize_value(pref_val) == v_norm) or \
                               (disp_name and normalize_value(disp_name) == v_norm):
                                # Return the preferred value (with correct type)
                                data_type = el.get("dataType", "string").lower()
                                if data_type in ["int", "integer"] and pref_val is not None:
                                    try:
                                        return int(pref_val)
                                    except (ValueError, TypeError):
                                        return pref_val
                                return pref_val
                        
                        # Not in the Egeria list - fatal error
                        self.errors.append(f"Value '{v}' is not a valid metadata value for '{details.get('name')}' (Validated by Egeria)")
                        return v

                except Exception as e:
                    logger.debug(f"Dynamic validation failed for {prop_name}: {e}. Falling back to spec.")

            # 3. Fallback to Specification if offline or server check failed
            valid_values = details.get("valid_values", [])
            v_norm = normalize_value(v)
            for vv in valid_values:
                if normalize_value(vv) == v_norm:
                    return vv

            # Mismatch handling - make it a warning unless it's strictly required
            msg = f"Value '{v}' is not a valid metadata value for '{details.get('name', 'attribute')}'"
            if self.directive == "validate" or not details.get("input_required", False):
                if msg not in self.warnings:
                    self.warnings.append(msg)
            else:
                if msg not in self.errors:
                    self.errors.append(msg)
            return v
            
        elif style in {"List", "NameList", "Simple List", "Reference Name List"}:
            return [v.strip() for v in re.split(r'[,\n]', value) if v.strip()]
            
        return value

async def parse_dr_egeria_content(text: str) -> List[Dict[str, Any]]:
    """Helper to extract and parse all commands in one go."""
    from .extraction import UniversalExtractor
    extractor = UniversalExtractor(text)
    commands = extractor.extract_commands()
    
    results = []
    for cmd in commands:
        if not cmd.is_command:
            continue
            
        parser = AttributeFirstParser(cmd)
        ir = await parser.parse()
        results.append({
            "verb": cmd.verb,
            "object_type": cmd.object_type,
            "attributes": ir["attributes"],
            "errors": ir["errors"],
            "warnings": ir["warnings"],
            "raw_block": cmd.raw_block
        })
    return results
