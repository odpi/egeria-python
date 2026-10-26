"""
Security Officer Processors for Dr.Egeria v2.

Handles statements of applicability (Egeria 6.3): `Create/Update Statement of
Applicability` and `Link/Unlink Control Applicability`, built on the
SecurityOfficer OMVS client.

A statement records which controls from a standard (for example the Annex A
controls of ISO/IEC 27001) apply to the organization, why, and how far each is
implemented:

    CertificationType --GovernedBy--> StatementOfApplicability
    StatementOfApplicability --ScopedBy--> Referenceable (organization, site, system...)
    StatementOfApplicability --ControlApplicability--> GovernanceDefinition (a control)

ControlApplicability is not multi-link, and its attach operation updates the
properties of an existing relationship, so re-running a Link command for the
same statement and control is how a control's status is updated.
"""
from typing import Any, Dict, Optional

from loguru import logger

from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.common_md_utils import (
    set_create_body,
    set_delete_rel_request_body,
    set_element_prop_body,
    set_rel_request_body,
    update_element_dictionary,
)
from pyegeria.core._exceptions import PyegeriaException
from pyegeria.core.utils import body_slimmer


def _related_guids(element: Optional[Dict[str, Any]], relationship_type: str,
                   related_type: Optional[str] = None) -> set:
    """GUIDs of the elements related to `element` through `relationship_type`.

    Scans every list in the element for related-element entries rather than
    relying on one key name, since Egeria groups relationships under
    type-specific keys (e.g. governedBy, scopedBy) or otherRelatedElements.
    `related_type` restricts the result to related elements of that type.
    """
    guids = set()
    if not isinstance(element, dict):
        return guids
    for value in element.values():
        if not isinstance(value, list):
            continue
        for entry in value:
            if not isinstance(entry, dict):
                continue
            rel_header = entry.get("relationshipHeader") or {}
            if (rel_header.get("type") or {}).get("typeName") != relationship_type:
                continue
            related_header = (entry.get("relatedElement") or {}).get("elementHeader") or {}
            if related_type and (related_header.get("type") or {}).get("typeName") != related_type:
                continue
            if related_header.get("guid"):
                guids.add(related_header["guid"])
    return guids


def _plain_rel_body(attributes: Dict[str, Any]) -> Dict[str, Any]:
    """A NewRelationshipRequestBody with no relationship properties.

    set_rel_request_body leaves "properties" as "" for the caller to fill;
    GovernedBy and ScopedBy need none here, so drop it rather than send a string.
    """
    body = set_rel_request_body("", attributes)
    body.pop("properties", None)
    return body_slimmer(body)


