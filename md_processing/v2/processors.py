"""
Async-First Command Processors for Dr.Egeria v2.
"""
import uuid
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from loguru import logger

from pyegeria import EgeriaTech, PyegeriaException
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
            return {
                "output": self.command.raw_block,
                "status": "failure",
                "message": full_message,
                "verb": self.command.verb,
                "object_type": self.command.object_type
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

        # 5. Record this element in the shared 'planned_elements' set (if it's a create-like action)
        current_qn = self.parsed_output.get("qualified_name")
        planned = self.context.get("planned_elements")
        if isinstance(planned, set) and current_qn and self.command.verb in ["Create", "Define", "Register", "Add"]:
            planned.add(current_qn)

        # 6. Dry-run validation (optional/future)

        # 7. Global Lookups and Existential Checks for References (Relationship commands)
        if self.command.verb in ["Link", "Attach", "Add"]:
            # Check for attributes that are likely references (Contain 'Id' or 'Name' and aren't 'Display Name' or 'Qualified Name')
            for attr_name, attr_data in attributes.items():
                if any(k in attr_name for k in ["Id", "GUID", "Name"]) and attr_name not in ["Display Name", "Qualified Name", "Description"]:
                    val = attr_data.get("value")
                    if val and not attr_data.get("guid"):
                        # Try to resolve GUID from cache or Egeria
                        guid = await self.resolve_element_guid(val)
                        if guid:
                            attr_data["guid"] = guid
                            attr_data["exists"] = True
                        else:
                            attr_data["exists"] = False
                            attr_data["valid"] = False
                            logger.error(f"Referenced element '{val}' for attribute '{attr_name}' not found.")
                            if "errors" not in self.parsed_output:
                                 self.parsed_output["errors"] = []
                            self.parsed_output["errors"].append(f"Referenced element '{val}' for attribute '{attr_name}' not found.")

        # 7. Check for existence of the target element (As-Is state)
        if self.as_is_element:
            logger.debug(f"Element found! GUID: {self.parsed_output.get('guid')}")
        else:
            logger.debug(f"Element NOT found for QN: '{current_qn}'")
            self.parsed_output["exists"] = False
            if self.command.verb == "Update":
                logger.error(f"Target element for 'Update' not found: {self.parsed_output.get('qualified_name') or self.command.object_type}")
                if "errors" not in self.parsed_output:
                    self.parsed_output["errors"] = []
                self.parsed_output["errors"].append(f"Target element for 'Update' not found.")
                return {
                    "output": self.command.raw_block,
                    "status": "failure",
                    "message": f"Target element for Update not found.",
                    "verb": self.command.verb,
                    "object_type": self.command.object_type
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
                "warnings": self.parsed_output.get("warnings", [])
            }
        
        # Check for blockers before applying changes
        if self.parsed_output.get("errors"):
            return {
                "output": self.command.raw_block,
                "status": "failure",
                "message": f"Execution blocked: {'; '.join(self.parsed_output['errors'])}",
                "verb": self.command.verb,
                "object_type": self.command.object_type
            }

        output = await self.apply_changes()
        
        # 7. Post-execution: Update the cache on success
        if output and not output.startswith(self.command.raw_block): # Basic success check
            qn = self.parsed_output.get("qualified_name")
            guid = self.parsed_output.get("guid") or attributes.get("guid")
            if qn and guid:
                update_element_dictionary(qn, {"guid": guid, "display_name": display_name or qn})

        return {
            "output": output,
            "status": "success",
            "message": f"Executed {self.command.verb} {self.command.object_type}",
            "verb": self.command.verb,
            "object_type": self.command.object_type,
            "guid": self.parsed_output.get("guid") or attributes.get("guid"),
            "qualified_name": self.parsed_output.get("qualified_name"),
            "warnings": self.parsed_output.get("warnings", [])
        }

    def derive_qualified_name(self, attributes: Dict[str, Any]) -> str:
        """
        Derive a qualified_name from 'Display Name' (or other basis) and the command spec.
        """
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

        # Extract Version Identifier if present 
        version_identifier = attributes.get("Version Identifier", {}).get("value")

        # Reach into 'collections' subclient which is guaranteed to have the helper
        helper = getattr(self.client, 'collections', self.client)
        if hasattr(helper, "__create_qualified_name__"):
            return helper.__create_qualified_name__(
                type_name=qn_prefix,
                display_name=display_name,
                version_identifier=version_identifier or ""
            )
        else:
            # Basic fallback if SDK helper unavailable
            return f"{qn_prefix}::{display_name}"

    async def render_result_markdown(self, guid: str) -> str:
        """
        Fetch the element by GUID and render it into markdown using the appropriate report_spec.
        """
        if not guid:
            return self.command.raw_block
            
        # 1. Determine the report spec name
        # Convention: <Type>-DrE
        report_spec_name = f"{self.command.object_type}-DrE"
        
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
        Fetch the element bean for rendering. 
        Subclasses should override if MetadataExplorer is unavailable.
        """
    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the details of an element by GUID. 
        Subclasses should override if MetadataExplorer is unavailable or if a specific OMAS method is needed.
        """
        try:
            # First try generic element retrieval
            return await self.client._async_get_metadata_element_by_guid(guid)
        except (PyegeriaException, AttributeError):
            # Fallback for servers without MetadataExplorer
            logger.debug("Generic element fetch failed, trying specific lookup fallback")
            return None

    async def resolve_element_guid(self, name_or_guid: str) -> Optional[str]:
        """
        Try to resolve a GUID from a string which could be a GUID, a Qualified Name, 
        or a Display Name.
        Checks the local cache first, then Egeria.
        """
        if not name_or_guid:
            return None
            
        # 1. Is it a GUID?
        try:
            uuid.UUID(name_or_guid)
            return name_or_guid
        except ValueError:
            pass
            
        # 2. Check local cache
        key = find_key_with_value(name_or_guid)
        if key:
            cache_info = get_element_dictionary().get(key)
            if cache_info and "guid" in cache_info:
                return cache_info["guid"]
        
        # 2b. Check 'planned_elements' (for forward references in same batch)
        planned = self.context.get("planned_elements")
        if isinstance(planned, set) and name_or_guid in planned:
            # Return a special string to indicate it exists but has no real GUID yet
            return f"(Planned: {name_or_guid})"
        
        # 3. Check Egeria (expensive fallback)
        try:
            # 3a. If it looks like a qualified name (contains ::), try exact unique name lookup
            # This is much more robust for the Create -> Update transition
            if "::" in name_or_guid:
                # EgeriaTech delegates to MetadataExplorer
                try:
                    res = await self.client._async_get_metadata_guid_by_unique_name(name_or_guid, "qualifiedName")
                    logger.debug(f"Step 3a: MetadataExplorer lookup for '{name_or_guid}' returned: {res}")
                    if res and res != "No element found" and isinstance(res, str):
                        return res
                except (PyegeriaException, AttributeError) as e:
                    logger.debug(f"Step 3a: MetadataExplorer lookup failed or unavailable: {e}")
            
            # 3b. Try specific search if it's a known type and we have a name
            # We use find_method if available in spec
            spec = self.get_command_spec()
            find_method_name = spec.get("find_method")
            if find_method_name:
                try:
                    # Parse 'Manager.method' or just 'method'
                    method_parts = find_method_name.split('.')
                    mgr_method = method_parts[-1]
                    # Direct delegation usually handles it
                    method = getattr(self.client, f"_async_{mgr_method}", None)
                    if method:
                        # Extract name basis properly (handling version identifiers)
                        parts = name_or_guid.split("::")
                        # Based on our __create_qualified_name__ logic:
                        # [prefix, type, name, version] -> parts[-2]
                        # [prefix, type, name] -> parts[-1]
                        # [type, name] -> parts[-1]
                        
                        basis = parts[-2] if len(parts) >= 4 else parts[-1]
                        logger.debug(f"Step 3b: Specific search using {mgr_method} for basis '{basis}'")
                        results = await method(basis)
                        if isinstance(results, list) and len(results) > 0:
                            for res in results:
                                header = res.get("elementHeader", {})
                                qn = header.get("qualifiedName") or res.get("properties", {}).get("qualifiedName")
                                logger.debug(f"Step 3b: Checking result '{qn}' against '{name_or_guid}'")
                                if qn == name_or_guid:
                                    return header.get("guid") or res.get("guid") or res.get("elementHeader",{}).get("guid")
                        else:
                            logger.debug(f"Step 3b: No results found for basis '{basis}'")
                except Exception as e:
                    logger.debug(f"Step 3b: Specific search failed: {e}")

            # 3c. Try by name (generic search or specific client method)
            # For now, let's use a generic search if possible, or common lookup
            # Many processors have specific lookup logic. Maybe we can leverage that.
            element = await self.client._async_get_metadata_element_by_name(name_or_guid)
            if element:
                header = element.get("elementHeader")
                if header and "guid" in header:
                    return header["guid"]
        except Exception:
            pass
            
        return None

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        """
        Standardized lookup for the target element. 
        Checks the cache first.
        """
        qn = self.parsed_output.get("qualified_name")
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
            logger.debug(f"fetch_as_is: resolve_element_guid for '{qn}' returned: {guid}")
            if guid and not guid.startswith("(Planned:"):
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

    async def validate_only(self) -> str:
        """
        Standardized 'dry-run' logic. 
        Generates a rich markdown diagnostic summary of what *would* happen.
        """
        logger.info(f"DRY RUN: Validating {self.command.verb} {self.command.object_type}")
        
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
