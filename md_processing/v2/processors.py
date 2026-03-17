"""
Async-First Command Processors for Dr.Egeria v2.
"""
import uuid
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from loguru import logger

from pyegeria import EgeriaTech, PyegeriaException
from pyegeria.core.utils import make_format_set_name_from_type
from pyegeria.view.base_report_formats import select_report_spec
from pyegeria.view.output_formatter import generate_output

from md_processing.v2.extraction import DrECommand
from md_processing.v2.parsing import AttributeFirstParser
from md_processing.md_processing_utils.md_processing_constants import get_command_spec
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
            
        self.parser = AttributeFirstParser(self.command, client=self.client)
        self.parsed_output = None
        self.as_is_element = None
        
        # Resolve canonical name from spec
        spec = self.get_command_spec()
        if spec:
            self.canonical_object_type = spec.get("display_name") or self.command.object_type
            if " " in self.canonical_object_type:
                # Use only the object part if display_name is "Verb Object"
                _verb, obj = spec.get("verb", ""), self.canonical_object_type
                if obj.startswith(f"{_verb} "):
                    self.canonical_object_type = obj[len(_verb)+1:]
        else:
            self.canonical_object_type = self.command.object_type

    def get_command_spec(self) -> Dict[str, Any]:
        """Return the JSON specification for this command family."""
        # Use full command name to ensure alternate names match correctly
        spec = get_command_spec(f"{self.command.verb} {self.command.object_type}")
        return spec or {}

    async def execute(self) -> Dict[str, Any]:
        """
        Orchestrate the command execution flow.
        Returns a dictionary containing the output markdown and execution metadata.
        """
        directive = self.context.get("directive", "process")
        
        # 1. Parse attributes using the spec-agnostic parser
        spec = self.get_command_spec()
        self.parsed_output = self.parser.parse()
        
        # 2. Pre-flight Validation (check required fields, etc.)
        if not self.parsed_output.get("valid", True):
            errors = self.parsed_output.get("errors", [])
            err_msg = "; ".join(errors) if errors else "General validation failure"
            full_message = f"Validation failed: {err_msg}"
            logger.error(f"{full_message} for {self.command.verb} {self.command.object_type}")
            logger.debug(f"Parsed Output: {self.parsed_output}")
            
            # Even if invalid, we want to show the diagnosis table if possible
            output = await self.validate_only()
            return {
                "output": output,
                "status": "failure",
                "message": full_message,
                "verb": self.command.verb,
                "object_type": self.command.object_type,
                "found": self.parsed_output.get("exists", False),
                "errors": errors
            }

        # 3. Ensure qualified_name is populated
        attributes = self.parsed_output.get("attributes", {})
        
        if not self.parsed_output.get("qualified_name"):
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
        
        # 4. Fetch As-Is state (Lookup by GUID or QN)
        # We do this BEFORE recording in planned_elements to avoid self-shadowing 
        # (where an element sees itself in 'planned' and skips the Egeria lookup)
        self.as_is_element = await self.fetch_as_is()
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
        # We check all attributes that look like references or are marked as Reference Name/ID in spec
        for attr_name, attr_data in attributes.items():
            # Get the style from the spec if possible
            spec_style = "Simple"
            spec = self.get_command_spec()
            if spec:
                spec_attrs = spec.get("Attributes", spec.get("attributes", []))
                for a in spec_attrs:
                    if isinstance(a, dict):
                        # Flattened or nested
                        if a.get("name") == attr_name:
                            spec_style = a.get("style", "Simple")
                            break
                        elif attr_name in a:
                            val = a[attr_name]
                            if isinstance(val, dict):
                                spec_style = val.get("style", "Simple")
                                break
                            else:
                                # In compact specs, it might just be the value
                                spec_style = "Simple"
                                break
            
            # Heuristics for identifying what attributes represent references to other elements
            # We exclude common string attributes that might contain keywords like "Reference" or "Name"
            non_ref_names = [
                "Display Name", "Qualified Name", "Description", 
                "Reference Abstract", "Reference Title", "Reference Description",
                "Abstract", "Title", "Category", "Organization", "URL", "License", "Copyright"
            ]
            
            is_ref_candidate = (
                spec_style in ["Reference Name", "ID", "GUID", "Reference"]
            ) or (
                any(k in attr_name for k in ["Id", "GUID", "Name", "Reference"]) 
                and attr_name not in non_ref_names
                and spec_style != "Simple" # If spec explicitly says Simple, trust it unless it looks very much like an ID
            )
            
            # More precise check: if it's already got a GUID, don't re-resolve. 
            # If it's a value but no GUID, and it's a candidate, try to resolve.
            val = attr_data.get("value")
            if val and not attr_data.get("guid") and is_ref_candidate:
                # Try to resolve GUID from cache or Egeria
                guid = await self.resolve_element_guid(val)
                if guid:
                    attr_data["guid"] = guid
                    # If it's a 'Planned' element, it counts as exists for validation
                    attr_data["exists"] = True
                    if guid.startswith("(Planned:"):
                        attr_data["is_planned"] = True
                else:
                    # If it's a candidate ref and we couldn't resolve it, mark as not found
                    attr_data["exists"] = False
                    attr_data["valid"] = False
                    msg = f"Referenced element '{val}' for attribute '{attr_name}' not found."
                    if attr_data.get("warnings") is None: attr_data["warnings"] = []
                    attr_data["warnings"].append(msg)
                    if directive == "validate":
                        logger.warning(msg)
                        if "warnings" not in self.parsed_output:
                            self.parsed_output["warnings"] = []
                        self.parsed_output.get("warnings", []).append(msg)
                    else:
                        logger.error(msg)
                        if "errors" not in self.parsed_output:
                            self.parsed_output["errors"] = []
                        self.parsed_output.get("errors", []).append(msg)

        # 7. Check for existence of the target element (As-Is state)
        if self.as_is_element:
            logger.debug(f"Element found! GUID: {self.parsed_output.get('guid')}")
        else:
            logger.debug(f"Element NOT found for QN: '{current_qn}'")
            self.parsed_output["exists"] = False
            if self.command.verb == "Update":
                logger.debug(f"Target element for 'Update' not found: {self.parsed_output.get('qualified_name') or self.command.object_type}")
                if "errors" not in self.parsed_output:
                    self.parsed_output["errors"] = []
                self.parsed_output["errors"].append(f"Target element for 'Update' not found.")
                
                if directive == "validate":
                    logger.info("Validation mode: Proceeding to validate_only despite missing update target.")
                    output = await self.validate_only()
                    return {
                        "output": output,
                        "status": "failure",
                        "message": f"Target element for Update not found.",
                        "verb": self.command.verb,
                        "object_type": self.command.object_type,
                        "found": False,
                        "errors": self.parsed_output["errors"]
                    }

                return {
                    "output": self.command.raw_block,
                    "status": "failure",
                    "message": f"Target element for Update not found.",
                    "verb": self.command.verb,
                    "object_type": self.command.object_type,
                    "found": False
                }

        # 6. Action Dispatch
        if directive == "validate":
            output = await self.validate_only()
            # If relationship and missing ends, the validate_only output should reflect this.
            # We check errors at the end of validate_only
            status = "success" if not self.parsed_output.get("errors") else "failure"
            return {
                "output": output,
                "status": status,
                "message": f"Validated {self.command.verb} {self.command.object_type}",
                "verb": self.command.verb,
                "object_type": self.command.object_type,
                "guid": self.parsed_output.get("guid"),
                "found": self.parsed_output.get("exists", False),
                "warnings": self.parsed_output.get("warnings", [])
            }
        
        # Check for blockers before applying changes
        if self.parsed_output.get("errors"):
            return {
                "output": self.command.raw_block,
                "status": "failure",
                "message": f"Execution blocked: {'; '.join(self.parsed_output['errors'])}",
                "verb": self.command.verb,
                "object_type": self.command.object_type,
                "guid": self.parsed_output.get("guid"),
                "found": self.parsed_output.get("exists", False)
            }

        output = await self.apply_changes()
        
        # 7. Post-execution: Update the cache on success
        guid = self.parsed_output.get("guid") or attributes.get("guid")
        if output and not output.startswith(self.command.raw_block): # Basic success check
            qn = self.parsed_output.get("qualified_name")
            if qn and guid:
                d_name = self.parsed_output.get("display_name") or qn
                update_element_dictionary(qn, {"guid": guid, "display_name": d_name})

        return {
            "output": output,
            "status": "success",
            "message": f"Executed {self.command.verb} {self.command.object_type}" + (f" (GUID: {guid})" if guid else ""),
            "verb": self.command.verb,
            "object_type": self.command.object_type,
            "guid": guid,
            "qualified_name": self.parsed_output.get("qualified_name"),
            "found": self.parsed_output.get("exists", False),
            "warnings": self.parsed_output.get("warnings", [])
        }

    def derive_qualified_name(self, attributes: Optional[Dict[str, Any]] = None) -> str:
        """
        Derive a qualified_name from 'Display Name' (or other basis) and the command spec.
        """
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
        
        # Strip trailing colon if present
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
        report_spec_name = make_format_set_name_from_type(self.command.object_type)
        
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
            logger.warning(f"Report spec '{report_spec_name}' not found. Falling back to default.")
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
        Subclasses should override if MetadataExplorer is unavailable or if a specific OMAS method is needed.
        """
        try:
            # First try MetadataExplorer (most detailed properties)
            res = await self.client._async_get_metadata_element_by_guid(guid)
            if res and isinstance(res, dict):
                return res
        except Exception as e:
            logger.debug(f"MetadataExplorer fetch failed: {e}")
            
        try:
            # Fallback to ClassificationExplorer if MetadataExplorer is missing
            logger.debug("Trying ClassificationExplorer fallback for element fetch.")
            res = await getattr(self.client, "_async_get_element_by_guid_")(guid)
            if res and isinstance(res, dict):
                # The structure from classification-explorer comes under "element" usually
                if "element" in res:
                    return res["element"]
                return res
        except Exception as e:
            logger.debug(f"ClassificationExplorer fallback failed: {e}")

        return None

    async def resolve_element_guid(self, name_or_guid: str) -> Optional[str]:
        """
        Resolves a name or GUID to a GUID using various strategies.
        Returns None if not found, or f"(Planned: {name})" if it's a forward reference.
        """
        if not name_or_guid:
            return None
            
        import sys
        sys.stdout.flush()

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
        
        # 4. Check Egeria (strict lookup)
        try:
            # 4a. Use SDK's strict name-to-GUID resolution
            # This checks QN, Display Name, Resource Name, and Identifier.
            # It raises PyegeriaException if multiple matches are found.
            try:
                res = await self.client._async_get_guid_for_name(name_or_guid)
                # Ensure it's not a "not found" indicator string
                if res and isinstance(res, str) and not res.startswith("No ") and " found" not in res and not res.startswith("(Planned:"):
                    logger.debug(f"resolve_element_guid: SDK strict lookup for '{name_or_guid}' returned: {res}")
                    return res
            except PyegeriaException as e:
                # Catch multiple matches error
                if "Multiple elements found" in str(e):
                    msg = f"Multiple elements found for name '{name_or_guid}'. Please use a unique Qualified Name."
                    logger.error(msg)
                    if "errors" not in self.parsed_output:
                        self.parsed_output["errors"] = []
                    self.parsed_output["errors"].append(msg)
                    return None
                logger.debug(f"SDK strict lookup failed for '{name_or_guid}': {e}")


            # 4c. Try find_method search from spec
            spec = self.get_command_spec()
            find_method_name = spec.get("find_method")
            if find_method_name:
                try:
                    method_parts = find_method_name.split('.')
                    mgr_method = method_parts[-1]
                    method = getattr(self.client, f"_async_{mgr_method}", None)
                    if method:
                        parts = name_or_guid.split("::")
                        basis = parts[-2] if len(parts) >= 4 else parts[-1]
                        results = await method(basis or name_or_guid)
                        if isinstance(results, list) and len(results) > 0:
                            for res in results:
                                qn = (res.get("elementHeader", {}).get("qualifiedName") or 
                                      res.get("properties", {}).get("qualifiedName"))
                                if qn == name_or_guid:
                                    return res.get("guid") or res.get("elementHeader", {}).get("guid")
                except Exception:
                    pass

        except Exception as e:
            logger.debug(f"resolve_element_guid: Unexpected error resolving '{name_or_guid}': {e}")
            
        return None

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        """
        Standardized lookup for the target element. 
        Checks the cache first.
        """
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
            
            # 2. Check Egeria (Harden against missing cache in new sessions)
            guid = await self.resolve_element_guid(qn)
            logger.debug(f"fetch_as_is: resolve_element_guid returned: {guid}")
            if guid and isinstance(guid, str) and not guid.startswith("(Planned:") and not guid.startswith("No "):
                try:
                    # Sanity check: is it a GUID?
                    try:
                        uuid.UUID(guid)
                    except (ValueError, TypeError):
                        logger.debug(f"fetch_as_is: Resolved string '{guid}' is not a valid GUID. Skipping fetch.")
                        return None

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
        qualified_name = self.parsed_output.get("qualified_name")
        exists = self.parsed_output.get("exists", False)
        errors = self.parsed_output.get("errors", [])
        warnings = self.parsed_output.get("warnings", [])
        
        target_verb = "Update" if exists else "Create"
        guid_info = f" (GUID: {self.as_is_element['elementHeader']['guid']})" if exists else ""
        
        report = [
            f"### Validation Diagnosis: {self.command.verb} {self.command.object_type}",
            f"**Proposed Action**: {target_verb}{guid_info}",
            f"**Qualified Name**: `{qualified_name}`",
            "",
            "#### Parsed Attributes",
            "| Attribute | Value | Status |",
            "| :--- | :--- | :--- |"
        ]
        
        for name, details in attributes.items():
            val = str(details.get("value", ""))
            # Truncate long values
            if len(val) > 50:
                val = val[:47] + "..."
            
            # Visual feedback for existential validation
            if details.get("exists") is False:
                status = "❌ Not Found"
            elif details.get("is_planned"):
                status = "🕒 Planned"
            else:
                status = "✅ Valid" if details.get("valid") else "❌ Invalid"
                
            report.append(f"| {name} | {val} | {status} |")
            
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
        
        results = {"added": [], "removed": []}
        
        if to_add:
            logger.debug(f"Sync: Adding {len(to_add)} members")
            for guid in to_add:
                await add_coro(guid)
                results["added"].append(guid)
                
        if to_remove:
            logger.debug(f"Sync: Removing {len(to_remove)} members")
            for guid in to_remove:
                await remove_coro(guid)
                results["removed"].append(guid)
                
        return results
