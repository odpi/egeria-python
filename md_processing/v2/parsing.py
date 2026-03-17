"""
Standardized parsing logic for Dr.Egeria v2 commands.
Implements the Attribute-First (Spec-Agnostic) parsing strategy.
"""
import re
from typing import Any, Dict, List, Optional
from loguru import logger

from pyegeria.core._globals import resolve_enum, CONTENT_STATUS, ACTIVITY_STATUS, DEPLOYMENT_STATUS, GovernanceDomains
from md_processing.md_processing_utils.md_processing_constants import get_command_spec, load_commands
from .extraction import DrECommand
from .utils import parse_key_value

class AttributeFirstParser:
    """
    Parses a DrECommand by mapping its raw attributes to the canonical command specification.
    """
    def __init__(self, command: DrECommand, client: Optional[Any] = None):
        self.command = command
        self.client = client
        self.spec = get_command_spec(f"{command.verb} {command.object_type}")
        self.parsed_attributes = {}
        self.errors = []
        self.warnings = []

    def parse(self) -> Dict[str, Any]:
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
                logger.warning(f"Unknown attribute label: '{raw_label}'")
                self.warnings.append(f"Unknown attribute label: '{raw_label}'")
                continue

            canonical_name, details = match
            # print(f"DEBUG: Processing {canonical_name}, style={details.get('style')}, value={raw_value}")
            pre_warnings = len(self.warnings)
            parsed_value = self._process_attribute_value(raw_value, details)
            if parsed_value is not None:
                # Use canonical_name for compatibility with legacy helpers (e.g. 'Description')
                self.parsed_attributes[canonical_name] = {
                    "value": parsed_value,
                    "valid": True,
                    "exists": True,
                    "status": "INFO" if len(self.warnings) == pre_warnings else "WARNING"
                }

        # Check for required attributes
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

            if details.get("input_required", False) and canonical_name not in self.parsed_attributes:
                self.errors.append(f"Missing required attribute: '{canonical_name}'")

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
        label_map[canonical_name.lower()] = (canonical_name, details)
        alt_labels = details.get("attr_labels", "")
        if alt_labels:
            # Labels can be comma or semicolon separated
            for label in re.split(r'[,;]', str(alt_labels)):
                l = label.strip().lower()
                if l:
                    label_map[l] = (canonical_name, details)

    def _process_attribute_value(self, value: str, details: dict) -> Any:
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
            
        elif style == "Boolean":
            v = value.lower()
            return v in {"true", "yes", "1", "on"}
            
        elif style == "Dictionary" or style == "KeyValue":
            return parse_key_value(value)
            
        elif style in {"Valid Value", "Enum", "ValidValue"}:
            v = value
            if not v:
                return v
            # 1. Try dynamic lookup if client is available
            if self.client and hasattr(self.client, "get_valid_metadata_values"):
                # Use property_name from details if available, else name
                prop_name = details.get("property_name") or details.get("name")
                type_name = details.get("type_name")
                
                try:
                    valid_elements = self.client.get_valid_metadata_values(prop_name, type_name)
                    if isinstance(valid_elements, list) and len(valid_elements) > 0:
                        v_upper = v.upper()
                        for el in valid_elements:
                            pref_val = el.get("preferredValue")
                            if pref_val and pref_val.upper() == v_upper:
                                return pref_val
                        
                        self.warnings.append(f"Value '{v}' is not a valid metadata value for '{prop_name}'")
                        return v
                except Exception as e:
                    logger.debug(f"Dynamic valid value lookup failed for {prop_name}: {e}")

            # 2. Fallback to hardcoded list in spec
            valid_values = details.get("valid_values", [])
            if not valid_values:
                # If it's styled as Enum but no valid_values, it might be an unresolved Enumeration
                # Try to resolve it if it's potentially an enum
                if style == "Enum" or style == "ValidValue":
                     return self._process_attribute_value(value, {**details, "style": "Enumeration"})
                return v
            
            # Case-insensitive match
            v_upper = v.upper()
            for vv in valid_values:
                if vv.upper() == v_upper:
                    return vv
            
            self.warnings.append(f"Value '{v}' is not in valid values list for {details.get('name', 'attribute')}")
            return v

        elif style == "Enumeration":
            enum_type_name = details.get("enum_type", "GovernanceDomains")
            enum_class = {
                "GovernanceDomains": GovernanceDomains
            }.get(enum_type_name)
            
            if enum_class:
                resolved = resolve_enum(enum_class, value)
                if resolved is None:
                    self.warnings.append(f"Could not resolve enum value '{value}' for {enum_type_name}")
                    return value
                return resolved
            else:
                # Fallback if marked as Enumeration but no class found (maybe older spec)
                return value
            
        elif style == "List" or style == "NameList" or style == "Simple List":
            return [v.strip() for v in re.split(r'[,\n]', value) if v.strip()]
            
        return value

def parse_dr_egeria_content(text: str) -> List[Dict[str, Any]]:
    """Helper to extract and parse all commands in one go."""
    from .extraction import UniversalExtractor
    extractor = UniversalExtractor(text)
    commands = extractor.extract_commands()
    
    results = []
    for cmd in commands:
        parser = AttributeFirstParser(cmd)
        ir = parser.parse()
        results.append({
            "verb": cmd.verb,
            "object_type": cmd.object_type,
            "attributes": ir["attributes"],
            "errors": ir["errors"],
            "warnings": ir["warnings"],
            "raw_block": cmd.raw_block
        })
    return results
