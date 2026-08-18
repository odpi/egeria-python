"""
Curation Processors for Dr.Egeria v2.

Handles the "Curation" command family: post-hoc classification and
relationship curation for existing Referenceable elements.

CurationClassifyProcessor -- Classify/Reclassify/Update/Declassify commands
for: Impact, Confidence, Confidentiality, Criticality, Retention, Ownership,
Digital Resource Origin, Zone Membership, Data Scope, Governance
Expectations, Governance Measurements, Security Tags, Known Duplicate,
Consolidated Duplicate, Class Word, Modifier, Prime Word.

CurationLinkProcessor -- Link/Unlink/Attach/Detach relationship commands
for: Semantic Assignment, Semantic Definition, Scoped By, Peer Duplicate,
Consolidated Duplicate Link, Resource List, and the create-side of Search
Keyword.

ClassWord/Modifier/PrimeWord (0438 naming standards classifications) were
added 2026-08-09 once Egeria PR #9166 shipped the backing REST endpoints
(glossary-manager's is-class-word/is-modifier/is-prime-word) -- see the new
set/clear method pairs in pyegeria/omvs/glossary_manager.py. They route
through GlossaryManager, not ClassificationExplorer (the module docstring
here previously said "no backing pyegeria method exists" for these three --
no longer true for these; still true for Policy Management Point, which
has no matching Egeria PR yet and stays parse-only.

NOT implemented (no backing pyegeria method exists): Classify/Declassify
Policy Management Point. This command parses but is not registered with
the dispatcher, so it stays parse-only, same as Create Note.

PARTIALLY implemented: Update/Detach Search Keyword need the previously
-created SearchKeyword entity's own GUID, which the current compact-JSON
attribute set for this command has no way to reference (only "Target
Element", "Keyword", "Keyword Description" are captured -- there's no
"Search Keyword GUID" attribute). Only "Attach Search Keyword" (create +
attach in one call) is wired here; Update/Detach are a known follow-up.
"""
from dataclasses import dataclass, field as dc_field
from typing import Any, Dict, Optional

from loguru import logger

from pyegeria import PyegeriaException
from md_processing.v2.processors import AsyncBaseCommandProcessor


def _v(attributes: dict, name: str, default=None):
    return attributes.get(name, {}).get("value", default)


def _guid(attributes: dict, name: str):
    return attributes.get(name, {}).get("guid")


def _audit_fields(attributes: dict) -> dict:
    return {
        "externalSourceGUID": attributes.get("External Source GUID", {}).get("guid"),
        "externalSourceName": _v(attributes, "External Source Name"),
        "effectiveTime": _v(attributes, "Effective Time"),
        "forLineage": _v(attributes, "For Lineage", False),
        "forDuplicateProcessing": _v(attributes, "For Duplicate Processing", False),
    }


# ============================================================== classifications

@dataclass
class ClassificationSpec:
    set_method: str
    clear_method: str
    props_class: str
    update_method: Optional[str] = None
    level_field: Optional[str] = None  # e.g. "severityLevel" -- reads "Level Identifier"
    fields: Dict[str, str] = dc_field(default_factory=dict)  # attribute name -> property name


# Shared governance-classification fields (Impact/Confidence/Confidentiality/Criticality/Retention)
# "Governance Status" (not "Status" -- that name collides with the universal Referenceable/
# element-header "Status" attribute shared by nearly every other family; see PYEGERIA_ISSUES.md).
_GOVERNANCE_SHARED_FIELDS = {"Governance Status": "statusIdentifier", "Steward": "steward", "Source": "source", "Description": "notes"}

