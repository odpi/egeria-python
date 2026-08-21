"""
Curation Processors for Dr.Egeria v2.

Handles the "Curation" command family: post-hoc classification and
relationship curation for existing Referenceable elements.

CurationClassifyProcessor -- Classify/Reclassify/Update/Declassify commands
for: Impact, Confidence, Confidentiality, Criticality, Retention, Ownership,
Digital Resource Origin, Zone Membership, Data Scope, Governance
Expectations, Governance Measurements, Security Tags, Known Duplicate,
Consolidated Duplicate, Class Word, Modifier, Prime Word, the 10 governance-
point classifications (0435: Control/Verification/Enforcement/Execution/
Policy Administration/Policy Decision/Policy Enforcement/Policy Information/
Policy Management/Policy Retrieval Point), 6 metamodel/classification-
explorer markers (0463: Incomplete, ObjectIdentifier, ReferenceData,
MobileResource, InstanceMetadata, MetamodelInstance), and ProjectKind (0130)/
CollectionKind (0021).

CurationLinkProcessor -- Link/Unlink/Attach/Detach relationship commands
for: Semantic Assignment, Semantic Definition, Scoped By, Peer Duplicate,
Consolidated Duplicate Link, Resource List, and Search Keyword (Attach
creates a new keyword and links it in one call; Update/Detach act on the
SearchKeyword entity's own GUID via a "Search Keyword GUID" attribute,
added 2026-08-21 -- previously a known gap, see below).

ClassWord/Modifier/PrimeWord (0438 naming standards classifications) were
added 2026-08-09 once Egeria PR #9166 shipped the backing REST endpoints
(glossary-manager's is-class-word/is-modifier/is-prime-word) -- see the new
set/clear method pairs in pyegeria/omvs/glossary_manager.py. They route
through GlossaryManager, not ClassificationExplorer.

The 10 governance-point classifications, the 6 classification-explorer
markers, and ProjectKind/CollectionKind were added 2026-08-21 once an
omvs_audit.py gap-closure pass shipped their backing REST endpoints
(governance_officer.py, classification_explorer.py, project_manager.py,
collection_manager.py respectively) -- confirmed against a live 6.2-SNAPSHOT
server's /v3/api-docs. Policy Management Point's command already existed in
the compact spec (parse-only, no backing method, per the module docstring's
previous note here) -- this is what unblocks it; the other 9 governance
points are new commands added alongside it. No classification in this
family remains genuinely unimplemented as of this pass.

Update/Detach Search Keyword were "PARTIALLY implemented" as of the note
previously here: they need the previously-created SearchKeyword entity's
own GUID, which the compact-JSON attribute set for this command had no way
to reference. Fixed 2026-08-21 by adding a "Search Keyword GUID" attribute
to the shared "Search Keyword Link Base" bundle (present but optional/
unused on Attach, since that command creates a new keyword rather than
referencing an existing one) and wiring
_async_update_search_keyword/_async_remove_search_keyword_from_element
(both take only the keyword's own GUID, not the Target Element it's
attached to -- confirmed in classification_explorer.py).
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
    # 0435 governance-point classifications -- routed through GovernanceOfficer
    # (not ClassificationExplorer, see CURATION_CLASSIFICATION_CLIENTS below).
    # Added 2026-08-21 once GovernanceOfficer._async_set_*_point/_async_clear_*_point
    # shipped (verified against a live 6.2-SNAPSHOT server). PolicyManagementPoint's
    # command already existed in the compact spec (parse-only, no backing method) --
    # this is what unblocks it; the other 9 are new commands added alongside it.
    "ControlPoint": ClassificationSpec(
        "_async_set_control_point", "_async_clear_control_point", "ControlPointProperties"),
    "VerificationPoint": ClassificationSpec(
        "_async_set_verification_point", "_async_clear_verification_point", "VerificationPointProperties"),
    "EnforcementPoint": ClassificationSpec(
        "_async_set_enforcement_point", "_async_clear_enforcement_point", "EnforcementPointProperties"),
    "ExecutionPoint": ClassificationSpec(
        "_async_set_execution_point", "_async_clear_execution_point", "ExecutionPointProperties"),
    "PolicyAdministrationPoint": ClassificationSpec(
        "_async_set_policy_administration_point", "_async_clear_policy_administration_point", "PolicyAdministrationPointProperties"),
    "PolicyDecisionPoint": ClassificationSpec(
        "_async_set_policy_decision_point", "_async_clear_policy_decision_point", "PolicyDecisionPointProperties"),
    "PolicyEnforcementPoint": ClassificationSpec(
        "_async_set_policy_enforcement_point", "_async_clear_policy_enforcement_point", "PolicyEnforcementPointProperties"),
    "PolicyInformationPoint": ClassificationSpec(
        "_async_set_policy_information_point", "_async_clear_policy_information_point", "PolicyInformationPointProperties"),
    "PolicyManagementPoint": ClassificationSpec(
        "_async_set_policy_management_point", "_async_clear_policy_management_point", "PolicyManagementPointProperties"),
    "PolicyRetrievalPoint": ClassificationSpec(
        "_async_set_policy_retrieval_point", "_async_clear_policy_retrieval_point", "PolicyRetrievalPointProperties"),
    # 0463 metamodel/classification-explorer marker classifications, added 2026-08-21
    # once ClassificationExplorer._async_set_element_as_*/_async_clear_element_as_*
    # shipped (verified against a live 6.2-SNAPSHOT server). Routed through the
    # default classification_manager client -- no CURATION_CLASSIFICATION_CLIENTS
    # entry needed.
    "Incomplete": ClassificationSpec(
        "_async_set_element_as_incomplete", "_async_clear_element_as_incomplete", "IncompleteProperties"),
    "ObjectIdentifier": ClassificationSpec(
        "_async_set_element_as_object_identifier", "_async_clear_element_as_object_identifier", "ObjectIdentifierProperties"),
    "ReferenceData": ClassificationSpec(
        "_async_set_element_as_reference_data", "_async_clear_element_as_reference_data", "ReferenceDataProperties"),
    "MobileResource": ClassificationSpec(
        "_async_set_element_as_mobile_resource", "_async_clear_element_as_mobile_resource", "MobileResourceProperties"),
    "InstanceMetadata": ClassificationSpec(
        "_async_set_element_as_instance_metadata", "_async_clear_element_as_instance_metadata", "InstanceMetadataProperties",
        fields={"Instance Metadata Type Name": "instanceMetadataTypeName", "Description": "description"}),
    "MetamodelInstance": ClassificationSpec(
        "_async_set_element_as_metamodel_instance", "_async_clear_element_as_metamodel_instance", "MetamodelInstanceProperties",
        fields={"Metamodel Element": "metamodelElementGUID"}),
    # ProjectKind (0130) and CollectionKind (0021) -- pure marker classifications,
    # routed through ProjectManager/CollectionManager respectively (see
    # CURATION_CLASSIFICATION_CLIENTS below).
    "ProjectKind": ClassificationSpec(
        "_async_set_project_kind", "_async_clear_project_kind", "ProjectKindProperties"),
    "CollectionKind": ClassificationSpec(
        "_async_set_collection_kind", "_async_clear_collection_kind", "CollectionKindProperties"),
    # DataSharingAgreement retrofit -- "Create Data Sharing Agreement" (Digital
    # Products family, CollectionManagerProcessor) already sets this classification
    # at creation time via initialClassifications; this pair is for classifying/
    # declassifying an Agreement that already exists, routed through DigitalBusiness
    # (see CURATION_CLASSIFICATION_CLIENTS below).
    "DataSharingAgreement": ClassificationSpec(
        "_async_set_agreement_as_data_sharing_agreement", "_async_clear_agreement_as_data_sharing_agreement",
        "DataSharingAgreementProperties"),
}

# OM_TYPEs in CLASSIFICATION_METHODS whose set/clear methods live on a client other than
# self.client.classification_manager (the default every other entry above uses).
CURATION_CLASSIFICATION_CLIENTS = {
    "ClassWord": "glossary_manager",
    "Modifier": "glossary_manager",
    "PrimeWord": "glossary_manager",
    "ControlPoint": "governance_officer",
    "VerificationPoint": "governance_officer",
    "EnforcementPoint": "governance_officer",
    "ExecutionPoint": "governance_officer",
    "PolicyAdministrationPoint": "governance_officer",
    "PolicyDecisionPoint": "governance_officer",
    "PolicyEnforcementPoint": "governance_officer",
    "PolicyInformationPoint": "governance_officer",
    "PolicyManagementPoint": "governance_officer",
    "PolicyRetrievalPoint": "governance_officer",
    "ProjectKind": "project_manager",
    "CollectionKind": "collection_manager",
    "DataSharingAgreement": "digital_business",
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

    def supports_target_element_lookup(self) -> bool:
        # Same fix as CurationLinkProcessor, same root cause (ISSUE-68 pattern):
        # fetch_as_is() always returns None here, so without this override the
        # base class's Create<->Update upsert-transition logic silently rewrote
        # every "Update X" command (Data Scope, Governance Expectations,
        # Governance Measurements -- the three CLASSIFICATION_METHODS entries
        # with an update_method) to "Create X" before apply_changes() ever saw
        # verb="Update". That made `use_update = verb == "Update" and
        # class_spec.update_method` always False, so these commands silently
        # called the set_method (re-apply as new) instead of update_method --
        # not necessarily an error, likely idempotent-looking success, but not
        # what "Update" was supposed to do. Found and fixed 2026-08-21 while
        # investigating the identical bug in CurationLinkProcessor's new
        # "Update Search Keyword" command; pre-existing and unrelated to that.
        return False

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

    def supports_target_element_lookup(self) -> bool:
        # Relationship-only processor -- see GovernanceLinkProcessor's identical
        # override (md_processing/v2/governance.py) for why this matters: without
        # it, AsyncBaseCommandProcessor.execute()'s Create<->Update upsert-transition
        # logic silently rewrites the verb (ISSUE-68 follow-up). Latent here until
        # 2026-08-21's "Update Search Keyword" -- every other command this processor
        # handles uses Link/Unlink/Attach/Detach, never Update, so the bug (fetch_as_is()
        # always returning None -> "not found" -> Update rewritten to Create -> wrong
        # branch executed, e.g. Update Search Keyword silently deleting the keyword
        # instead of updating it) had nothing to trigger it before.
        return False

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
                # Update/Detach act on the SearchKeyword entity's own GUID, not the Target
                # Element - _async_update_search_keyword/_async_remove_search_keyword_from_element
                # both take only the keyword's own GUID (confirmed in classification_explorer.py;
                # "from_element" in the remove method's name is misleading - it deletes the keyword
                # entity itself, not just its link). Previously blocked on the compact spec having
                # no way to reference that GUID - "Search Keyword GUID" fixes that (2026-08-21).
                keyword_guid = _guid(attributes, "Search Keyword GUID")
                if not keyword_guid:
                    raise PyegeriaException(
                        f"Cannot {verb.lower()} Search Keyword: 'Search Keyword GUID' did not resolve "
                        f"to a GUID. This must be the SearchKeyword entity's own identifier (not the "
                        f"Target Element it's attached to)."
                    )
                if verb == "Update":
                    props = {"class": "SearchKeywordProperties"}
                    keyword = _v(attributes, "Keyword")
                    description = _v(attributes, "Keyword Description")
                    if keyword is not None:
                        props["displayName"] = keyword
                    if description is not None:
                        props["description"] = description
                    body = {"class": "UpdateElementRequestBody", "mergeUpdate": True, "properties": props,
                            **_audit_fields(attributes)}
                    await client._async_update_search_keyword(keyword_guid, body)
                    logger.success(f"Updated search keyword {keyword_guid}")
                    return f"\n\n## {verb} {object_type}\n\nUpdated search keyword {keyword_guid}."
                else:
                    await client._async_remove_search_keyword_from_element(keyword_guid)
                    logger.success(f"Removed search keyword {keyword_guid}")
                    return f"\n\n## {verb} {object_type}\n\nRemoved search keyword {keyword_guid}."

        else:
            raise PyegeriaException(f"Unsupported Curation link OM_TYPE: '{om_type}' ({object_type})")

        logger.success(f"{verb}ed {object_type}")
        return f"\n\n## {verb} {object_type}\n\n{'Linked' if is_link else 'Unlinked'} {target_guid} ({om_type})."
