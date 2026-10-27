"""
Security Officer Processors for Dr.Egeria v2.

Handles statements of applicability (Egeria 6.3): `Create/Update Statement of
Applicability` and `Link/Unlink Control Applicability`, built on the
SecurityOfficer OMVS client; and security testing results: `Create/Update
Survey Report` (Asset Maker) and the security finding and posture summary
commands (Data Discovery) -- see the section further down.

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


def _report_sync(processor: AsyncBaseCommandProcessor, label: str, res: Dict[str, Any]) -> None:
    """Record a sync_members result as related results on the command's output."""
    for g in res.get("added", []):
        processor.add_related_result(label, g)
    for g in res.get("removed", []):
        processor.add_related_result(label, g, message="removed")
    if res.get("errors"):
        processor.add_related_result(label, status="failure", message="; ".join(res["errors"]))


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
            _report_sync(self, "Certification Standard", res)

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
            _report_sync(self, "Scoped By", res)


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


#
# Security testing results (Egeria 6.3, model 0665). Each test run is a SurveyReport asset;
# each finding is a SecurityFindingAnnotation (or its Vulnerability / PenetrationTestFinding
# subtypes) and the run's summary a SecurityPostureAnnotation, linked to the report with
# ReportedAnnotation:
#
#   SurveyReport --ReportSubject--> asset that was tested
#   SurveyReport --ReportedAnnotation--> finding / posture summary
#   affected element --AssociatedAnnotation--> finding
#   finding from the previous run --AnnotationExtension--> the same finding in this run
#   finding --ReferenceValueAssignment--> vulnerability type (reference data value)
#

# Dr.Egeria attribute -> Egeria property, for the annotation types' own properties.
_ANNOTATION_FIELDS = {
    "Summary": "summary",
    "Severity": "severity",
    "CVSS Score": "cvssScore",
    "CVSS Vector": "cvssVector",
    "Vulnerability Identifiers": "vulnerabilityIdentifiers",
    "Weakness Identifiers": "weaknessIdentifiers",
    "Affected Location": "affectedLocation",
    "Evidence": "evidence",
    "Remediation": "remediation",
    "Exploit Available": "exploitAvailable",
    "Package URL": "packageURL",
    "Installed Version": "installedVersion",
    "Fixed Version": "fixedVersion",
    "Patch Available": "patchAvailable",
    "Attack Vector": "attackVector",
    "Attack Techniques": "attackTechniques",
    "Privileges Gained": "privilegesGained",
    "Compromised Resources": "compromisedResources",
    "Reproduction Steps": "reproductionSteps",
    "Finding Counts By Severity": "findingCountsBySeverity",
    "Resources In Scope Count": "resourcesInScopeCount",
    "Resources Tested Count": "resourcesTestedCount",
    "New Finding Count": "newFindingCount",
    "Resolved Finding Count": "resolvedFindingCount",
}


_FLOAT_FIELDS = {"cvssScore"}
_INT_FIELDS = {"resourcesInScopeCount", "resourcesTestedCount", "newFindingCount", "resolvedFindingCount"}


def _annotation_properties(om_type: str, qualified_name: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
    """The properties body for a security finding or posture annotation of type `om_type`."""
    props = set_element_prop_body(om_type, qualified_name, attributes)
    for attr_name, key in _ANNOTATION_FIELDS.items():
        value = attributes.get(attr_name, {}).get("value")
        if value is None or value == "" or value == []:
            continue
        try:
            if key in _FLOAT_FIELDS:
                value = float(value)
            elif key in _INT_FIELDS:
                value = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"'{attr_name}' needs a number; got {value!r}") from None
        if key == "findingCountsBySeverity" and isinstance(value, dict):
            try:
                value = {str(k): int(v) for k, v in value.items()}
            except ValueError:
                raise ValueError(f"'{attr_name}' needs a whole-number count per severity, one "
                                 f"'severity: count' pair per line; got {value}") from None
        props[key] = value
    return props


class SurveyReportProcessor(AsyncBaseCommandProcessor):
    """Processor for Create Survey Report (and its Update transition).

    A SurveyReport is an Asset, so it is created through Asset Maker; Report Subjects
    are synced as ReportSubject relationships.
    """

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output.get("qualified_name") or self.derive_qualified_name(attributes)
        display_name = attributes.get("Display Name", {}).get("value") or qualified_name
        merge_update = attributes.get("Merge Update", {}).get("value", True)

        props = set_element_prop_body("SurveyReport", qualified_name, attributes)
        props["purpose"] = attributes.get("Purpose", {}).get("value")
        props["startTime"] = attributes.get("Start Time", {}).get("value")
        props["completionTime"] = attributes.get("Completion Time", {}).get("value")

        if self.as_is_element:
            guid = self.as_is_element["elementHeader"]["guid"]
            self.last_body = body = {
                "class": "UpdateElementRequestBody",
                "properties": self.filter_update_properties(props, merge_update),
                "mergeUpdate": merge_update,
            }
            await self.client._async_update_asset(guid, body_slimmer(body))
            verb_word = "Updated"
        else:
            self.last_body = body = set_create_body("SurveyReport", attributes)
            body["properties"] = props
            raw_guid = await self.client._async_create_asset(["SurveyReportProperties"], body_slimmer(body))
            guid = self.extract_guid_or_raise(raw_guid, "Create Survey Report")
            verb_word = "Created"

        self.parsed_output["guid"] = guid
        if attributes.get("Report Subjects", {}).get("value"):
            res = await self.sync_members(
                _related_guids(self.as_is_element, "ReportSubject"),
                set(attributes["Report Subjects"].get("guid_list") or []),
                lambda g: self.client._async_link_report_subject(g, guid, _plain_rel_body(attributes)),
                lambda g: self.client._async_unlink_report_subject(
                    g, guid, body_slimmer(set_delete_rel_request_body("ReportSubject", attributes))),
                replace_all=not merge_update,
            )
            _report_sync(self, "Report Subjects", res)

        update_element_dictionary(qualified_name, {"guid": guid, "display_name": display_name})
        logger.success(f"{verb_word} Survey Report '{display_name}' with GUID {guid}")
        return await self.render_result_markdown(guid)


