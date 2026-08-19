"""
Async-First Command Processors for Dr.Egeria v2.
"""
import uuid
import asyncio
import json
import re
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union
from loguru import logger

from pyegeria import EgeriaTech, PyegeriaException, PyegeriaTimeoutException, NO_ELEMENTS_FOUND, print_basic_exception
from pyegeria.core.utils import make_format_set_name_from_type
from pyegeria.view.base_report_formats import select_report_spec
from pyegeria.view.output_formatter import generate_output, format_for_markdown_table, populate_columns_from_properties

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
                # Egeria GUIDs are typically UUIDs (36 chars) or at least 8+ chars of hex/dashes
                # We want to avoid returning "GUIDResponse" or other descriptive strings.
                if re.match(r"^[a-fA-F0-9-]{8,}$", candidate):
                    return candidate
                return None

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

    # Egeria's "0422 Governed Data Classifications" - Confidentiality/Confidence/
    # Criticality/Retention/Impact. Maps Dr.Egeria attribute name -> (classification
    # short name used in classification_manager's _async_set_X_classification/
    # _async_clear_X_classification method names, the Properties "class" value, the
    # real Java property field for the enum level, and the enum-string -> int map).
    #
    # The "real Java property field" column matters: both pyegeria's own docstrings
    # and the compact spec's attribute descriptions document this uniformly (and
    # wrongly) as "levelIdentifier" (Retention: "basisIdentifier", Impact:
    # "severityIdentifier") - confirmed live against qs-view-server that calling
    # set_X_classification with that documented name returns no error but silently
    # fails to attach the classification at all. The field names below are the real
    # ones (cross-checked against each XProperties.java class in egeria core and
    # confirmed live via a direct classify + fetch round-trip).
    _GOVERNANCE_CLASSIFICATION_MAP = {
        "Confidentiality Classification": (
            "confidentiality", "ConfidentialityProperties", "confidentialityLevel",
            {"UNCLASSIFIED": 0, "INTERNAL": 1, "CONFIDENTIAL": 2, "SENSITIVE": 3, "RESTRICTED": 4, "OTHER": 99},
        ),
        "Confidence Classification": (
            "confidence", "ConfidenceProperties", "confidenceLevel",
            {"UNCLASSIFIED": 0, "AD_HOC": 1, "TRANSACTIONAL": 2, "AUTHORITATIVE": 3, "DERIVED": 4, "OBSOLETE": 5, "OTHER": 99},
        ),
        "Criticality Classification": (
            "criticality", "CriticalityProperties", "criticalityLevel",
            {"UNCLASSIFIED": 0, "MARGINAL": 1, "IMPORTANT": 2, "CRITICAL": 3, "CATASTROPHIC": 4, "OTHER": 99},
        ),
        "Retention Classification": (
            # "RetentionClassificationProperties" (the server's registered Jackson
            # subtype ID for this classification - confirmed live via its own
            # InvalidTypeIdException error listing all valid ids) is the correct
            # class name to send, despite the real Java properties class's own
            # simple name being "RetentionProperties" - do not "fix" this to
            # "RetentionProperties", that's the wrong direction (confirmed live
            # 2026-08-03: sending "RetentionProperties" gets rejected by Jackson
            # outright as an unrecognized subtype id).
            #
            # Previously blocked server-side (see BACKLOG.md history) by
            # OMRS-REPOSITORY-400-028 ("a property called statusIdentifier ...
            # is not supported for this type") even though this code never sent
            # that field - an Egeria server-side ClassificationDef registration
            # gap, not a pyegeria issue. Confirmed fixed server-side 2026-08-03:
            # live round-trip (Create Project with Retention Classification:
            # PROJECT_LIFETIME through the real Dr.Egeria pipeline) now persists
            # correctly, server-populated statusIdentifier default included.
            "retention", "RetentionClassificationProperties", "retentionBasis",
            {"UNCLASSIFIED": 0, "TEMPORARY": 1, "PROJECT_LIFETIME": 2, "TEAM_LIFETIME": 3, "CONTRACT_LIFETIME": 4, "REGULATED_LIFETIME": 5, "TIMEBOXED_LIFETIME": 6, "OTHER": 99},
        ),
        "Impact Classification": (
            "impact", "ImpactProperties", "severityLevel",
            {"UNCLASSIFIED": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "OTHER": 99},
        ),
    }

    _GOVERNANCE_STATUS_MAP = {
        "PROPOSED": 0,
        "VALIDATED": 1,
        "DEPRECATED": 2,
        "OBSOLETE": 3,
        "OTHER": 99
    }

    async def _sync_governance_classifications(self, guid: str, attributes: Dict[str, Any]) -> None:
        """
        Apply Confidentiality/Confidence/Criticality/Retention/Impact classifications
        when the corresponding Dr.Egeria attribute is present. These can legitimately
        change over an element's lifetime (unlike Anchors), so this runs for both
        Create and Update, the same as _sync_zone_membership - and like zone
        membership, Egeria's classification handler reclassifies in place, so
        calling set_X_classification again with a new value is a safe update, not a
        duplicate-classification error (confirmed live).
        """
        status_attr = attributes.get("Status", {})
        status_value = status_attr.get("value")
        status_ordinal = None
        if status_value:
            status_ordinal = self._GOVERNANCE_STATUS_MAP.get(str(status_value).strip().upper())

        for attr_name, (short_name, prop_class, field_name, enum_map) in self._GOVERNANCE_CLASSIFICATION_MAP.items():
            attr_data = attributes.get(attr_name, {})
            if "value" not in attr_data:
                continue
            value = attr_data.get("value")
            set_method = getattr(self.client.classification_manager, f"_async_set_{short_name}_classification")
            clear_method = getattr(self.client.classification_manager, f"_async_clear_{short_name}_classification")
            try:
                if not value:
                    await clear_method(guid)
                    self.add_related_result(attr_name, guid=guid, message="Cleared")
                    continue
                level = enum_map.get(str(value).strip().upper())
                if level is None:
                    logger.warning(f"Unrecognized value '{value}' for '{attr_name}'; skipping classification sync.")
                    continue

                properties = {"class": prop_class, field_name: level}
                if status_ordinal is not None:
                    properties["statusIdentifier"] = status_ordinal

                body = {"class": "NewClassificationRequestBody", "properties": properties}
                await set_method(guid, body)
                self.add_related_result(attr_name, guid=guid, message=f"Set to {value}")
            except PyegeriaException as e:
                logger.error(f"Error syncing {attr_name} for {guid}: {e}")
                self.add_related_result(attr_name, guid=guid, status="failure", message=str(e))

    async def _sync_zone_membership(self, guid: str, attributes: Dict[str, Any]) -> None:
        """
        Apply the "Zone Membership" attribute (a ZoneMembershipProperties classification,
        not a plain Referenceable property) to the element just created/updated.

        Egeria's classification handler reclassifies in place, so a single
        add_zone_membership call is safe for both create and update; an empty/cleared
        list removes the classification instead.
        """
        zone_attr = attributes.get("Zone Membership", {})
        if "value" not in zone_attr:
            return
        zones = zone_attr.get("value")
        try:
            if zones:
                body = {
                    "class": "NewClassificationRequestBody",
                    "properties": {"class": "ZoneMembershipProperties", "zoneMembership": zones},
                }
                await self.client._async_add_zone_membership(guid, body)
                self.add_related_result("Zone Membership", guid=guid, message=f"Set to {zones}")
            else:
                await self.client._async_clear_zone_membership(
                    guid, {"class": "DeleteClassificationRequestBody"}
                )
                self.add_related_result("Zone Membership", guid=guid, message="Cleared")
        except PyegeriaException as e:
            logger.error(f"Error syncing Zone Membership for {guid}: {e}")
            self.add_related_result("Zone Membership", guid=guid, status="failure", message=str(e))

    async def _sync_parent_relationship(self, guid: str, attributes: Dict[str, Any]) -> None:
        """
        Establish the relationship declared by 'Parent ID' + 'Parent Relationship
        Type Name' (+ optional 'Parent Relationship Attributes'/'Parent at End1')
        on the element just created/updated.

        Egeria's create-time NewElementRequestBody bundles "create the element"
        and "link it to this one named parent relationship" into a single call -
        there is no Update-time equivalent of that shortcut (UpdateElementRequestBody
        has no anchor/parent fields at all), so on Update this relationship was
        previously silently dropped. This applies the same effect explicitly via
        the generic MetadataExpert relationship calls (any Egeria relationship
        type, not just ones with a dedicated OMVS wrapper), for both Create and
        Update - idempotent, so calling it after a Create (where the shortcut
        already established it) is a safe no-op.

        Anchor ID / Anchor Scope ID are NOT handled here - Egeria implements
        anchoring as a classification, not a relationship, so this mechanism
        doesn't apply to them.
        """
        parent_guid = attributes.get("Parent ID", {}).get("guid")
        if not parent_guid or str(parent_guid).startswith("(Planned:"):
            return

        rel_type = (
            attributes.get("Parent Relationship Type Name", {}).get("value")
            or attributes.get("Parent Relationship Type", {}).get("value")
        )
        if not rel_type:
            return

        rel_props = (
            attributes.get("Parent Relationship Attributes", {}).get("value")
            or attributes.get("Parent Relationship Properties", {}).get("value")
        )
        parent_at_end1 = attributes.get("Parent at End1", {}).get("value", True)
        end_1_guid, end_2_guid = (parent_guid, guid) if parent_at_end1 else (guid, parent_guid)

        try:
            existing = await self.client.metadata_expert._async_get_all_related_elements(guid)
            current_parent_guid = None
            current_relationship_guid = None
            # _async_get_all_related_elements returns a dict, not a list -
            # {"startingElement": {...}, "elementList": [...], "mermaidGraph": ...} -
            # and each elementList entry is the low-level MetadataExpert shape
            # (type.typeName / relationshipGUID / element.elementGUID), NOT the
            # friendlier relationshipHeader/relatedElement shape returned by
            # domain-specific get-by-guid calls like ProjectManager's (confirmed
            # by inspecting a live response - the two are genuinely different).
            element_list = existing.get("elementList", []) if isinstance(existing, dict) else []
            for rel in element_list:
                try:
                    if rel["type"]["typeName"] != rel_type:
                        continue
                    related_guid = rel["element"]["elementGUID"]
                except (KeyError, TypeError):
                    continue
                current_parent_guid = related_guid
                current_relationship_guid = rel.get("relationshipGUID")
                if related_guid == parent_guid:
                    break

            if current_parent_guid == parent_guid:
                return  # Already correct - idempotent no-op.

            if current_parent_guid and current_relationship_guid:
                # Re-parenting: remove the stale relationship of this type first.
                # An explicit body is required here - passing none crashes with
                # AttributeError inside pyegeria's _async_open_metadata_delete_body_request
                # (its validator returns None for a None body, then unconditionally
                # calls .model_dump() on that None).
                await self.client.metadata_expert._async_delete_related_elements(
                    current_relationship_guid, {"class": "OpenMetadataDeleteRequestBody"}
                )

            body = {
                "class": "NewRelatedElementsRequestBody",
                "type_name": rel_type,
                "metadata_element_1_guid": end_1_guid,
                "metadata_element_2_guid": end_2_guid,
            }
            if isinstance(rel_props, dict):
                body["properties"] = rel_props
            await self.client.metadata_expert._async_create_related_elements(body)
            self.add_related_result("Parent Relationship", guid=parent_guid, message=f"Linked via {rel_type}")
        except PyegeriaException as e:
            logger.error(f"Error syncing parent relationship for {guid}: {e}")
            self.add_related_result("Parent Relationship", guid=guid, status="failure", message=str(e))

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
                            ele_props = element.get("properties", {}) if "properties" in element else element.get("elementProperties", {})
                            ele_qn = ele_props.get("qualifiedName")
                            my_qn = self.parsed_output.get("qualified_name")
                            if ele_qn and my_qn and ele_qn != my_qn:
                                # ISSUE-59: this is a real, silent-duplication risk, not just an
                                # informational log line -- proceeding as Create here will mint a
                                # second element sharing this Display Name. Surface it to the
                                # caller so it's visible in the rendered --process/--validate
                                # output, not only in the debug log.
                                msg = (
                                    f"Found existing element with Display Name '{display_name}' (GUID: "
                                    f"{existing_guid}) but under a different Qualified Name ('{ele_qn}' vs. "
                                    f"'{my_qn}'). Proceeding as Create -- if you meant to update/rename that "
                                    f"element, re-run with '### GUID {existing_guid}' to target it directly."
                                )
                                logger.info(msg)
                                self._add_warning(msg)
                            else:
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

        # 5. Determine element existence and handle Upsert (Create <-> Update) transitions
        #
        # Gated on supports_target_element_lookup(): a relationship-only
        # processor (GovernanceLinkProcessor, ActionProcessStepLinkProcessor,
        # LineageLinkProcessor/UpdateLineageRelationshipProcessor, ...) has no
        # target Referenceable element to track existence/qualified-name for,
        # so as_is_element is always None and current_qn is always empty --
        # which, left ungated, made every branch below fall into "doesn't
        # exist anywhere" and silently rewrite verb="Update" to verb="Create"
        # for ANY relationship processor with an Update command (confirmed
        # live, ISSUE-68 follow-up: broke the new "Update Certification"/
        # "Update License"/"Update Next Process Step" commands as well as the
        # pre-existing "Update Lineage Relationship", which had apparently
        # never been exercised through --validate/--process with a full
        # valid attribute set before).
        # current_qn is read unconditionally (referenced further down in this
        # method regardless of supports_target_element_lookup()); only the
        # existence/rewrite side effects below are gated.
        current_qn = self.parsed_output.get("qualified_name")
        if self.supports_target_element_lookup():
            planned = self.context.get("planned_elements")

            # Check if it was already planned by a previous command in the same file
            is_already_planned = False
            if isinstance(planned, set) and current_qn:
                is_already_planned = current_qn in planned

            if self.as_is_element:
                # Transition Create -> Update if it already exists in Egeria
                if self.command.verb in ["Create", "Define", "Register", "Add", "Upsert"]:
                    logger.info(f"Rewriting '{self.command.verb} {self.command.object_type}' to 'Update' as it already exists.")
                    self.command.verb = "Update"

                self.parsed_output["exists"] = True
                header = self.as_is_element.get('elementHeader', {})
                self.parsed_output["guid"] = header.get('guid')
            elif not is_already_planned:
                # Transition Update -> Create if it doesn't exist anywhere
                if self.command.verb in ["Update", "Modify", "Upsert"]:
                    logger.info(f"Rewriting '{self.command.verb} {self.command.object_type}' to 'Create' as it does not exist.")
                    self.command.verb = "Create"
                self.parsed_output["exists"] = False
            else:
                # Found in planned_elements (planned by previous command)
                self.parsed_output["exists"] = True
                self.parsed_output["is_planned"] = True
                # Note: Step 7 will resolve the (Planned: ...) GUID

            # Record this element in the shared 'planned_elements' set for subsequent commands
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
                    "Display Name", "Qualified Name", "Description", "Label",
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
                        # "Simple"/"Simple List"/"List"/"NameList" without an explicit
                        # `existing_element` type (already handled above) are plain data,
                        # not element references, regardless of what the attribute name
                        # contains - e.g. "Match Property Names" (Simple List) is a list
                        # of arbitrary property-name strings, not a list of Egeria
                        # elements to resolve. Without this exclusion, the substring
                        # heuristic on "Name" wrongly flagged it as a reference
                        # candidate, and every one of its plain string values then
                        # failed resolution.
                        and spec_style not in ["Simple", "Simple List", "List", "NameList", "Enum", "Valid Value", "ValidValue", "Dictionary", "KeyValue", "Enumeration", "Integer", "Boolean", "Simple Int", "Simple Float", "Bool"]
                    )

                # More precise check: if it's already got a GUID or guid_list, don't re-resolve.
                # If it's a value but no GUID/guid_list, and it's a candidate, try to resolve.
                val = attr_data.get("value")
                batch_targets = self.context.get("batch_target_qns", set())
                if val and not attr_data.get("guid") and not attr_data.get("guid_list") and is_ref_candidate:
                    if isinstance(val, list):
                        guid_list = []
                        failed_items = []
                        for item in val:
                            guid = await self.resolve_element_guid(item, tech_type=sanitized_spec_existing)
                            if guid:
                                guid_list.append(guid)
                            else:
                                failed_items.append(item)
                        if guid_list:
                            attr_data["guid_list"] = guid_list
                            attr_data["exists"] = len(guid_list) == len(val)
                            if any(g.startswith("(Planned:") for g in guid_list):
                                attr_data["is_planned"] = True
                        if failed_items:
                            # A failed item may just be a forward reference - a name that
                            # belongs to a command elsewhere in this batch that simply
                            # hasn't run yet. Only hard-fail on names that aren't
                            # recognized as a legitimate batch target at all; defer the
                            # command (retried in a later dispatch_batch round) for the rest.
                            genuinely_failed = [item for item in failed_items if item not in batch_targets]
                            if genuinely_failed:
                                # Mirror the single-value branch below: an unresolvable list item must
                                # not be silently dropped - previously, a wholly- or partially-unresolvable
                                # list (e.g. a "Reference Name List" attribute like Sub-Projects referencing
                                # an element listed later in the same file) produced no error at all, so
                                # the attribute appeared to succeed while quietly doing nothing.
                                attr_data["exists"] = False
                                attr_data["valid"] = False  # Treat as invalid to block execution
                                msg = f"Referenced element(s) {genuinely_failed} for attribute '{attr_name}' not found."
                                if attr_data.get("errors") is None: attr_data["errors"] = []
                                attr_data["errors"].append(msg)
                                logger.error(msg)
                                if "errors" not in self.parsed_output:
                                    self.parsed_output["errors"] = []
                                self.parsed_output["errors"].append(msg)
                            else:
                                attr_data["exists"] = False
                                attr_data["batch_deferred"] = True
                                self.parsed_output["deferred"] = True
                    else:
                        # Try to resolve GUID from cache or Egeria
                        guid = await self.resolve_element_guid(val, tech_type=sanitized_spec_existing)
                        if guid:
                            attr_data["guid"] = guid
                            # If it's a 'Planned' element, it counts as exists for validation
                            attr_data["exists"] = True
                            if guid.startswith("(Planned:"):
                                attr_data["is_planned"] = True
                        elif val in batch_targets:
                            # Forward reference: this name belongs to a command later in
                            # the same batch that hasn't run yet. Defer instead of failing.
                            attr_data["exists"] = False
                            attr_data["batch_deferred"] = True
                            self.parsed_output["deferred"] = True
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
                # We only allow resolution to (Planned: ...) if it was already planned 
                # BEFORE this command added itself to planned_elements.
                if is_already_planned:
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
                            "display_name": self.parsed_output.get("display_name"),
                            "qualified_name": self.parsed_output.get("qualified_name"),
                            "found": False,
                            "errors": self.parsed_output["errors"]
                        }

        # 8. Decouple Analysis from Output
        analysis = await self.validate_only()

        # 9. Action Dispatch
        if directive == "validate":
            errors = self.parsed_output.get("errors") or []
            status = "success" if not errors else "failure"
            guid = self.parsed_output.get("guid")
            # On failure, surface the actual validation error(s) (e.g. "Referenced
            # element 'X' for attribute 'Y' not found.") rather than the generic
            # "Validated ..." success-shaped message — and include "errors" in the
            # result so callers building a structured response (e.g. the MCP
            # server's _build_structured_response) can route this into
            # validation_errors with the real text instead of falling through to
            # a generic execution_errors entry with no useful detail.
            message = (
                f"Validated {self.command.verb} {self.command.object_type}"
                + (f" (GUID: {guid})" if guid else "")
                if status == "success"
                else "; ".join(errors)
            )
            deferred = bool(self.parsed_output.get("deferred"))
            if status == "success" and deferred:
                # A forward reference (names an element defined later in this
                # same batch) can't be confirmed during a single static preview
                # pass - validate mode never actually creates anything, so
                # there's nothing for it to resolve against yet. Not a real
                # problem (that's why status stays "success"), but say so
                # plainly rather than letting this look identical to a fully
                # resolved reference.
                message += " | Note: forward reference(s) not yet creatable in this preview - will resolve during --process"
            return {
                "output": analysis,
                "analysis": analysis,
                "status": status,
                "deferred": deferred,
                "message": message,
                "verb": self.command.verb,
                "object_type": self.canonical_object_type,
                "markdown_object_type": self.markdown_object_type,
                "display_name": self.parsed_output.get("display_name"),
                "qualified_name": self.parsed_output.get("qualified_name"),
                "guid": self.parsed_output.get("guid"),
                "found": self.parsed_output.get("exists", False),
                "warnings": self.parsed_output.get("warnings", []),
                "errors": errors,
            }
        
        # Check for blockers before applying changes
        if self.parsed_output.get("errors"):
            guid = self.parsed_output.get("guid")
            error_list = self.parsed_output['errors']
            error_msg = "; ".join(error_list)
            
            # Incorporate errors into the output markdown for better user feedback
            output = self.command.raw_block
            if error_list:
                output += "\n\n> ❌ **Execution Blocked**\n"
                for err in error_list:
                    output += f"> - {err}\n"
            
            return {
                "output": output,
                "analysis": analysis,
                "status": "failure",
                "message": f"Execution blocked: {error_msg}" + (f" (GUID: {guid})" if guid else ""),
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
                        if not self.context.get("final_round"):
                            # Still might resolve in a later dispatch_batch round -
                            # defer rather than declaring permanent failure.
                            self.parsed_output["deferred"] = True
                            return {
                                "output": self.command.raw_block,
                                "analysis": analysis,
                                "status": "deferred",
                                "deferred": True,
                                "message": f"Deferred: waiting on prerequisite element '{val}'",
                                "verb": self.command.verb,
                                "object_type": self.canonical_object_type,
                                "markdown_object_type": self.markdown_object_type
                            }
                        msg = f"Prerequisite element '{val}' was not successfully created or found."
                        logger.error(msg)
                        return {
                            "output": f"{self.command.raw_block}\n\n> ❌ **Execution Blocked**\n> - {msg}",
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
                            if not self.context.get("final_round"):
                                self.parsed_output["deferred"] = True
                                return {
                                    "output": self.command.raw_block,
                                    "analysis": analysis,
                                    "status": "deferred",
                                    "deferred": True,
                                    "message": f"Deferred: waiting on prerequisite element(s) {failed_names}",
                                    "verb": self.command.verb,
                                    "object_type": self.canonical_object_type,
                                    "markdown_object_type": self.markdown_object_type
                                }
                            msg = f"Prerequisite elements {failed_names} were not successfully created or found."
                            logger.error(msg)
                            return {
                                "output": f"{self.command.raw_block}\n\n> ❌ **Execution Blocked**\n> - {msg}",
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

        # A "standalone" command (its entire purpose IS a relationship - e.g.
        # Link Project Hierarchy, Link Term-Term Relationship - discriminated by
        # having no qualified_name of its own, since derive_qualified_name()
        # returns "" for attach-only commands) has nothing to create on its own.
        # If one of its references is still only a forward-reference-in-waiting,
        # skip apply_changes() entirely and retry the whole command next round,
        # rather than running it now with a still-unresolved reference.
        if self.parsed_output.get("deferred") and not current_qn and not self.context.get("final_round"):
            return {
                "output": self.command.raw_block,
                "analysis": analysis,
                "status": "deferred",
                "deferred": True,
                "message": "Deferred: waiting on forward reference(s) to resolve",
                "verb": self.command.verb,
                "object_type": self.canonical_object_type,
                "markdown_object_type": self.markdown_object_type,
                "display_name": self.parsed_output.get("display_name"),
                "qualified_name": self.parsed_output.get("qualified_name"),
                "found": self.parsed_output.get("exists", False)
            }

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

            if guid and self.command.verb in ["Create", "Define", "Register", "Add", "Update", "Modify", "Upsert"]:
                await self._sync_zone_membership(guid, attributes)
                await self._sync_parent_relationship(guid, attributes)
                await self._sync_governance_classifications(guid, attributes)

        deferred = bool(self.parsed_output.get("deferred")) and not self.context.get("final_round")

        if deferred and output == self.command.raw_block:
            # Nothing was actually applied yet (a standalone-flavor command's own
            # duplicate resolution deferred without going through apply_changes()'s
            # normal output) - say so plainly rather than claiming "Executed".
            message = f"Deferred {self.command.verb} {self.command.object_type}: waiting on forward reference(s) to resolve"
        else:
            message = f"Executed {self.command.verb} {self.command.object_type}" + (f" (GUID: {guid})" if guid else "")
            if deferred:
                message += " | Pending: reference(s) still awaiting later resolution"

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
            "deferred": deferred,
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

        spec = self.get_command_spec()
        is_attach = spec.get("attach", False) if spec else False
        
        if not display_name:
            if is_attach:
                # For link commands, don't guess the QN from other elements' IDs/Names
                return ""
                
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

        if spec and "qn_prefix" in spec:
            qn_prefix = spec.get("qn_prefix")
        else:
            qn_prefix = self.command.object_type
        
        # Strip trailing colon and sanitize spaces if present (Egeria types cannot have spaces)
        if qn_prefix:
            qn_prefix = str(qn_prefix).replace(" ", "")
            if qn_prefix.endswith(':'):
                qn_prefix = qn_prefix[:-1]
        
        # Extract local qualifier (Namespace Path) and Version Identifier if present 
        local_qualifier = attributes.get("Namespace Path", {}).get("value")
        version_identifier = attributes.get("Version Identifier", {}).get("value")

        # Reach into 'collections' subclient which is guaranteed to have the helper
        helper = getattr(self.client, 'collections', self.client)
        if hasattr(helper, "__create_qualified_name__") and qn_prefix:
            return helper.__create_qualified_name__(
                type_name=qn_prefix,
                display_name=display_name,
                local_qualifier=local_qualifier,
                version_identifier=version_identifier or ""
            )
        else:
            # Basic fallback if SDK helper unavailable or if prefix is empty
            if qn_prefix:
                q_name = f"{qn_prefix}::{display_name}"
            else:
                q_name = display_name
                
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
                columns_struct=columns_struct,
                extract_properties_func=populate_columns_from_properties
            )
            return markdown
        except Exception as e:
            logger.error(f"Error generating markdown: {e}")
            return self.command.raw_block

    async def fetch_element(self, guid: str, _max_timeout_retries: int = 2) -> Optional[Dict[str, Any]]:
        """
        Fetch the details of an element by GUID.
        Subclasses should override if MetadataExpert/Explorer is unavailable or if a specific OMAS method is needed.

        On a timeout, retries the *same* ClassificationExplorer call rather than falling
        through to the MetadataExpert fallback (ISSUE-51/52): a timeout means either the
        request was transient (a retry of the same call is exactly as likely to succeed as
        any other call would be) or the server is under sustained load (in which case a
        different endpoint is no more likely to succeed, and MetadataExpert's raw response
        isn't guaranteed to have the same shape as ClassificationExplorer's -- switching
        endpoints on a timeout traded a clean failure for a downstream KeyError crash).
        MetadataExpert stays the fallback for everything that *isn't* a timeout (not found,
        unsupported type, etc.), where switching endpoints is actually likely to help.
        """
        for attempt in range(_max_timeout_retries):
            try:
                # First try ClassificationExplorer (most standard and lightweight)
                logger.debug(f"fetch_element('{guid}') using client {self.client} (attempt {attempt + 1})")
                res = await getattr(self.client, "_async_get_element_by_guid_")(guid)
                logger.debug(f"fetch_element returned {res is not None}")
                if res and isinstance(res, dict):
                    # The structure from classification-explorer comes under "element" usually
                    if "element" in res:
                        return res["element"]
                    return res
                return res
            except PyegeriaTimeoutException as e:
                logger.debug(f"ClassificationExplorer fetch timed out (attempt {attempt + 1}/{_max_timeout_retries}): {e}")
                continue
            except Exception as e:
                logger.debug(f"ClassificationExplorer fetch failed: {e}")
                break

        try:
            # Fallback to MetadataExpert (more detailed properties) -- only reached for a
            # non-timeout failure, or after exhausting timeout retries above.
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
                res = await self.client.__async_get_guid__(qualified_name=name_or_guid, display_name=name_or_guid, property_name="displayName", tech_type=tech_type or None)
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
                    res = await self.client.__async_get_guid__(qualified_name=name_or_guid, display_name=name_or_guid, property_name="displayName")
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

        # ISSUE-59: an explicit '### GUID' attribute on the command should target
        # that specific element directly, regardless of what qualified_name/display
        # name happen to resolve to -- this is the whole point of supplying one (e.g.
        # "rename" a qualified name via Create <X>, which otherwise has no other way
        # to say "this is the same element, just update it"). Try it first, before
        # any name/QN-based lookup, so it isn't silently ignored.
        explicit_guid = self.parsed_output.get("attributes", {}).get("GUID", {}).get("value")
        if explicit_guid and isinstance(explicit_guid, str) and explicit_guid.strip():
            try:
                element = await self.fetch_element(explicit_guid.strip())
                if element:
                    logger.debug(f"fetch_as_is: Element found via explicit GUID '{explicit_guid}'")
                    return element
                else:
                    msg = f"Warning: explicit GUID '{explicit_guid}' was supplied but no element was found for it."
                    logger.warning(msg)
                    self._add_warning(msg)
            except Exception as e:
                msg = f"Warning: explicit GUID '{explicit_guid}' was supplied but could not be fetched: {e}"
                logger.warning(msg)
                self._add_warning(msg)

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
            raw = details.get("raw_value", details.get("value", ""))
            val = format_for_markdown_table(raw)
            
            report.append(f"| {name} | {val} |")
            
        expanded = []
        for name, details in attributes.items():
            raw = details.get("value", "")
            display_raw = details.get("raw_value", raw)
            if isinstance(display_raw, str) and ("\n" in display_raw or any(display_raw.strip().startswith(p) for p in ("- ", "* ", "1.", "#", ">", "```"))):
                expanded.append(f"##### {name}\n\n{display_raw}\n")
            elif isinstance(raw, dict) and details.get("style") in ("Dictionary", "KeyValue"):
                table_lines = [
                    f"##### {name}\n",
                    "| Parameter Name | Parameter Value |",
                    "| :--- | :--- |"
                ]
                for k, v in raw.items():
                    table_lines.append(f"| {k} | {v} |")
                expanded.append("\n".join(table_lines) + "\n")

        if expanded:
            report.append("\n#### Rendered Attribute Details\n")
            report.extend(expanded)

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
            raw = details.get("raw_value", details.get("value", ""))
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
            display_raw = details.get("raw_value", raw)
            if isinstance(display_raw, str) and ("\n" in display_raw or any(display_raw.strip().startswith(p) for p in ("- ", "* ", "1.", "#", ">", "```"))):
                expanded.append(f"##### {name}\n\n{display_raw}\n")
            elif isinstance(raw, dict) and details.get("style") in ("Dictionary", "KeyValue"):
                table_lines = [
                    f"##### {name}\n",
                    "| Parameter Name | Parameter Value |",
                    "| :--- | :--- |"
                ]
                for k, v in raw.items():
                    table_lines.append(f"| {k} | {v} |")
                expanded.append("\n".join(table_lines) + "\n")

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
                           as_is_guids: Union[set, Callable[[], Awaitable[set]]],
                           to_be_guids: set,
                           add_coro,
                           remove_coro,
                           replace_all: bool = True) -> Dict[str, List[str]]:
        """
        Generic async relationship synchronization logic.
        Handles set comparison (As-Is vs To-Be) and executes provided coroutines.

        If replace_all is False, it only performs additions.

        `as_is_guids` may be a plain set (already fetched -- unchanged
        behavior) or a zero-arg async callable that fetches it lazily. The
        lazy form lets a caller skip an expensive "what does this element
        currently have" relationship query entirely in the one case where
        its result can never change the outcome: replace_all=False
        (add-only) with an empty to_be_guids -- there is nothing to add
        regardless of current state, so the fetch is skipped below before
        the callable is ever invoked. Separately, a caller whose element is
        known to be brand new (verb == "Create") should pass an empty set
        directly rather than a fetcher at all -- a just-created element
        cannot have any existing relationships, so there's nothing to fetch.
        """
        if not replace_all and not to_be_guids:
            return {"added": [], "removed": [], "errors": []}

        if callable(as_is_guids):
            as_is_guids = await as_is_guids()

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