CLASSIFICATION_METHODS: Dict[str, ClassificationSpec] = {
    # Keys are real Egeria classification type names (confirmed live via
    # get_all_classification_defs -- e.g. "Impact", not "ImpactClassification").
    "Impact": ClassificationSpec(
        "_async_set_impact_classification", "_async_clear_impact_classification", "ImpactProperties",
        level_field="severityLevel", fields=dict(_GOVERNANCE_SHARED_FIELDS)),
    "Confidence": ClassificationSpec(
        "_async_set_confidence_classification", "_async_clear_confidence_classification", "ConfidenceProperties",
        level_field="confidenceLevel", fields=dict(_GOVERNANCE_SHARED_FIELDS)),
    "Confidentiality": ClassificationSpec(
        "_async_set_confidentiality_classification", "_async_clear_confidentiality_classification", "ConfidentialityProperties",
        level_field="confidentialityLevel", fields=dict(_GOVERNANCE_SHARED_FIELDS)),
    "Criticality": ClassificationSpec(
        "_async_set_criticality_classification", "_async_clear_criticality_classification", "CriticalityProperties",
        level_field="criticalityLevel", fields=dict(_GOVERNANCE_SHARED_FIELDS)),
    "Retention": ClassificationSpec(
        "_async_set_retention_classification", "_async_clear_retention_classification", "RetentionClassificationProperties",
        level_field="retentionBasis",  # "Retention Basis" attribute holds an enum, reuse level_field slot
        fields={**_GOVERNANCE_SHARED_FIELDS, "Archive After": "archiveAfter", "Delete After": "deleteAfter"}),
    "Ownership": ClassificationSpec(
        "_async_add_ownership_to_element", "_async_clear_ownership_from_element", "OwnershipProperties",
        fields={"Owner": "owner", "Owner Type Name": "ownerTypeName", "Owner Property Name": "ownerPropertyName"}),
    "DigitalResourceOrigin": ClassificationSpec(
        "_async_add_digital_resource_origin", "_async_clear_digital_resource_origin_from_element", "DigitalResourceOriginProperties",
        # NOTE: pyegeria's .http example for this endpoint shows the same owner/ownerTypeName/ownerPropertyName
        # fields as Ownership -- unverified against a live server, may be a copy-paste artifact in the docs.
        # Mapped here on a best-effort basis; verify against a live server before relying on this.
        fields={"Organization": "owner", "Business Capability": "ownerTypeName"}),
    "ZoneMembership": ClassificationSpec(
        "_async_add_zone_membership", "_async_clear_zone_membership", "ZoneMembershipProperties",
        # NOTE: pyegeria's .http example shows owner/ownerTypeName/ownerPropertyName fields here too, which
        # doesn't match Egeria's documented 0424 ZoneMembership type (a `zoneMembership` string list). Using
        # the documented type's real field name instead of the (likely erroneous) .http example --
        # verify against a live server before relying on this.
        fields={"Zone Membership": "zoneMembership"}),
    "SecurityTags": ClassificationSpec(
        "_async_set_security_tags_classification", "_async_clear_security_tags_classification", "SecurityTagsProperties",
        fields={"Security Labels": "securityLabels", "Security Properties": "securityProperties"}),
    "AccountingCodes": ClassificationSpec(
        "_async_set_accounting_codes_classification", "_async_clear_accounting_codes_classification", "AccountingCodesProperties",
        fields={"Accounting Code": "accountingCode", "Description": "description",
                "Accounting Code List": "accountingCodeList", "Accounting Code Map": "accountingCodeMap"}),
    "DataScope": ClassificationSpec(
        "_async_add_data_scope", "_async_clear_data_scope", "DataScopeProperties",
        update_method="_async_update_data_scope",
        fields={"Description": "additionalProperties"}),
    "GovernanceExpectations": ClassificationSpec(
        "_async_set_governance_expectation", "_async_clear_governance_expectation", "GovernanceExpectationsProperties",
        update_method="_async_update_governance_expectation",
        fields={"Governance Expectations Counts": "counts"}),
    "GovernanceMeasurements": ClassificationSpec(
        "_async_add_governance_measurements", "_async_clear_governance_measurements", "GovernanceMeasurementsProperties",
        update_method="_async_update_governance_measurements",
        fields={"Governance Measurements": "measurements"}),
    "KnownDuplicate": ClassificationSpec(
        "_async_set_known_duplicate_classification", "_async_clear_known_duplicate_classification", "KnownDuplicateProperties"),
    "ConsolidatedDuplicate": ClassificationSpec(
        "_async_set_consolidated_duplicate_classification", "_async_clear_consolidated_duplicate_classification", "ConsolidatedDuplicateProperties",
        fields={"Duplicate Notes": "notes"}),
    # 0438 naming standards classifications (Egeria PR #9166) -- marker classifications
    # with no custom properties, routed through GlossaryManager (not
    # ClassificationExplorer/classification_manager, unlike every other entry above --
    # see CURATION_CLASSIFICATION_CLIENTS below and apply_changes()'s client selection).
    "ClassWord": ClassificationSpec(
        "_async_set_is_class_word", "_async_clear_is_class_word", "ClassWordProperties"),
    "Modifier": ClassificationSpec(
        "_async_set_is_modifier", "_async_clear_is_modifier", "ModifierProperties"),
    "PrimeWord": ClassificationSpec(
        "_async_set_is_prime_word", "_async_clear_is_prime_word", "PrimeWordProperties"),
}

# OM_TYPEs in CLASSIFICATION_METHODS whose set/clear methods live on a client other than
# self.client.classification_manager (the default every other entry above uses).
CURATION_CLASSIFICATION_CLIENTS = {
    "ClassWord": "glossary_manager",
    "Modifier": "glossary_manager",
    "PrimeWord": "glossary_manager",
}