class StatementOfApplicabilityProcessor(AsyncBaseCommandProcessor):
    """Processor for Create Statement of Applicability (and its Update transition)."""

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            element = await self.client._async_get_statement_of_applicability_by_guid(guid)
        except PyegeriaException:
            return None
        return element if isinstance(element, dict) else None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output.get("qualified_name") or self.derive_qualified_name(attributes)
        display_name = attributes.get("Display Name", {}).get("value") or qualified_name
        merge_update = attributes.get("Merge Update", {}).get("value", True)

        props = set_element_prop_body("StatementOfApplicability", qualified_name, attributes)
        props["scope"] = attributes.get("Scope", {}).get("value")
        props["reviewDate"] = attributes.get("Review Date", {}).get("value")

        if verb == "Update" or self.as_is_element:
            guid = self.parsed_output.get("guid") or (
                self.as_is_element["elementHeader"]["guid"] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block
            self.last_body = body = {
                "class": "UpdateElementRequestBody",
                "properties": self.filter_update_properties(props, merge_update),
                "mergeUpdate": merge_update,
            }
            await self.client._async_update_statement_of_applicability(guid, body_slimmer(body))
            verb_word = "Updated"
        else:
            self.last_body = body = set_create_body("StatementOfApplicability", attributes)
            body["properties"] = props
            raw_guid = await self.client._async_create_statement_of_applicability(body_slimmer(body))
            guid = self.extract_guid_or_raise(raw_guid, "Create Statement of Applicability")
            verb_word = "Created"

        self.parsed_output["guid"] = guid
        await self._sync_relationships(guid, attributes, replace_all=not merge_update)
        update_element_dictionary(qualified_name, {"guid": guid, "display_name": display_name})
        logger.success(f"{verb_word} Statement of Applicability '{display_name}' with GUID {guid}")
        return await self.render_result_markdown(guid)

    async def _sync_relationships(self, guid: str, attributes: Dict[str, Any], replace_all: bool) -> None:
        """Bring the GovernedBy (certification standard) and ScopedBy links in line with the command.

        An attribute left out of the command leaves its relationships alone. A
        merge update only adds; a replacing update (Merge Update false) also
        removes links the command no longer lists. Only GovernedBy links to a
        CertificationType are considered, so other governance definitions
        governing the statement are never removed here.
        """
        as_is = self.as_is_element

        if attributes.get("Certification Standard", {}).get("value"):
            cert_guid = attributes["Certification Standard"].get("guid")
            to_be = {cert_guid} if cert_guid else set()
            res = await self.sync_members(
                _related_guids(as_is, "GovernedBy", "CertificationType"),
                to_be,
                lambda g: self.client._async_attach_governed_by_definition(
                    guid, g, _plain_rel_body(attributes)),
                lambda g: self.client._async_detach_governed_by_definition(
                    guid, g, body_slimmer(set_delete_rel_request_body("GovernedBy", attributes))),
                replace_all=replace_all,
            )
            self._report_sync("Certification Standard", res)

        if attributes.get("Scoped By", {}).get("value"):
            to_be = set(attributes["Scoped By"].get("guid_list") or [])
            res = await self.sync_members(
                _related_guids(as_is, "ScopedBy"),
                to_be,
                lambda g: self.client._async_add_scope_to_element(
                    scoped_by_guid=g, element_guid=guid,
                    body=_plain_rel_body(attributes)),
                lambda g: self.client._async_clear_scope_from_element(
                    scoped_by_guid=g, element_guid=guid,
                    body=body_slimmer(set_delete_rel_request_body("ScopedBy", attributes))),
                replace_all=replace_all,
            )
            self._report_sync("Scoped By", res)

    def _report_sync(self, label: str, res: Dict[str, Any]) -> None:
        for g in res.get("added", []):
            self.add_related_result(label, g)
        for g in res.get("removed", []):
            self.add_related_result(label, g, message="removed")
        if res.get("errors"):
            self.add_related_result(label, status="failure", message="; ".join(res["errors"]))


class ControlApplicabilityLinkProcessor(AsyncBaseCommandProcessor):
    """Processor for Link / Unlink Control Applicability.

    The relationship is identified by its two ends, so both link and unlink take
    the statement and control GUIDs. Linking an already-linked control updates
    the existing relationship's properties.
    """

    def supports_target_element_lookup(self) -> bool:
        # Relationship-only command: there is no target element to look up by
        # qualified name, and without this the upsert rewriter would treat
        # every Link as a Create of an unnamed element.
        return False

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = getattr(self, "canonical_object_type", self.command.object_type)
        attributes = self.parsed_output["attributes"]

        soa_guid = attributes.get("Statement of Applicability", {}).get("guid")
        control_guid = attributes.get("Control", {}).get("guid")
        if not (soa_guid and control_guid):
            missing = []
            if not soa_guid:
                missing.append("'Statement of Applicability'")
            if not control_guid:
                missing.append("'Control'")
            raise ValueError(f"Cannot {verb.lower()} control applicability: resolution failed for {', '.join(missing)}")

        if verb in ["Link", "Attach", "Add"]:
            new_props = {
                "isApplicable": attributes.get("Is Applicable", {}).get("value"),
                "justification": attributes.get("Justification", {}).get("value"),
                "inclusionReasons": attributes.get("Inclusion Reasons", {}).get("value"),
                "implementationStatus": attributes.get("Implementation Status", {}).get("value"),
                "implementationDescription": attributes.get("Implementation Description", {}).get("value"),
                "reviewDate": attributes.get("Review Date", {}).get("value"),
                "label": attributes.get("Label", {}).get("value"),
                "description": attributes.get("Description", {}).get("value"),
                "effectiveFrom": attributes.get("Effective From", {}).get("value"),
                "effectiveTo": attributes.get("Effective To", {}).get("value"),
            }
            # Attaching an already-linked control replaces the relationship's
            # properties wholesale (confirmed live), so by default start from the
            # existing ones -- re-linking with just a new status keeps the
            # justification, reasons and so on. Merge Update false replaces them.
            properties = {}
            if attributes.get("Merge Update", {}).get("value", True):
                properties = await self._existing_applicability(soa_guid, control_guid)
            properties.update({k: v for k, v in new_props.items() if v not in (None, "", [])})
            properties["class"] = "ControlApplicabilityProperties"

            body = set_rel_request_body("ControlApplicability", attributes)
            body["properties"] = properties
            self.last_body = body = body_slimmer(body)
            await self.client._async_link_control_applicability(soa_guid, control_guid, body)
            logger.success(f"Linked control {control_guid} to statement of applicability {soa_guid}")
            return (f"\n\n## {verb} {object_type}\n\n"
                    f"Linked control {control_guid} to statement of applicability {soa_guid}")

        if verb in ["Detach", "Unlink", "Remove"]:
            self.last_body = body = body_slimmer(set_delete_rel_request_body("ControlApplicability", attributes))
            await self.client._async_detach_control_applicability(soa_guid, control_guid, body)
            logger.success(f"Removed control {control_guid} from statement of applicability {soa_guid}")
            return (f"\n\n## {verb} {object_type}\n\n"
                    f"Removed control {control_guid} from statement of applicability {soa_guid}")

        return self.command.raw_block

    async def _existing_applicability(self, soa_guid: str, control_guid: str) -> Dict[str, Any]:
        """The current ControlApplicability properties for this control, or {} if it is not linked yet."""
        soa = await self.client._async_get_statement_of_applicability_by_guid(soa_guid)
        if not isinstance(soa, dict):
            return {}
        for rel in soa.get("otherRelatedElements") or []:
            rel_type = ((rel.get("relationshipHeader") or {}).get("type") or {}).get("typeName")
            related_guid = ((rel.get("relatedElement") or {}).get("elementHeader") or {}).get("guid")
            if rel_type == "ControlApplicability" and related_guid == control_guid:
                return {k: v for k, v in (rel.get("relationshipProperties") or {}).items()
                        if k not in ("class", "typeName")}
        return {}