class SecurityFindingProcessor(AsyncBaseCommandProcessor):
    """Processor for Create Security Finding / Vulnerability Finding / Penetration Test Finding
    and Create Security Posture Summary (and their Update transitions).

    A new annotation is created under its Survey Report (ReportedAnnotation, anchored to the
    report). Affected Elements, Previous Finding and Vulnerability Type are synced as
    AssociatedAnnotation, AnnotationExtension and ReferenceValueAssignment relationships.
    """

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output.get("qualified_name") or self.derive_qualified_name(attributes)
        display_name = attributes.get("Display Name", {}).get("value") or qualified_name
        merge_update = attributes.get("Merge Update", {}).get("value", True)
        om_type = self.get_command_spec().get("OM_TYPE")

        props = _annotation_properties(om_type, qualified_name, attributes)

        if self.as_is_element:
            guid = self.as_is_element["elementHeader"]["guid"]
            self.last_body = body = {
                "class": "UpdateElementRequestBody",
                "properties": self.filter_update_properties(props, merge_update),
                "mergeUpdate": merge_update,
            }
            await self.client._async_update_annotation(guid, body_slimmer(body))
            verb_word = "Updated"
        else:
            report_guid = attributes.get("Survey Report", {}).get("guid")
            if not report_guid:
                raise ValueError("Cannot create the finding: 'Survey Report' did not resolve to a survey report.")
            body = set_create_body(om_type, attributes)
            body.update({
                "anchorGUID": report_guid,
                "isOwnAnchor": False,
                "parentGUID": report_guid,
                "parentRelationshipTypeName": "ReportedAnnotation",
                "parentAtEnd1": True,
                "properties": props,
            })
            self.last_body = body = body_slimmer(body)
            raw_guid = await self.client._async_create_annotation(body)
            guid = self.extract_guid_or_raise(raw_guid, f"Create {self.command.object_type}")
            verb_word = "Created"

        self.parsed_output["guid"] = guid
        await self._sync_relationships(guid, attributes, replace_all=not merge_update)
        update_element_dictionary(qualified_name, {"guid": guid, "display_name": display_name})
        logger.success(f"{verb_word} {self.command.object_type} '{display_name}' with GUID {guid}")
        return await self.render_result_markdown(guid)

    async def _sync_relationships(self, guid: str, attributes: Dict[str, Any], replace_all: bool) -> None:
        """Bring the finding's relationships in line with the command.

        As for statements of applicability, an attribute left out of the command
        leaves its relationships alone, and only a replacing update removes links.
        """
        as_is = self.as_is_element
        delete_body = lambda rel: body_slimmer(set_delete_rel_request_body(rel, attributes))

        if attributes.get("Affected Elements", {}).get("value"):
            res = await self.sync_members(
                _related_guids(as_is, "AssociatedAnnotation"),
                set(attributes["Affected Elements"].get("guid_list") or []),
                lambda g: self.client._async_link_annotation_to_described_element(
                    guid, g, _plain_rel_body(attributes)),
                lambda g: self.client._async_detach_annotation_from_described_element(
                    guid, g, delete_body("AssociatedAnnotation")),
                replace_all=replace_all,
            )
            _report_sync(self, "Affected Elements", res)

        if attributes.get("Previous Finding", {}).get("value"):
            previous = attributes["Previous Finding"].get("guid")
            res = await self.sync_members(
                _related_guids(as_is, "AnnotationExtension") - {guid},
                {previous} if previous else set(),
                lambda g: self.client._async_link_annotation_to_its_predecessor(
                    guid, g, _plain_rel_body(attributes)),
                lambda g: self.client._async_detach_annotation_from_its_predecessor(
                    guid, g, delete_body("AnnotationExtension")),
                replace_all=replace_all,
            )
            _report_sync(self, "Previous Finding", res)

        if attributes.get("Vulnerability Type", {}).get("value"):
            vuln_type = attributes["Vulnerability Type"].get("guid")
            res = await self.sync_members(
                _related_guids(as_is, "ReferenceValueAssignment"),
                {vuln_type} if vuln_type else set(),
                lambda g: self.client._async_link_reference_value_assignment(guid, g, _plain_rel_body(attributes)),
                lambda g: self.client._async_detach_reference_value_assignment(
                    guid, g, delete_body("ReferenceValueAssignment")),
                replace_all=replace_all,
            )
            _report_sync(self, "Vulnerability Type", res)