def _build_classification_properties(spec: ClassificationSpec, attributes: dict) -> dict:
    props: dict = {"class": spec.props_class}
    if spec.level_field:
        level = _v(attributes, "Level Identifier") if spec.level_field != "retentionBasis" else _v(attributes, "Retention Basis")
        if level is not None:
            props[spec.level_field] = level
    for attr_name, prop_name in spec.fields.items():
        # Reference-Name-styled fields (e.g. "Owner") resolve to a GUID during the
        # standard pipeline step; prefer that over the raw display value when present.
        val = attributes.get(attr_name, {}).get("guid")
        if val is None:
            val = _v(attributes, attr_name)
        if val is not None:
            props[prop_name] = val
    return props


class CurationClassifyProcessor(AsyncBaseCommandProcessor):
    """Standalone Classify/Reclassify/Update/Declassify commands (Curation family)."""

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.canonical_object_type or self.command.object_type
        attributes = self.parsed_output.get("attributes", {})
        om_type = self.get_command_spec().get("OM_TYPE")

        class_spec = CLASSIFICATION_METHODS.get(om_type)
        if not class_spec:
            raise PyegeriaException(f"No classification mapping registered for OM_TYPE '{om_type}' ({object_type})")

        element_guid = _guid(attributes, "Target Element")
        if not element_guid:
            raise PyegeriaException(f"Could not resolve 'Target Element' for {verb} {object_type}")

        client = getattr(self.client, CURATION_CLASSIFICATION_CLIENTS.get(om_type, "classification_manager"))

        if verb == "Declassify":
            body = {"class": "DeleteClassificationRequestBody", **_audit_fields(attributes)}
            await getattr(client, class_spec.clear_method)(element_guid, body)
            logger.success(f"Declassified {object_type} on {element_guid}")
            return f"\n\n## {verb} {object_type}\n\nRemoved {om_type} classification from {element_guid}."

        properties = _build_classification_properties(class_spec, attributes)
        use_update = verb == "Update" and class_spec.update_method
        body = {
            "class": "UpdateClassificationRequestBody" if use_update else "NewClassificationRequestBody",
            "properties": properties,
            **_audit_fields(attributes),
        }
        if use_update:
            body["mergeUpdate"] = True
            method = getattr(client, class_spec.update_method)
        else:
            method = getattr(client, class_spec.set_method)
        await method(element_guid, body)
        logger.success(f"{verb}ed {object_type} on {element_guid}")
        return f"\n\n## {verb} {object_type}\n\nApplied {om_type} classification to {element_guid}."


# ============================================================== relationships

