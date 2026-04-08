"""
Async-First Command Processors for Dr.Egeria v2.
"""
import uuid
import asyncio
import json
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from loguru import logger

from pyegeria import EgeriaTech, PyegeriaException, NO_ELEMENTS_FOUND, print_basic_exception
from pyegeria.core.utils import make_format_set_name_from_type
from pyegeria.view.base_report_formats import select_report_spec
from pyegeria.view.output_formatter import generate_output, format_for_markdown_table

from md_processing.v2.extraction import DrECommand
from md_processing.v2.parsing import AttributeFirstParser
from md_processing.md_processing_utils.md_processing_constants import get_command_spec, resolve_command_spec
from md_processing.md_processing_utils.common_md_utils import (
    update_element_dictionary, get_element_dictionary, is_present, find_key_with_value
)

class AsyncBaseCommandProcessor(ABC):
    """
    Base class for all v2 Dr.Egeria command processors.
    Handles the standard flow: Parse -> Validate -> Execute/Validate (Dry Run).
    """

    def __init__(self, client: EgeriaTech, command: DrECommand, context: Optional[Dict[str, Any]] = None):
        self.client = client
        self.command = command
        self.context = context or {}
        
        # Ensure a request_id exists
        if "request_id" not in self.context:
            self.context["request_id"] = str(uuid.uuid4())
            
        directive = self.context.get("directive", "process")
        self.parser = AttributeFirstParser(self.command, client=self.client, directive=directive)
        self.parsed_output = None
        self.as_is_element = None
        self.related_results = []
        self.last_body = None
        self.markdown_verb = self.command.source_verb or self.command.verb
        self.markdown_object_type = self.command.source_object_type or self.command.object_type
        
        command_name = f"{self.command.verb} {self.command.object_type}"
        self.canonical_command_name, self.command_spec = resolve_command_spec(command_name)
        self.canonical_object_type = self._derive_canonical_object_type()
        self.egeria_type_name = self._derive_egeria_type_name()

    @staticmethod
    def _is_unsupported_type_lookup_error(exc: Exception) -> bool:
        """Detect server responses that indicate an unknown metadata type constraint."""
        msg = str(exc)
        return (
            "OMAG-COMMON-400-018" in msg
            or ("type name" in msg.lower() and "not recognized" in msg.lower())
        )

    @staticmethod
    def _extract_egeria_error_id(exc: Exception) -> Optional[str]:
        msg = str(exc)
        match = re.search(r"(OMAG-[A-Z-]+-\d{3}-\d{3})", msg)
        return match.group(1) if match else None

    def _add_warning(self, warning: str) -> None:
        """Record warning once so validate output can surface it without duplicates."""
        if not self.parsed_output:
            return
        warnings = self.parsed_output.setdefault("warnings", [])
        if warning not in warnings:
            warnings.append(warning)

    def extract_guid_or_raise(self, raw_guid: Any, operation: str) -> str:
        """Normalize GUID-like SDK responses and fail fast on invalid create/update identifiers."""
        def _find_guid(payload: Any) -> Optional[str]:
            if isinstance(payload, str):
                candidate = payload.strip()
                return candidate if candidate else None

            if isinstance(payload, dict):
                for key in ("guid", "elementGUID", "elementGuid"):
                    found = _find_guid(payload.get(key))
                    if found:
                        return found

                header = payload.get("elementHeader")
                if isinstance(header, dict):
                    found = _find_guid(header.get("guid"))
                    if found:
                        return found

                for value in payload.values():
                    found = _find_guid(value)
                    if found:
                        return found
                return None

            if isinstance(payload, list):
                for item in payload:
                    found = _find_guid(item)
                    if found:
                        return found
                return None

            return None

        guid = _find_guid(raw_guid)

        if not isinstance(guid, str) or not guid.strip():
            raise ValueError(f"{operation} did not return a GUID string. Raw response type: {type(raw_guid).__name__}")

        return guid.strip()
    
    def get_command_spec(self) -> Dict[str, Any]:
        """Return the JSON specification for this command family."""
        if self.command_spec:
            return self.command_spec
        spec = get_command_spec(f"{self.command.verb} {self.command.object_type}")
        self.command_spec = spec or {}
        return self.command_spec

    def _derive_canonical_object_type(self) -> str:
        if self.canonical_command_name and " " in self.canonical_command_name:
            return self.canonical_command_name.split(" ", 1)[1]
        return self.command.object_type

    def _derive_egeria_type_name(self) -> str:
        spec = self.get_command_spec() or {}
        om_type = spec.get("OM_TYPE")
        if om_type:
            return om_type

        find_constraints = spec.get("find_constraints") if spec else None
        if find_constraints:
            parsed_constraints = None
            if isinstance(find_constraints, dict):
                parsed_constraints = find_constraints
            elif isinstance(find_constraints, str):
                try:
                    parsed_constraints = json.loads(find_constraints)
                except json.JSONDecodeError:
                    parsed_constraints = None

            if isinstance(parsed_constraints, dict):
                metadata_element_type = parsed_constraints.get("metadata_element_type")
                if isinstance(metadata_element_type, str) and metadata_element_type.strip():
                    return metadata_element_type.strip()

                metadata_types = parsed_constraints.get("metadata_element_types", [])
                if isinstance(metadata_types, list):
                    for type_name in metadata_types:
                        if isinstance(type_name, str) and type_name.strip():
                            return type_name.strip()

        # Fallback for specs without explicit metadata type constraints.
        if not self.canonical_object_type:
            return None
        words = [w for w in re.split(r"[^A-Za-z0-9]+", self.canonical_object_type) if w]
        if words:
            return "".join(w[0].upper() + w[1:] for w in words)
        return self.canonical_object_type or None

    def is_report_view_command(self) -> bool:
        """True when this command is a report runner, not an element-targeting command."""
        return self.command.verb.lower() == "view" and self.command.object_type.strip().lower() == "report"

    def supports_target_element_lookup(self) -> bool:
        """Whether this command should resolve/track a target element by qualified name."""
        return not self.is_report_view_command()

    def add_related_result(self, label: str, guid: Optional[str] = None, status: str = "success", message: Optional[str] = None):
        """Record the outcome of a secondary operation."""
        self.related_results.append({
            "label": label, "guid": guid, "status": status, "message": message
        })

    async def execute(self) -> Dict[str, Any]:
        """
        Orchestrate the command execution flow.
        Returns a dictionary containing the output markdown and execution metadata.
        """
        directive = self.context.get("directive", "process")
        
        # 1. Parse attributes using the spec-agnostic parser
        spec = self.get_command_spec()
        self.parsed_output = await self.parser.parse()
        attributes = self.parsed_output.get("attributes", {})

        # Extract Display Name if present
        if self.is_report_view_command():
            display_name = attributes.get("Report Spec", {}).get("value")
        else:
            display_name = attributes.get("Display Name", {}).get("value")
            if not display_name:
                # Fallback to other name-like attributes if possible
                for k, v in attributes.items():
                    if any(k.endswith(s) for s in [" Name", " ID", " Id"]) and k != "Qualified Name":
                        display_name = v.get("value")
                        if display_name:
                            break
            if not display_name:
                display_name = attributes.get("Name", {}).get("value")

        if display_name:
            self.parsed_output["display_name"] = display_name

        # 1a. Ensure qualified_name is derived early if possible
        if self.supports_target_element_lookup() and not self.parsed_output.get("qualified_name"):
            qn = self.derive_qualified_name(attributes)
            if qn:
                self.parsed_output["qualified_name"] = qn
                # Inject into attributes for consistency with legacy prop body helpers
                if "Qualified Name" not in attributes:
                    attributes["Qualified Name"] = {
                        "value": qn,
                        "valid": True,
                        "exists": True,
                        "status": "INFO"
                    }

        # 1b. Handle 'display' directive
        if directive == "display":
            self.as_is_element = await self.fetch_as_is()
            if self.as_is_element:
                output = await self.render_result_markdown(self.as_is_element.get('elementHeader', {}).get('guid'))
            else:
                output = await self.display_only()
            
            return {
                "output": output,
                "status": "success",
                "message": f"Displayed {self.command.verb} {self.command.object_type}",
                "verb": self.command.verb,
                "object_type": self.canonical_object_type,
                "markdown_object_type": self.markdown_object_type,
                "display_name": self.parsed_output.get("display_name"),
                "qualified_name": self.parsed_output.get("qualified_name"),
                "warnings": self.parsed_output.get("warnings", [])
            }

        # 2. Pre-flight Validation (check required fields, etc.)
        if not self.parsed_output.get("valid", True):
            errors = self.parsed_output.get("errors", [])
            err_msg = "; ".join(errors) if errors else "General validation failure"
            full_message = f"Validation failed: {err_msg}"
            logger.error(f"{full_message} for {self.command.verb} {self.command.object_type}")
            logger.debug(f"Parsed Output: {self.parsed_output}")
            
            # Even if invalid, we want to show the diagnosis table if possible
            analysis = await self.validate_only()
            return {
                "output": analysis if directive == "validate" else self.command.raw_block,
                "analysis": analysis,
                "status": "failure",
                "message": full_message,
                "verb": self.command.verb,
                "object_type": self.canonical_object_type,
                "markdown_object_type": self.markdown_object_type,
                "display_name": self.parsed_output.get("display_name"),
                "qualified_name": self.parsed_output.get("qualified_name"),
                "found": self.parsed_output.get("exists", False),
                "errors": errors
            }

        # 3. Handle As-Is state and other pre-execution steps
        # Fetch As-Is state (Lookup by GUID or QN)
        # We do this BEFORE recording in planned_elements to avoid self-shadowing 
        # (where an element sees itself in 'planned' and skips the Egeria lookup)
        if self.supports_target_element_lookup():
            self.as_is_element = await self.fetch_as_is()
        else:
            self.as_is_element = None

        # 4a. Check for duplicate display_name if we are creating a new element
        if not self.as_is_element and self.command.verb in ["Create", "Define", "Register", "Add", "Upsert"]:
            display_name = attributes.get("Display Name", {}).get("value")
            if display_name:
                existing_guid = await self.resolve_element_guid(display_name, tech_type=self.egeria_type_name)
                if existing_guid and not existing_guid.startswith("(Planned:"):
                    # Try to fetch the full element and transition to Update to avoid 409 conflicts
                    try:
                        element = await self.fetch_element(existing_guid)
                        if element:
                            self.as_is_element = element
                            logger.info(f"Element with Display Name '{display_name}' found in Egeria (GUID: {existing_guid}). Transitioning to Update.")
                        else:
                            msg = f"Warning: An element with Display Name '{display_name}' already exists in Egeria (QN or Display Name match) but could not be fetched."
                            logger.warning(msg)
                            self._add_warning(msg)
                    except Exception as fetch_err:
                        msg = f"Warning: An element with Display Name '{display_name}' already exists in Egeria (QN or Display Name match)."
                        logger.warning(f"{msg} Fetch error: {fetch_err}")
                        self._add_warning(msg)

        if self.as_is_element:
            # Transition to Update
            self.command.verb = "Update"
            self.parsed_output["exists"] = True
            header = self.as_is_element.get('elementHeader', {})
            self.parsed_output["guid"] = header.get('guid')

        # 5. Record this element in the shared 'planned_elements' set
        current_qn = self.parsed_output.get("qualified_name")
        planned = self.context.get("planned_elements")
        if isinstance(planned, set) and current_qn and self.command.verb in ["Create", "Define", "Register", "Add", "Update", "Modify", "Upsert"]:
            planned.add(current_qn)

        # 6. Dry-run validation (optional/future)

        # 7. Global Lookups and Existential Checks for References
        # For report commands, only explicit reference-style attributes are resolved.
        # For non-report commands, retain broader heuristics.
        for attr_name, attr_data in attributes.items():
                # Get the style from the attribute data (provided by AttributeFirstParser) or fallback to spec
                spec_style = attr_data.get("style", "Simple")
                spec_existing = attr_data.get("existing_element", "")

                # --- PATCH: Only use valid element types for endpoint GUID resolution ---
                # If spec_existing looks like a relationship type, skip it as a type constraint.
                # Relationship types in Egeria are usually CamelCase with no 'Element' suffix and not OpenMetadataRoot.
                # We'll use a simple heuristic: if it ends with 'Description', 'Assignment', 'Relationship', or is in a known set, skip it.
                RELATIONSHIP_TYPE_SUFFIXES = ("Description", "Assignment", "Relationship", "Link", "Reference", "Membership", "Dependency", "Composition")
                KNOWN_RELATIONSHIP_TYPES = {"DataDescription", "DataValueAssignment", "DataValueComposition", "DataValueDefinition", "DataClassComposition", "CertificationTypeAssignment", "CollectionMembership", "ProductDependency"}
                sanitized_spec_existing = spec_existing
                if spec_existing and (spec_existing.endswith(RELATIONSHIP_TYPE_SUFFIXES) or spec_existing in KNOWN_RELATIONSHIP_TYPES):
                    sanitized_spec_existing = None

                # Heuristics for identifying what attributes represent references to other elements
                # We exclude common string attributes that might contain keywords like "Reference" or "Name"
                non_ref_names = [
                    "Display Name", "Qualified Name", "Description", 
                    "Reference Abstract", "Reference Title", "Reference Description",
                    "Abstract", "Title", "Category", "Organization", "URL", "License", "Copyright",
                    "Identifier", "Domain", "Summary"
                ]

                explicit_ref_styles = {"Reference Name", "Reference Name List", "Reference", "ID", "GUID"}

                if self.is_report_view_command():
                    is_ref_candidate = spec_style in explicit_ref_styles
                else:
                    is_ref_candidate = (
                        spec_style in explicit_ref_styles
                    ) or (
                        spec_existing != "" and spec_style in ["Simple", "Simple List", "List", "NameList"]
                    ) or (
                        any(k in attr_name for k in ["Id", "GUID", "Name", "Reference"]) 
                        and attr_name not in non_ref_names
                        and spec_style not in ["Simple", "Enum", "Valid Value", "ValidValue", "Dictionary", "KeyValue", "Enumeration", "Integer", "Boolean"]
                    )

                # More precise check: if it's already got a GUID or guid_list, don't re-resolve.
                # If it's a value but no GUID/guid_list, and it's a candidate, try to resolve.
                val = attr_data.get("value")
                if val and not attr_data.get("guid") and not attr_data.get("guid_list") and is_ref_candidate:
                    if isinstance(val, list):
                        guid_list = []
                        for item in val:
                            guid = await self.resolve_element_guid(item, tech_type=sanitized_spec_existing)
                            if guid:
                                guid_list.append(guid)
                        if guid_list:
                            attr_data["guid_list"] = guid_list
                            attr_data["exists"] = len(guid_list) == len(val)
                            if any(g.startswith("(Planned:") for g in guid_list):
                                attr_data["is_planned"] = True
                    else:
                        # Try to resolve GUID from cache or Egeria
                        guid = await self.resolve_element_guid(val, tech_type=sanitized_spec_existing)
                        if guid:
                            attr_data["guid"] = guid
                            # If it's a 'Planned' element, it counts as exists for validation
                            attr_data["exists"] = True
                            if guid.startswith("(Planned:"):
                                attr_data["is_planned"] = True
                        else:
                            # If it's a candidate ref and we couldn't resolve it, mark as not found
                            attr_data["exists"] = False
                            attr_data["valid"] = False # Treat as invalid to block execution
                            msg = f"Referenced element '{val}' for attribute '{attr_name}' not found."
                            if attr_data.get("errors") is None: attr_data["errors"] = []
                            attr_data["errors"].append(msg)
                            logger.error(msg)
                            if "errors" not in self.parsed_output:
                                self.parsed_output["errors"] = []
                            self.parsed_output["errors"].append(msg)


        # 7. Check for existence of the target element (As-Is state)
        if self.supports_target_element_lookup():
            if self.as_is_element:
                logger.debug(f"Element found! GUID: {self.parsed_output.get('guid')}")
            else:
                # Check if it's planned (defined earlier in the document)
                guid = await self.resolve_element_guid(current_qn)
                if guid and guid.startswith("(Planned:"):
                    logger.debug(f"Element is Planned! GUID: {guid}")
                    self.parsed_output["exists"] = True
                    self.parsed_output["guid"] = guid
                    self.parsed_output["is_planned"] = True
                else:
                    logger.debug(f"Element NOT found for QN: '{current_qn}'")
                    self.parsed_output["exists"] = False
                    if self.command.verb == "Update":
                        logger.debug(f"Target element for 'Update' not found: {self.parsed_output.get('qualified_name') or self.command.object_type}")
                        if "errors" not in self.parsed_output:
                            self.parsed_output["errors"] = []
                        self.parsed_output["errors"].append(f"Target element for 'Update' not found.")

                        analysis = await self.validate_only()
                        return {
                            "output": analysis if directive == "validate" else self.command.raw_block,
                            "analysis": analysis,
                            "status": "failure",
                            "message": f"Target element for Update not found.",
                            "verb": self.command.verb,
                            "object_type": self.canonical_object_type,
                            "markdown_object_type": self.markdown_object_type,
                            "found": False,
                            "errors": self.parsed_output["errors"]
                        }

        # 8. Decouple Analysis from Output
        analysis = await self.validate_only()

        # 9. Action Dispatch
        if directive == "validate":
            status = "success" if not self.parsed_output.get("errors") else "failure"
            guid = self.parsed_output.get("guid")
            return {
                "output": analysis,
                "analysis": analysis,
                "status": status,
                "message": f"Validated {self.command.verb} {self.command.object_type}" + (f" (GUID: {guid})" if guid else ""),
                "verb": self.command.verb,
                "object_type": self.canonical_object_type,
                "markdown_object_type": self.markdown_object_type,
                "display_name": self.parsed_output.get("display_name"),
                "qualified_name": self.parsed_output.get("qualified_name"),
                "guid": self.parsed_output.get("guid"),
                "found": self.parsed_output.get("exists", False),
                "warnings": self.parsed_output.get("warnings", [])
            }
        
        # Check for blockers before applying changes
        if self.parsed_output.get("errors"):
            guid = self.parsed_output.get("guid")
            return {
                "output": self.command.raw_block,
                "analysis": analysis,
                "status": "failure",
                "message": f"Execution blocked: {'; '.join(self.parsed_output['errors'])}" + (f" (GUID: {guid})" if guid else ""),
                "verb": self.command.verb,
                "object_type": self.canonical_object_type,
                "markdown_object_type": self.markdown_object_type,
                "display_name": self.parsed_output.get("display_name"),
                "qualified_name": self.parsed_output.get("qualified_name"),
                "guid": self.parsed_output.get("guid"),
                "found": self.parsed_output.get("exists", False)
            }

        # Resolve any Planned GUIDs before applying changes
        attributes = self.parsed_output.get("attributes", {})
        for attr_name, attr_data in attributes.items():
            if attr_data.get("is_planned"):
                val = attr_data.get("value")
                if attr_data.get("guid") and str(attr_data["guid"]).startswith("(Planned:"):
                    real_guid = await self.resolve_element_guid(val)
                    if real_guid and not str(real_guid).startswith("(Planned:"):
                        attr_data["guid"] = real_guid
                        attr_data["is_planned"] = False
                    else:
                        msg = f"Prerequisite element '{val}' was not successfully created or found."
                        logger.error(msg)
                        return {
                            "output": self.command.raw_block,
                            "analysis": analysis,
                            "status": "failure",
                            "message": f"Execution blocked: {msg}",
                            "verb": self.command.verb,
                            "object_type": self.canonical_object_type,
                            "markdown_object_type": self.markdown_object_type
                        }
                
                list_val = attr_data.get("guid_list")
                if list_val and any(str(g).startswith("(Planned:") for g in list_val):
                    new_list = []
                    names = attr_data.get("value", [])
                    if isinstance(names, list) and len(names) == len(list_val):
                        failed_names = []
                        for idx, g in enumerate(list_val):
                            if str(g).startswith("(Planned:"):
                                real_g = await self.resolve_element_guid(names[idx])
                                if real_g and not str(real_g).startswith("(Planned:"):
                                    new_list.append(real_g)
                                else:
                                    failed_names.append(names[idx])
                            else:
                                new_list.append(g)
                        
                        if failed_names:
                            msg = f"Prerequisite elements {failed_names} were not successfully created or found."
                            logger.error(msg)
                            return {
                                "output": self.command.raw_block,
                                "analysis": analysis,
                                "status": "failure",
                                "message": f"Execution blocked: {msg}",
                                "verb": self.command.verb,
                                "object_type": self.canonical_object_type,
                                "markdown_object_type": self.markdown_object_type
                            }
                        else:
                            attr_data["guid_list"] = new_list
                            attr_data["is_planned"] = False

        try:
            if self.context.get("debug"):
                print(
                    f"\n\033[1;36m══ DEBUG CMD: {self.command.verb} {self.command.object_type}"
                    f" | display_name={self.parsed_output.get('display_name', '')!r}"
                    f" | GUID={self.parsed_output.get('guid', 'new')} ══\033[0m"
                )
            output = await self.apply_changes()
        except PyegeriaException as e:
            logger.error(f"Command String: {self.command.raw_block}")
            if self.last_body:
                logger.error(f"Request Body: {json.dumps(self.last_body, indent=2, default=str)}")
            logger.exception(f"Error applying changes for {self.command.verb} {self.command.object_type}")
            print_basic_exception(e)
            return {
                "output": self.command.raw_block,
                "analysis": analysis,
                "status": "failure",
                "message": f"Execution failed: {str(e)}",
                "verb": self.command.verb,
                "object_type": self.canonical_object_type,
                "markdown_object_type": self.markdown_object_type,
                "display_name": self.parsed_output.get("display_name"),
                "qualified_name": self.parsed_output.get("qualified_name"),
                "found": self.parsed_output.get("exists", False),
                "errors": [str(e)]
            }
        except Exception as e:
            logger.error(f"Command String: {self.command.raw_block}")
            if self.last_body:
                logger.error(f"Request Body: {json.dumps(self.last_body, indent=2, default=str)}")
            logger.exception(f"Error applying changes for {self.command.verb} {self.command.object_type}")
            return {
                "output": self.command.raw_block,
                "analysis": analysis,
                "status": "failure",
                "message": f"Execution failed: {str(e)}",
                "verb": self.command.verb,
                "object_type": self.canonical_object_type,
                "markdown_object_type": self.markdown_object_type,
                "display_name": self.parsed_output.get("display_name"),
                "qualified_name": self.parsed_output.get("qualified_name"),
                "found": self.parsed_output.get("exists", False),
                "errors": [str(e)]
            }
        
        # 10. Post-execution: Update the cache on success
        guid = self.parsed_output.get("guid") or attributes.get("guid")
        if isinstance(output, str) and output and not output.startswith(self.command.raw_block): # Basic success check
            qn = self.parsed_output.get("qualified_name")
            if qn and guid:
                d_name = self.parsed_output.get("display_name") or qn
                update_element_dictionary(qn, {"guid": guid, "display_name": d_name})

        message = f"Executed {self.command.verb} {self.command.object_type}" + (f" (GUID: {guid})" if guid else "")
        if self.related_results:
            rel_parts = [
                f"{r['label']}" + (f" (GUID: {r['guid']})" if r.get('guid') else "") + 
                (f" - {r['status'].upper()}" if r.get('status') != "success" else "")
                for r in self.related_results
            ]
            message += " | Related: " + "; ".join(rel_parts)

        return {
            "output": output,
            "analysis": analysis,
            "status": "success",
            "message": message,
            "verb": self.command.verb,
            "object_type": self.canonical_object_type,
            "markdown_object_type": self.markdown_object_type,
            "display_name": self.parsed_output.get("display_name"),
            "guid": guid,
            "qualified_name": self.parsed_output.get("qualified_name"),
            "found": self.parsed_output.get("exists", False),
            "warnings": self.parsed_output.get("warnings", [])
        }

    def derive_qualified_name(self, attributes: Optional[Dict[str, Any]] = None) -> str:
        """
        Derive a qualified_name from 'Display Name' (or other basis) and the command spec.
        """
        if not self.supports_target_element_lookup():
            return ""

        if attributes is None:
            attributes = self.parsed_output.get("attributes", {})
            
        # 1. Find the best attribute to use as a name basis
        display_name = attributes.get("Display Name", {}).get("value")
        if not display_name:
            # Look for attributes marked as 'is_qualified_name_basis' in the spec
            spec = self.get_command_spec()
            basis_attr = None
            if spec and "attributes" in spec:
                for attr_name, attr_spec in spec["attributes"].items():
                    if attr_spec.get("is_qualified_name_basis"):
                        basis_attr = attr_name
                        break
            
            if basis_attr:
                display_name = attributes.get(basis_attr, {}).get("value")

        if not display_name:
            # Look for ANY attribute ending in ' Name', ' ID', or ' Id' (e.g., 'Glossary Name', 'Term ID')
            for k, v in attributes.items():
                if any(k.endswith(s) for s in [" Name", " ID", " Id"]) and k != "Qualified Name":
                    display_name = v.get("value")
                    if display_name:
                        break
        
        if not display_name:
            # Try 'Name' strictly if present
            display_name = attributes.get("Name", {}).get("value")

        if not display_name:
            # Return empty if no basis found - will fail validation if required
            return ""

        spec = self.get_command_spec()
        qn_prefix = (spec.get("qn_prefix") if spec else None) or self.command.object_type
        
        # Strip trailing colon and sanitize spaces if present (Egeria types cannot have spaces)
        if qn_prefix:
            qn_prefix = qn_prefix.replace(" ", "")
            if qn_prefix.endswith(':'):
                qn_prefix = qn_prefix[:-1]

        # Extract local qualifier (Namespace Path) and Version Identifier if present 
        local_qualifier = attributes.get("Namespace Path", {}).get("value")
        version_identifier = attributes.get("Version Identifier", {}).get("value")

        # Reach into 'collections' subclient which is guaranteed to have the helper
        helper = getattr(self.client, 'collections', self.client)
        if hasattr(helper, "__create_qualified_name__"):
            return helper.__create_qualified_name__(
                type_name=qn_prefix,
                display_name=display_name,
                local_qualifier=local_qualifier,
                version_identifier=version_identifier or ""
            )
        else:
            # Basic fallback if SDK helper unavailable
            q_name = f"{qn_prefix}::{display_name}"
            if local_qualifier:
                q_name = f"{local_qualifier}::{q_name}"
            if version_identifier:
                q_name = f"{q_name}::{version_identifier}"
            return q_name

    async def render_result_markdown(self, guid: str) -> str:
        """
        Fetch the element by GUID and render it into markdown using the appropriate report_spec.
        """
        if not guid:
            return self.command.raw_block
            
        # 1. Determine the report spec name
        # Convention: <Type>-DrE (spaces replaced with dashes)
        # Use canonical_object_type to ensure we get 'Glossary-Term-DrE' instead of 'Term-DrE'
        base_report_spec_name = make_format_set_name_from_type(self.canonical_object_type)
        
        from md_processing.md_processing_utils.common_md_proc_utils import EGERIA_USAGE_LEVEL
        level_suffix = f"-{EGERIA_USAGE_LEVEL.capitalize()}" if getattr(EGERIA_USAGE_LEVEL, 'capitalize', None) else "-Basic"
        report_spec_name = f"{base_report_spec_name}{level_suffix}"
        
        # 2. Fetch the element dictionary
        try:
            element = await self.fetch_element(guid)
            if not element or isinstance(element, str):
                logger.warning(f"Could not fetch element {guid} for rendering.")
                return self.command.raw_block
        except Exception as e:
            logger.error(f"Error fetching element for rendering: {e}")
            return self.command.raw_block

        # 3. Select the report spec
        columns_struct = select_report_spec(report_spec_name, "MD")
        if not columns_struct:
            columns_struct = select_report_spec(base_report_spec_name, "MD")
            
        if not columns_struct:
            msg = f"Report spec '{report_spec_name}' not found. Falling back to default."
            logger.warning(msg)
            if "warnings" not in self.parsed_output:
                self.parsed_output["warnings"] = []
            if msg not in self.parsed_output["warnings"]:
                self.parsed_output["warnings"].append(msg)
            columns_struct = select_report_spec("Referenceable", "MD")

        # 4. Generate the output
        try:
            markdown = generate_output(
                elements=[element],
                search_string=self.parsed_output.get("qualified_name", "Created/Updated Element"),
                entity_type=self.command.object_type,
                output_format="MD",
                columns_struct=columns_struct
            )
            return markdown
        except Exception as e:
            logger.error(f"Error generating markdown: {e}")
            return self.command.raw_block

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the details of an element by GUID. 
        Subclasses should override if MetadataExpert/Explorer is unavailable or if a specific OMAS method is needed.
        """
        try:
            # First try ClassificationExplorer (most standard and lightweight)
            logger.debug(f"fetch_element('{guid}') using client {self.client}")
            res = await getattr(self.client, "_async_get_element_by_guid_")(guid)
            logger.debug(f"fetch_element returned {res is not None}")
            if res and isinstance(res, dict):
                # The structure from classification-explorer comes under "element" usually
                if "element" in res:
                    return res["element"]
                return res
            return res
        except Exception as e:
            logger.debug(f"ClassificationExplorer fetch failed: {e}")

        try:
            # Fallback to MetadataExpert (more detailed properties)
            # Reordered subclients in EgeriaTech ensure this hits metadata-expert first
            res = await self.client._async_get_metadata_element_by_guid(guid)
            if res and isinstance(res, dict):
                return res
        except Exception as e:
            logger.debug(f"MetadataExpert/Explorer fetch failed: {e}")

        return None

    async def resolve_element_guid(self, name_or_guid: str, tech_type: Optional[str] = None) -> Optional[str]:
        """
        Resolves a name or GUID to a GUID using various strategies.
        Returns None if not found, or f"(Planned: {name})" if it's a forward reference.
        """
        if not name_or_guid or not str(name_or_guid).strip():
            return None
        
        name_or_guid = str(name_or_guid).strip()
        
        # Extract GUID from (guid:...) if present
        guid_match = re.search(r'\(guid:([^)]+)\)', name_or_guid)
        if guid_match:
            return guid_match.group(1).strip()
        
        # Ensure Egeria Type definitions contain no spaces, and remap
        # pseudo-types (classifications disguised as types in commands) to
        # their actual Egeria base entity types for API lookups.
        if tech_type:
            tech_type = tech_type.replace(" ", "")
            remap = {
                "DataSharingAgreement": "Agreement"
            }
            if tech_type in remap:
                logger.debug(f"resolve_element_guid: Remapping pseudo-type '{tech_type}' to '{remap[tech_type]}'")
                tech_type = remap[tech_type]
            
        # 1. Is it a GUID?
        try:
            uuid.UUID(name_or_guid)
            return name_or_guid
        except ValueError:
            pass
            
        # 2. Check local cache (real elements first!)
        key = find_key_with_value(name_or_guid)
        if key:
            cache_info = get_element_dictionary().get(key)
            if cache_info and "guid" in cache_info:
                return cache_info["guid"]

        # 3. Check current batch (planned_elements)
        planned = self.context.get("planned_elements", set())
        if name_or_guid in planned:
            return f"(Planned: {name_or_guid})"
        
        # 4. Check Egeria (Existence Check)
        try:
            # Use SDK's strict name-to-GUID resolution
            # This checks QN, Display Name, Resource Name, and Identifier via repository-services.
            res = None
            unsupported_type_warnings = self.context.setdefault("_unsupported_lookup_types_warned", set())
            try:
                # Pass 1: Try WITH type constraint (fastest, avoids ambiguity)
                res = await self.client._async_get_guid_for_name(name_or_guid, type_name=tech_type or None)
            except PyegeriaException as e:
                # Catch multiple matches error
                if "Multiple elements found" in str(e):
                    msg = f"Multiple elements found for name '{name_or_guid}' (Pass 1). Please use a unique Qualified Name."
                    logger.error(msg)
                    if "errors" not in self.parsed_output:
                        self.parsed_output["errors"] = []
                    self.parsed_output["errors"].append(msg)
                    return None
                if tech_type and self._is_unsupported_type_lookup_error(e):
                    error_id = self._extract_egeria_error_id(e) or "unknown-error-id"
                    if tech_type not in unsupported_type_warnings:
                        unsupported_type_warnings.add(tech_type)
                        self._add_warning(
                            f"Type constraint '{tech_type}' from command find_constraints is not recognized by this Egeria server ({error_id}); retrying lookup without type filter."
                        )
                    logger.warning(
                        f"Unsupported metadata type constraint '{tech_type}' while resolving '{name_or_guid}' ({error_id}). Falling back to untyped lookup."
                    )
                else:
                    logger.debug(f"SDK strict lookup (Pass 1) failed for '{name_or_guid}': {e}")
                    if self.context.get("directive") == "validate":
                        print_basic_exception(e)
                
            # Pass 2: If no result (or if type was invalid), try WITHOUT type constraint
            is_not_found = not res or (isinstance(res, str) and (res.startswith("No ") or " found" in res))
            if is_not_found and tech_type:
                try:
                    res = await self.client._async_get_guid_for_name(name_or_guid)
                except PyegeriaException as e:
                    if "Multiple elements found" in str(e):
                        msg = f"Multiple elements found for name '{name_or_guid}' (Pass 2). Please use a unique Qualified Name."
                        logger.error(msg)
                        if "errors" not in self.parsed_output:
                            self.parsed_output["errors"] = []
                        self.parsed_output["errors"].append(msg)
                        return None
                    logger.debug(f"SDK strict lookup (Pass 2) failed for '{name_or_guid}': {e}")
                    if self.context.get("directive") == "validate":
                        print_basic_exception(e)

            # Ensure it's not a "not found" indicator string
            if res and isinstance(res, str) and not res.startswith("No ") and " found" not in res and not res.startswith("(Planned:"):
                logger.debug(f"resolve_element_guid: SDK strict lookup for '{name_or_guid}' returned: {res}")
                return res
                
        except Exception as e:
            logger.debug(f"resolve_element_guid: Unexpected error resolving '{name_or_guid}': {e}")
            
        return None

    async def _extract_memberships_async(self, async_get_fn, guid: str) -> dict:
        """
        Async helper that fetches an element by GUID and extracts its
        collection memberships (DictList / SpecList).

        Works by awaiting the provided async getter function, then extracting
        the 'memberOfCollections' list from the response and classifying each
        entry by collectionType.

        Parameters
        ----------
        async_get_fn : coroutine function
            An async callable that accepts (guid, output_format="JSON") and
            returns the element dict.
        guid : str
            The GUID of the element to fetch.

        Returns
        -------
        dict  {"DictList": [...], "SpecList": [...], "CollectionDetails": [...]}
        """
        result = {"DictList": [], "SpecList": [], "CollectionDetails": []}
        try:
            info = await async_get_fn(guid, output_format="JSON")
            if not info or not isinstance(info, dict):
                return result
            for member_rel in info.get("memberOfCollections", []):
                related = member_rel.get("relatedElement", {})
                props = related.get("properties", {})
                coll_guid = related.get("elementHeader", {}).get("guid")
                collection_type = props.get("collectionType")
                if coll_guid:
                    if collection_type == "Data Dictionary":
                        result["DictList"].append(coll_guid)
                    elif collection_type == "Data Specification":
                        result["SpecList"].append(coll_guid)
                    result["CollectionDetails"].append({
                        "guid": coll_guid,
                        "description": props.get("description"),
                        "collectionType": collection_type,
                        "qualifiedName": props.get("qualifiedName"),
                    })
        except Exception as e:
            logger.warning(f"_extract_memberships_async: failed to get memberships for {guid}: {e}")
        return result

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        """
        Standardized lookup for the target element. 
        Checks the cache first.
        """
        if not self.supports_target_element_lookup():
            return None

        qn = self.parsed_output.get("qualified_name")
        
        # If QN is missing but Display Name is present, try deriving it
        if not qn:
            qn = self.derive_qualified_name()
            if qn:
                logger.debug(f"fetch_as_is: Derived QN '{qn}' for identification")
                self.parsed_output["qualified_name"] = qn

        if qn:
            # 1. Check Cache
            cache_info = get_element_dictionary().get(qn)
            if cache_info and "guid" in cache_info:
                try:
                    element = await self.fetch_element(cache_info["guid"])
                    if element:
                        return element
                except Exception:
                    pass
            
            guid = await self.resolve_element_guid(qn, tech_type=self.egeria_type_name)
            logger.debug(f"fetch_as_is: resolve_element_guid returned: {guid}")
            if guid and isinstance(guid, str) and not guid.startswith("(Planned:") and not guid.startswith("No "):
                try:
                    element = await self.fetch_element(guid)
                    if element:
                        logger.debug(f"fetch_as_is: Element found in Egeria for GUID '{guid}'")
                        # Update cache since we found it
                        attributes = self.parsed_output.get("attributes", {})
                        display_name = attributes.get('Display Name', {}).get('value', qn)
                        update_element_dictionary(qn, {"guid": guid, "display_name": display_name})
                        return element
                    else:
                        logger.debug(f"fetch_as_is: fetch_element returned None for GUID '{guid}'")
                except Exception as e:
                    logger.debug(f"fetch_as_is: fetch_element failed for GUID '{guid}': {e}")
        return None

    @abstractmethod
    async def apply_changes(self) -> str:
        """Apply side-effects to Egeria. Returns the updated markdown."""
        pass

    async def analyze_relationships(self) -> List[Dict[str, Any]]:
        """
        Analyze what relationships would be created/deleted.
        Subclasses should override this to return a list of dictionaries with info.
        E.g. [{'type': 'Collection Membership', 'added': [...], 'removed': [...]}]
        """
        return []

    async def display_only(self) -> str:
        """
        Display-only logic. Skips validation and Egeria lookups.
        Generates a clean markdown summary of the parsed attributes.
        """
        logger.info(f"DISPLAY ONLY: {self.command.verb} {self.command.object_type}")
        if not self.parsed_output:
            logger.error("display_only: self.parsed_output is None!")
            return "### Error: No parsed data available for display."
        
        attributes = self.parsed_output.get("attributes", {})
        report = [f"### Command: {self.command.verb} {self.command.object_type}"]
        if self.is_report_view_command():
            report_spec = attributes.get("Report Spec", {}).get("value", "")
            output_format = attributes.get("Output Format", {}).get("value", "JSON")
            report.extend([
                f"**Report Spec**: `{report_spec}`",
                f"**Output Format**: `{output_format}`",
                ""
            ])
        else:
            qualified_name = self.parsed_output.get("qualified_name")
            report.extend([f"**Qualified Name**: `{qualified_name}`", ""])

        report.extend([
            "#### Parsed Attributes",
            "| Attribute | Value |",
            "| :--- | :--- |"
        ])

        for name, details in attributes.items():
            raw = details.get("value", "")
            val = format_for_markdown_table(raw)
            
            report.append(f"| {name} | {val} |")
            
        report.append("\n---")
        return "\n".join(report)

    async def validate_only(self) -> str:
        """
        Standardized 'dry-run' logic. 
        Generates a rich markdown diagnostic summary of what *would* happen.
        """
        logger.info(f"DRY RUN: Validating {self.command.verb} {self.command.object_type}")
        if not self.parsed_output:
            logger.error("validate_only: self.parsed_output is None!")
            return "### Error: No parsed data available for validation."
        
        attributes = self.parsed_output.get("attributes", {})
        exists = self.parsed_output.get("exists", False)
        errors = self.parsed_output.get("errors", [])
        warnings = self.parsed_output.get("warnings", [])
        
        target_verb = self.command.verb
        guid_info = ""
        if exists:
            guid = ""
            if self.as_is_element:
                guid = self.as_is_element.get('elementHeader', {}).get('guid')
            if not guid:
                guid = self.parsed_output.get("guid") or ""
            guid_info = f" (GUID: {guid})" if guid else ""
        
        report = [
            f"### Command Analysis: {self.command.verb} {self.command.object_type}",
            f"**Action**: {target_verb}{guid_info}"
        ]
        if self.is_report_view_command():
            report_spec = attributes.get("Report Spec", {}).get("value", "")
            output_format = attributes.get("Output Format", {}).get("value", "JSON")
            report.extend([
                f"**Report Spec**: `{report_spec}`",
                f"**Output Format**: `{output_format}`",
                ""
            ])
        else:
            qualified_name = self.parsed_output.get("qualified_name")
            report.extend([f"**Qualified Name**: `{qualified_name}`", ""])

        report.extend([
            "#### Parsed Attributes",
            "| Attribute | Value | Status |",
            "| :--- | :--- | :--- |"
        ])

        for name, details in attributes.items():
            raw = details.get("value", "")
            val = format_for_markdown_table(raw)
            
            # Visual feedback for validation
            if details.get("is_default"):
                status = "ℹ️ Default"
            elif details.get("exists") is False:
                status = "❌ Not Found"
            elif details.get("is_planned"):
                status = "🕒 Planned"
            else:
                status = "✅ Valid" if details.get("valid") else "❌ Invalid"
                
            report.append(f"| {name} | {val} | {status} |")
            
        expanded = []
        for name, details in attributes.items():
            raw = details.get("value", "")
            if isinstance(raw, str) and ("\n" in raw or any(raw.strip().startswith(p) for p in ("- ", "* ", "1.", "#", ">", "```"))):
                expanded.append(f"##### {name}\n\n{raw}\n")

        if expanded:
            report.append("\n#### Rendered Attribute Details\n")
            report.extend(expanded)
            
        # Add Relationship Analysis
        rel_analysis = await self.analyze_relationships()
        if rel_analysis:
            report.append("\n#### 🔗 Relationship Changes")
            for rel in rel_analysis:
                rel_type = rel.get('type', 'Relationship')
                added = rel.get('added', [])
                removed = rel.get('removed', [])
                unchanged = rel.get('unchanged', [])
                
                if not added and not removed:
                    report.append(f"- **{rel_type}**: No changes.")
                else:
                    report.append(f"- **{rel_type}**:")
                    if added:
                        report.append(f"  - 🟢 **Adding**: {', '.join(added)}")
                    if removed:
                        report.append(f"  - 🔴 **Removing**: {', '.join(removed)}")
                    if unchanged:
                        report.append(f"  - ⚪ **Unchanged**: {', '.join(unchanged)}")

            
        if errors:
            report.append("\n#### ❌ Errors")
            for err in errors:
                report.append(f"- {err}")
                
        if warnings:
            report.append("\n#### ⚠️ Warnings")
            for warn in warnings:
                report.append(f"- {warn}")
                
        report.append("\n---")
        return "\n".join(report)

    async def sync_members(self, 
                           as_is_guids: set, 
                           to_be_guids: set, 
                           add_coro, 
                           remove_coro,
                           replace_all: bool = True) -> Dict[str, List[str]]:
        """
        Generic async relationship synchronization logic.
        Handles set comparison (As-Is vs To-Be) and executes provided coroutines.
        
        If replace_all is False, it only performs additions.
        """
        to_add = to_be_guids - as_is_guids
        to_remove = (as_is_guids - to_be_guids) if replace_all else set()
        
        results = {"added": [], "removed": [], "errors": []}
        
        if to_add:
            logger.debug(f"Sync: Adding {len(to_add)} members")
            for guid in to_add:
                try:
                    await add_coro(guid)
                    results["added"].append(guid)
                except Exception as e:
                    logger.error(f"Sync: Failed to add member {guid}: {e}")
                    results["errors"].append(f"Add {guid}: {e}")
                
        if to_remove:
            logger.debug(f"Sync: Removing {len(to_remove)} members")
            for guid in to_remove:
                try:
                    await remove_coro(guid)
                    results["removed"].append(guid)
                except Exception as e:
                    logger.error(f"Sync: Failed to remove member {guid}: {e}")
                    results["errors"].append(f"Remove {guid}: {e}")
                
        return results

    def filter_update_properties(self, properties: Dict[str, Any], merge_update: bool) -> Dict[str, Any]:
        """
        Filters properties for an update operation.
        If merge_update is True, it removes all None values to avoid overwriting 
        existing properties with nulls in Egeria.
        """
        if not merge_update:
            return properties
            
        # If merge_update is True, we only keep non-None values.
        # We MUST preserve core identification fields like 'class' and 'typeName'
        # which are used by the SDK to identify the property structure.
        identification_keys = {"class", "typeName"}
        return {k: v for k, v in properties.items() if v is not None or k in identification_keys}