class CurationLinkProcessor(AsyncBaseCommandProcessor):
    """Link/Unlink/Attach/Detach relationship commands (Curation family)."""

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.canonical_object_type or self.command.object_type
        attributes = self.parsed_output.get("attributes", {})
        om_type = self.get_command_spec().get("OM_TYPE")
        target_guid = _guid(attributes, "Target Element")
        is_link = verb in ("Link", "Attach", "Add")

        if om_type == "ScopedBy":
            other_guid = _guid(attributes, "Scope Reference")
            client = self.client.classification_manager
            if is_link:
                body = {"class": "NewRelationshipRequestBody", "properties": {"class": "ScopedByProperties"}, **_audit_fields(attributes)}
                await client._async_add_scope_to_element(scoped_by_guid=other_guid, element_guid=target_guid, body=body)
            else:
                body = {"class": "DeleteRelationshipRequestBody", **_audit_fields(attributes)}
                await client._async_clear_scope_from_element(scoped_by_guid=other_guid, element_guid=target_guid, body=body)

        elif om_type == "SemanticAssignment":
            other_guid = _guid(attributes, "Glossary Term")
            client = self.client.classification_manager
            if is_link:
                props = {
                    "class": "SemanticAssignmentProperties",
                    "expression": _v(attributes, "Semantic Expression"),
                    "confidence": _v(attributes, "Confidence Level"),
                    "status": _v(attributes, "Governance Status"),
                    "steward": _v(attributes, "Steward"),
                    "source": _v(attributes, "Source"),
                }
                body = {"class": "NewRelationshipRequestBody", "properties": props, **_audit_fields(attributes)}
                await client._async_setup_semantic_assignment(glossary_term_guid=other_guid, element_guid=target_guid, body=body)
            else:
                body = {"class": "DeleteRelationshipRequestBody", **_audit_fields(attributes)}
                await client._async_clear_semantic_assignment_classification(glossary_term_guid=other_guid, element_guid=target_guid, body=body)

        elif om_type == "SemanticDefinition":
            other_guid = _guid(attributes, "Semantic Definition")
            client = self.client.data_designer
            if is_link:
                body = {"class": "NewRelationshipRequestBody", **_audit_fields(attributes)}
                await client._async_link_semantic_definition(data_definition_guid=target_guid, glossary_term_guid=other_guid, body=body)
            else:
                body = {"class": "DeleteRelationshipRequestBody", **_audit_fields(attributes)}
                await client._async_detach_semantic_definition(data_definition_guid=target_guid, glossary_term_guid=other_guid, body=body)

        elif om_type == "PeerDuplicateLink":
            other_guid = _guid(attributes, "Peer Duplicate")
            client = self.client.classification_manager
            props = {"class": "PeerDuplicateLinkProperties", "notes": _v(attributes, "Duplicate Notes")}
            if is_link:
                body = {"class": "NewRelationshipRequestBody", "properties": props, **_audit_fields(attributes)}
                await client._async_link_elements_as_peer_duplicates(element_guid=target_guid, peer_duplicate_guid=other_guid, body=body)
            else:
                body = {"class": "DeleteRelationshipRequestBody", **_audit_fields(attributes)}
                await client._async_unlink_elements_as_peer_duplicates(element_guid=target_guid, peer_duplicate_guid=other_guid, body=body)

        elif om_type == "ConsolidatedDuplicateLink":
            other_guid = _guid(attributes, "Consolidated Source")
            client = self.client.classification_manager
            if is_link:
                body = {"class": "NewRelationshipRequestBody", "properties": {"class": "ConsolidatedDuplicateLinkProperties"}, **_audit_fields(attributes)}
                await client._async_link_consolidated_duplicate_to_source(element_guid=target_guid, source_element_guid=other_guid, body=body)
            else:
                body = {"class": "DeleteRelationshipRequestBody", **_audit_fields(attributes)}
                await client._async_unlink_consolidated_duplicate_from_source_element(element_guid=target_guid, source_element_guid=other_guid, body=body)

        elif om_type == "ResourceList":
            # Tier 2 -- requires add_resource_to_element/remove_resource_from_element on
            # ClassificationExplorer (new methods, mirroring add_scope_to_element).
            other_guid = _guid(attributes, "Resource")
            client = self.client.classification_manager
            props = {"class": "ResourceListProperties", "resourceUse": _v(attributes, "Resource Use"),
                     "additionalProperties": _v(attributes, "Additional Properties")}
            if is_link:
                body = {"class": "NewRelationshipRequestBody", "properties": props, **_audit_fields(attributes)}
                await client._async_add_resource_to_element(resource_guid=other_guid, element_guid=target_guid, body=body)
            else:
                body = {"class": "DeleteRelationshipRequestBody", **_audit_fields(attributes)}
                await client._async_remove_resource_from_element(resource_guid=other_guid, element_guid=target_guid, body=body)

        elif om_type == "MoreInformation":
            # Tier 2 -- requires add_more_information/remove_more_information on
            # ClassificationExplorer (new methods, mirroring add_scope_to_element).
            other_guid = _guid(attributes, "More Information Resource")
            client = self.client.classification_manager
            if is_link:
                body = {"class": "NewRelationshipRequestBody", "properties": {"class": "MoreInformationProperties"}, **_audit_fields(attributes)}
                await client._async_add_more_information(more_info_guid=other_guid, element_guid=target_guid, body=body)
            else:
                body = {"class": "DeleteRelationshipRequestBody", **_audit_fields(attributes)}
                await client._async_remove_more_information(more_info_guid=other_guid, element_guid=target_guid, body=body)

        elif om_type == "SearchKeywordLink":
            client = self.client.classification_manager
            if verb == "Attach":
                props = {"class": "SearchKeywordProperties", "displayName": _v(attributes, "Keyword"),
                         "description": _v(attributes, "Keyword Description")}
                body = {"class": "NewAttachmentRequestBody", "properties": props, **_audit_fields(attributes)}
                await client._async_add_search_keyword_to_element(target_guid, body)
                logger.success(f"Attached search keyword to {target_guid}")
                return f"\n\n## {verb} {object_type}\n\nAttached search keyword '{_v(attributes, 'Keyword')}' to {target_guid}."
            else:
                # Update/Detach need the SearchKeyword entity's own GUID, which this command's
                # attribute set has no way to reference. Known gap -- see module docstring.
                raise PyegeriaException(
                    f"'{verb} Search Keyword' is not yet implemented: the compact-JSON spec for this "
                    f"command has no 'Search Keyword GUID' attribute to identify which keyword entity "
                    f"to {verb.lower()}. Only 'Attach Search Keyword' (create+attach) is wired."
                )

        else:
            raise PyegeriaException(f"Unsupported Curation link OM_TYPE: '{om_type}' ({object_type})")

        logger.success(f"{verb}ed {object_type}")
        return f"\n\n## {verb} {object_type}\n\n{'Linked' if is_link else 'Unlinked'} {target_guid} ({om_type})."
