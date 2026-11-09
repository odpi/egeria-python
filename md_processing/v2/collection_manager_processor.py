"""
Collection Manager Processors for Dr.Egeria v2.
"""
from typing import Dict, Any, Optional
from loguru import logger

from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.common_md_utils import (
    set_create_body, set_update_body,
    update_element_dictionary,
    set_collection_manager_body, set_rel_request_body, set_delete_request_body,
    set_delete_rel_request_body,
    async_add_note_in_dr_e, set_object_classifications, report_spec_microflow
)
from pyegeria.core.utils import body_slimmer
from md_processing.v2.multilink import async_link_or_update, update_body


class CollectionManagerProcessor(AsyncBaseCommandProcessor):
    """
    Unified Processor for Collection Manager elements (Collections, Products, Agreements, etc.).
    Supports subtypes like Folders, Root Collections, Digital Products, and Agreements.
    """

    def check_parsed_attributes(self, attributes: Dict[str, Any]) -> list:
        """A Report Spec's Microflow must be valid JSON: a microflow/1 object, or a bare list
        (format 0), which is converted to microflow/1 when written (RS-EGERIA-TIER)."""
        object_type = getattr(self, 'canonical_object_type', self.command.object_type)
        if object_type not in ("Report Spec", "ReportSpec"):
            return []
        try:
            report_spec_microflow(attributes)
        except ValueError as exc:
            return [f"Report Spec '{attributes.get('Display Name', {}).get('value')}': {exc}"]
        return []

    async def _async_resolve_agreement_actor_relationship_guid(
            self, agreement_guid: str, actor_guid: str) -> Optional[str]:
        """Look up the AgreementActor relationship guid linking a given agreement and actor.

        `detach_agreement_actor` (pyegeria.omvs.collection_manager) takes the relationship guid
        directly rather than the two element guids it links, and `link_agreement_actor` doesn't
        hand back the guid of the relationship it creates - so a standalone "Detach Agreement
        Actor" command (run without a preceding "Link" in the same batch) has to resolve it via a
        lookup. Uses Classification Explorer's generic `get_relationships` rather than
        duplicating that logic here.
        """
        relationships = await self.client._async_get_relationships(
            "AgreementActor", body={"class": "ResultsRequestBody"})
        if isinstance(relationships, str) or not relationships:
            return None
        for rel in relationships:
            end1 = rel.get("elementGUIDAtEnd1")
            end2 = rel.get("elementGUIDAtEnd2")
            if {end1, end2} == {agreement_guid, actor_guid}:
                return rel.get("relationshipGUID")
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = getattr(self, 'canonical_object_type', self.command.object_type)
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        journal_entry = attributes.get('Journal Entry', {}).get('value')

        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block

            if object_type == "Data Sharing Agreement":
                actual_object_type = "Agreement"
            elif om_type:
                actual_object_type = om_type
            else:
                actual_object_type = object_type

            self.last_body = body = set_update_body(actual_object_type, attributes)
            prop_body = set_collection_manager_body(actual_object_type, qualified_name, attributes)
            body['properties'] = self.filter_update_properties(prop_body, body.get('mergeUpdate', True))
            
            # Dynamic routing for update based on type
            type_slug = object_type.lower().replace(" ", "_")
            method_name = f"_async_update_{type_slug}"
            
            if object_type == "Digital Product":
                method_name = "_async_update_digital_product"
            elif object_type in ["Agreement", "Data Sharing Agreement"]:
                method_name = "_async_update_agreement"
            elif object_type == "Digital Subscription":
                method_name = "_async_update_digital_subscription"
            
            if hasattr(self.client, method_name):
                method = getattr(self.client, method_name)
                await method(guid, body)
            else:
                await self.client._async_update_collection(guid, body)
                
            self.parsed_output["guid"] = guid

            if journal_entry:
                try:
                    j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                    if j_guid:
                        self.add_related_result("Journal Entry", j_guid)
                except Exception as e:
                    self.add_related_result("Journal Entry", status="failure", message=str(e))

            logger.success(f"Updated {object_type} '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            if object_type == "Data Sharing Agreement":
                actual_object_type = "Agreement"
            elif om_type:
                actual_object_type = om_type
            else:
                actual_object_type = object_type

            self.last_body = body = set_create_body(actual_object_type, attributes)
            body["properties"] = set_collection_manager_body(actual_object_type, qualified_name, attributes)
            
            # Handle classifications if present (e.g. for Taxonomy, CanonicalVocabulary)
            classifications = attributes.get('Classifications', {}).get('name_list', None)
            if classifications:
                # If classifications are specified, use them. 
                # Otherwise if it is a Glossary, we might have default classifications.
                body["initialClassifications"] = set_object_classifications(object_type, attributes, classifications)
            elif object_type == "Data Sharing Agreement":
                # Data Sharing Agreement is an Agreement with a specific classification
                body["initialClassifications"] = {
                    "DataSharingAgreement": {
                        "class": "DataSharingAgreementProperties"
                    }
                }
            elif "Glossary" in object_type:
                # Was unconditional (both classifications on every Glossary,
                # regardless of what the user set) -- confirmed live bug, not
                # just a missing field (PYEGERIA_ISSUES.md Cluster B
                # follow-up). Is Canonical/Is Taxonomy both default False per
                # the compact spec, so default False here too if unset.
                glossary_classifications = {}
                if attributes.get('Is Taxonomy', {}).get('value', False):
                    glossary_classifications["Taxonomy"] = {
                        "class": "TaxonomyProperties",
                        "organizingPrinciple": attributes.get('Organizing Principle', {}).get('value'),
                    }
                if attributes.get('Is Canonical', {}).get('value', False):
                    glossary_classifications["CanonicalVocabulary"] = {
                        "class": "CanonicalVocabularyProperties",
                        "scope": attributes.get('Canonical Scope', {}).get('value'),
                    }
                if glossary_classifications:
                    body["initialClassifications"] = glossary_classifications


            # Handle parent relationship for collections if specified
            if body.get('parentGUID') and not body.get('parentRelationshipTypeName'):
                body['parentRelationshipTypeName'] = "CollectionMembership"
                body['parentAtEnd1'] = True

            # Dynamic routing to appropriate create method
            # Try specific methods first, then generic collection creation
            type_slug = object_type.lower().replace(" ", "_")
            method_name = f"_async_create_{type_slug}"
            
            # Special cases for names
            if object_type == "Digital Product Catalog":
                method_name = "_async_create_digital_product_catalog"
            elif object_type == "Digital Product":
                 method_name = "_async_create_digital_product"
            elif object_type == "Data Specification":
                 method_name = "_async_create_data_spec_collection"
            elif object_type == "Data Dictionary":
                 method_name = "_async_create_data_dictionary_collection"
            elif object_type in ["Agreement", "Data Sharing Agreement"]:
                 method_name = "_async_create_agreement"
            elif object_type == "Digital Subscription":
                 method_name = "_async_create_digital_subscription"
            elif object_type == "Skill Set":
                method_name = "_async_create_skill_set_collection"
            elif object_type == "Reference List":
                method_name = "_async_create_reference_list_collection"
            elif object_type == "Report Type":
                method_name = "_async_create_report_type_collection"
            elif object_type == "Question Spec":
                method_name = "_async_create_question_spec_folder"
            
            if hasattr(self.client, method_name):
                method = getattr(self.client, method_name)
                # Some methods require body=body, others take body as positional
                try:
                    if "Glossary" == object_type:
                        raw_guid = await method(display_name=display_name, body=body)
                    else:
                        raw_guid = await method(body=body_slimmer(body)) if "Digital Product" in object_type else await method(body=body)
                except TypeError:
                    raw_guid = await method(body)
            else:
                # Generic fallback for any other collection subtype
                raw_guid = await self.client._async_create_collection(body=body, prop=[object_type.replace(" ", "")])

            guid = self.extract_guid_or_raise(raw_guid, f"Create {object_type}")

            if guid:
                self.parsed_output["guid"] = guid

                if journal_entry:
                    try:
                        j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                        if j_guid:
                            self.add_related_result("Journal Entry", j_guid)
                    except Exception as e:
                        self.add_related_result("Journal Entry", status="failure", message=str(e))

                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created {object_type} '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.raw_block

class CSVElementProcessor(AsyncBaseCommandProcessor):
    """
    Processor for CSV Elements from Template.
    """


    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None # Create only for now

    async def apply_changes(self) -> str:
        if self.command.verb != "Create":
            return self.command.raw_block
            
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        
        raw_guid = await self.client._async_get_create_csv_data_file_element_from_template(
            attributes.get('File Name', {}).get('value'),
            attributes.get('File Type', {}).get('value'),
            attributes.get('File Path', {}).get('value'),
            attributes.get('Version Identifier', {}).get('value'),
            attributes.get('File Encoding', {}).get('value', 'UTF-8'),
            attributes.get('File Extension', {}).get('value', 'csv'),
            attributes.get('File System Name', {}).get('value'),
            attributes.get('Description', {}).get('value')
        )
        guid = self.extract_guid_or_raise(raw_guid, "Create CSV Element")

        if guid:
            self.parsed_output["guid"] = guid
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            logger.success(f"Created CSV Element '{display_name}' with GUID {guid}")
            return f"## Created CSV Element\n\nGUID: {guid}\nQualified Name: {qualified_name}"

        return self.command.raw_block

# Relationship types CollectionLinkProcessor knows how to link and detach,
# keyed by the compact spec's OM_TYPE.
_COLLECTION_LINK_TYPES = frozenset({
    "AgreementItem", "AgreementActor", "CollectionMembership", "DigitalProductDependency",
    "BusinessCapabilityDependency", "DigitalSupport", "ResourceList", "DataDescription",
    "DigitalSubscriber",
})

# Phrase fallbacks for when no compact spec resolved (so there is no OM_TYPE),
# checked in order against the object type.  Every command phrasing that
# reaches this processor must land on exactly one relationship type here or
# via OM_TYPE -- a miss raises rather than reporting a no-op as success.
_COLLECTION_LINK_PHRASES = (
    (("Agreement Item", "Agreement to Item", "Agreement from Item"), "AgreementItem"),
    (("Agreement Actor", "Agreement to Actor", "Agreement from Actor"), "AgreementActor"),
    (("Business Capability Dependency", "Supporting Capability"), "BusinessCapabilityDependency"),
    (("Digital Support", "Digital Service"), "DigitalSupport"),
    (("Product Dependency", "Digital Product", "Product-Product"), "DigitalProductDependency"),
    (("Attach Collection", "Resource List", "Collection to Resource", "Collection from Resource",
      "Collection->Resource"), "ResourceList"),
    (("Data Description",), "DataDescription"),
    (("Subscriber",), "DigitalSubscriber"),
    (("Collection Member", "Member"), "CollectionMembership"),
)


class CollectionLinkProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Agreement Items, Collection Membership, product dependencies, etc.
    """


    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    # The Agreement Actor detach below calls this, but it was only defined on
    # CollectionManagerProcessor, so a detach without an explicit relationship
    # GUID died with AttributeError.  It uses nothing but self.client.
    _async_resolve_agreement_actor_relationship_guid = (
        CollectionManagerProcessor._async_resolve_agreement_actor_relationship_guid)

    def _relationship_type(self, object_type: str) -> str:
        """Which relationship this command links/detaches, or raise if none.

        The compact spec's OM_TYPE is authoritative: every phrasing of a
        command (``Detach Member from Collection``, ``Remove Member``, ...)
        resolves to the same spec, whose canonical object type ("Member to
        Collection") need not contain the words a substring test looks for.
        The phrase table is only a fallback for phrasings no spec resolves.
        """
        om_type = getattr(self, "egeria_type_name", None)
        if om_type in _COLLECTION_LINK_TYPES:
            return om_type
        names = [object_type or "", self.command.object_type or ""]
        for phrases, rel_type in _COLLECTION_LINK_PHRASES:
            if any(p in name for name in names for p in phrases):
                return rel_type
        raise ValueError(
            f"{self.command.verb} {self.command.object_type}: no relationship handler for object type "
            f"'{object_type}' (OM_TYPE {om_type!r}); nothing was sent to Egeria")

    def _require_guids(self, attributes: dict, *names: str) -> tuple:
        """GUIDs of the named reference attributes, in order, or raise.

        A detach whose end did not resolve must refuse with words, not send
        ``None`` to Egeria and not report "Operation completed".
        """
        guids = tuple((attributes.get(n) or {}).get('guid') for n in names)
        missing = [f"{n} ({(attributes.get(n) or {}).get('value')!r})" for n, g in zip(names, guids) if not g]
        if missing:
            raise ValueError(f"{self.command.verb} {self.command.object_type}: did not resolve to a GUID: "
                             f"{', '.join(missing)}; nothing was sent to Egeria")
        return guids

    def _resource_list_ends(self, attributes: dict) -> tuple[str, str]:
        """(resource guid, collection guid) for a ResourceList link/detach, or raise.

        The compact spec names the resource end "Element Id"; older markdown
        used "Resource Id".  Accept either, and never send a request with an
        unresolved end.
        """
        guid_res = ((attributes.get('Resource Id') or {}).get('guid')
                    or (attributes.get('Element Id') or {}).get('guid'))
        guid_coll = (attributes.get('Collection Id') or {}).get('guid')
        if not guid_res or not guid_coll:
            raise ValueError(f"{self.command.verb} {self.command.object_type}: Collection Id and Element Id "
                             f"(or Resource Id) must both resolve to a GUID (got {guid_coll!r}, {guid_res!r}); "
                             f"nothing was sent to Egeria")
        return guid_res, guid_coll

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.canonical_object_type
        attributes = self.parsed_output["attributes"]
        rel_type = self._relationship_type(object_type)

        self.last_body = body = set_rel_request_body(object_type, attributes)
        new_rel_guids: list[str] = []

        if verb in ["Link", "Attach", "Add"]:
            if rel_type == "AgreementItem":
                guid1 = attributes.get('Agreement Name', {}).get('guid')
                guid2 = attributes.get('Item Name', {}).get('guid')
                body['properties'] = {
                    "class": "AgreementItemProperties",
                    "typeName": "AgreementItem",
                    "agreementItemId": attributes.get("Agreement Item Id", {}).get("value"),
                    "agreementItemTypeName": attributes.get("Agreement Item Type", {}).get("value"),
                    "agreementStart": attributes.get("Agreement Start Date", {}).get("value"),
                    "agreementEnd": attributes.get("Agreement End Date", {}).get("value"),
                    "restrictions": attributes.get("Restrictions", {}).get("value"),
                    "obligations": attributes.get("Obligations", {}).get("value"),
                    "entitlements": attributes.get("Entitlements", {}).get("value"),
                    "usageMeasurements": attributes.get("Usage Measurements", {}).get("value"),
                    "effectiveFrom": attributes.get("Effective From", {}).get("value"),
                    "effectiveTo": attributes.get("Effective To", {}).get("value")
                }
                # AgreementItem is MULTI_LINK (see pyegeria.core.relationship_multiplicity)
                # -- more than one item relationship can exist between the same
                # agreement/item pair, so the created relationship's own GUID is
                # captured and surfaced here; it's the only reliable way to target
                # this specific instance later via a "GUID" attribute on Detach.
                # A re-run updates the item with the same agreementItemId instead
                # of adding a duplicate.
                rel_guid, _ = await async_link_or_update(
                    self.client, "AgreementItem", guid1, guid2,
                    {"agreementItemId": body['properties']['agreementItemId']},
                    create=lambda: self.client._async_link_agreement_item(guid1, guid2, body),
                    update=lambda g: self.client._async_update_agreement_item(g, update_body(body['properties'])))
                if rel_guid:
                    self.parsed_output["guid"] = rel_guid
                    new_rel_guids.append(rel_guid)

            elif rel_type == "AgreementActor":
                guid_ag = attributes.get('Agreement Name', {}).get('guid')
                actor_data = attributes.get('Actors', {})
                actor_guids = actor_data.get('guid_list') or ([actor_data.get('guid')] if actor_data.get('guid') else [])

                body['properties'] = {
                    "class": "AgreementActorProperties",
                    "typeName": "AgreementActor",
                    "actorRole": attributes.get("Actor Name", {}).get("value"),
                    "agreementStart": attributes.get("Agreement Start Date", {}).get("value"),
                    "agreementEnd": attributes.get("Agreement End Date", {}).get("value"),
                    "restrictions": attributes.get("Restrictions", {}).get("value"),
                    "obligations": attributes.get("Obligations", {}).get("value"),
                    "entitlements": attributes.get("Entitlements", {}).get("value"),
                    "usageMeasurements": attributes.get("Usage Measurements", {}).get("value"),
                    "effectiveFrom": attributes.get("Effective From", {}).get("value"),
                    "effectiveTo": attributes.get("Effective To", {}).get("value")
                }
                # AgreementActor is MULTI_LINK -- same reasoning as AgreementItem above.
                # Egeria has no AgreementActor update endpoint, so a re-run reuses the
                # actor link with the same actorRole unchanged rather than duplicating it.
                for guid_ac in actor_guids:
                    if guid_ac:
                        rel_guid, created = await async_link_or_update(
                            self.client, "AgreementActor", guid_ag, guid_ac,
                            {"actorRole": body['properties']['actorRole']},
                            create=lambda: self.client._async_link_agreement_actor(guid_ag, guid_ac, body))
                        if not created:
                            logger.warning(f"AgreementActor {rel_guid} already exists; its other properties "
                                           f"were not changed (Egeria has no AgreementActor update)")
                        if rel_guid:
                            new_rel_guids.append(rel_guid)
                if len(new_rel_guids) == 1:
                    self.parsed_output["guid"] = new_rel_guids[0]

            elif rel_type == "CollectionMembership":
                guid_coll = attributes.get('Collection Id', {}).get('guid')
                guid_el = attributes.get('Element Id', {}).get('guid')
                body['properties'] = {
                    "class": "CollectionMembershipProperties",
                    "typeName": "CollectionMembership",
                    "membershipType": attributes.get('Membership Type', {}).get('value'),
                    "membershipRationale": attributes.get('Membership Rationale', {}).get('value'),
                    "expression": attributes.get('Expression', {}).get('value'),
                    "membershipStatus": attributes.get('Membership Status', {}).get('value', 'ACTIVE').upper(),
                    "userDefinedStatus": attributes.get('User Defined Status', {}).get('value'),
                    "confidence": attributes.get('Confidence', {}).get('value'),
                    "steward": attributes.get('Steward', {}).get('guid'),
                    "stewardTypeName": attributes.get('Steward Type Name', {}).get('value'),
                    "stewardPropertyName": attributes.get('Steward Property Name', {}).get('value'),
                    "source": attributes.get('Source', {}).get('value'),
                    "notes": attributes.get('Notes', {}).get('value'),
                }
                await self.client._async_add_to_collection(guid_coll, guid_el, body_slimmer(body))

            elif rel_type == "DigitalProductDependency":
                guid1 = attributes.get('Digital Product 1', {}).get('guid')
                guid2 = attributes.get('Digital Product 2', {}).get('guid')
                body['properties'] = {
                    "class": "DigitalProductDependencyProperties",
                    "typeName": "DigitalProductDependency",
                    "label": attributes.get('Label', {}).get('value'),
                    "description": attributes.get('Description', {}).get('value'),
                    "iscQualifiedName": attributes.get('ISC Qualified Name', {}).get('value'),
                    "effectiveFrom": attributes.get('Effective From', {}).get('value'),
                    "effectiveTo": attributes.get('Effective To', {}).get('value')
                }
                # DigitalProductDependency is MULTI_LINK -- same reasoning as
                # AgreementItem above.  Because the server never merges a second
                # instance, re-running the same markdown would add a duplicate of
                # every dependency.  Target the existing instance instead: an explicit
                # GUID if the command gives one, otherwise the dependency between the
                # same two products with the same label and supply chain (a pair of
                # products may legitimately have one dependency per chain under one label).
                rel_guid, _ = await async_link_or_update(
                    self.client, "DigitalProductDependency", guid1, guid2,
                    {"label": body['properties']['label'],
                     "iscQualifiedName": body['properties']['iscQualifiedName']},
                    create=lambda: self.client._async_link_digital_product_dependency(guid1, guid2, body),
                    update=lambda g: self.client._async_update_digital_product_dependency(
                        g, update_body(body['properties'])),
                    explicit_guid=(attributes.get('GUID') or {}).get('guid') or (attributes.get('GUID') or {}).get('value'))
                if rel_guid:
                    self.parsed_output["guid"] = rel_guid
                    new_rel_guids.append(rel_guid)

            elif rel_type == "BusinessCapabilityDependency":
                # BusinessCapabilityDependency is UNI_LINK, so attach is an upsert.
                body['properties'] = {
                    "class": "BusinessCapabilityDependencyProperties",
                    "label": attributes.get('Label', {}).get('value'),
                    "description": attributes.get('Description', {}).get('value'),
                }
                await self.client._async_link_business_capability_dependency(
                    attributes.get('Dependent Capability', {}).get('guid'),
                    attributes.get('Supporting Capability', {}).get('guid'), body)

            elif rel_type == "DigitalSupport":
                # DigitalSupport is UNI_LINK, so attach is an upsert.
                body['properties'] = {
                    "class": "DigitalSupportProperties",
                    "label": attributes.get('Label', {}).get('value'),
                    "description": attributes.get('Description', {}).get('value'),
                }
                await self.client._async_link_digital_support(
                    attributes.get('Supported Capability', {}).get('guid'),
                    attributes.get('Digital Service', {}).get('guid'), body)

            elif rel_type == "ResourceList":
                guid_res, guid_coll = self._resource_list_ends(attributes)
                body['properties'] = {
                    "class": "ResourceListProperties",
                    "typeName": "ResourceList",
                    "label": attributes.get('Label', {}).get('value'),
                    "resourceUse": attributes.get('Resource Use', {}).get('value'),
                    "description": attributes.get('Description', {}).get('value'),
                    "additionalProperties": attributes.get('Additional Properties', {}).get('value'),
                    "effectiveFrom": attributes.get('Effective From', {}).get('value'),
                    "effectiveTo": attributes.get('Effective To', {}).get('value')
                }
                await self.client._async_attach_collection(guid_res, guid_coll, body)

            elif rel_type == "DataDescription":
                guid_coll = attributes.get('Collection Id', {}).get('guid')
                guid_el = attributes.get('Element Id', {}).get('guid')
                body['properties'] = {
                    "class": "DataDescriptionProperties",
                }
                await self.client._async_attach_data_description(guid_el, guid_coll, body)

            elif rel_type == "DigitalSubscriber":
                guid_sub = attributes.get('Subscriber Id', {}).get('guid')
                guid_sn = attributes.get('Subscription Id', {}).get('guid')
                body['properties'] = {
                    "class": "DigitalSubscriberProperties",
                    "typeName": "DigitalSubscriber",
                    "subscriberId": attributes.get('Subscriber Id', {}).get('value'),
                    "effectiveFrom": attributes.get('Effective From', {}).get('value'),
                    "effectiveTo": attributes.get('Effective To', {}).get('value'),
                }
                await self.client._async_link_subscriber(guid_sub, guid_sn, body)
            else:  # _relationship_type() returned a type with no link branch
                raise ValueError(f"{verb} {object_type}: no link handler for {rel_type}; nothing was sent to Egeria")

            logger.success(f"Linked {object_type}")

            # Format the output with attributes for better feedback
            header = f"\n\n## {verb} {object_type}\n\nOperation completed.\n\n"
            if new_rel_guids:
                # These object types are MULTI_LINK (see
                # pyegeria.core.relationship_multiplicity) -- more than one
                # instance can exist between the same pair of elements, so
                # the relationship's own GUID (not just the element pair) is
                # required to target this specific instance later via a
                # "GUID" attribute on Detach.
                label = "Relationship GUID" if len(new_rel_guids) == 1 else "Relationship GUIDs"
                header += f"### {label}\n" + "\n".join(f"- `{g}`" for g in new_rel_guids) + "\n\n"
            if rel_type == "CollectionMembership":
                header += "### Associated Elements\n"
                header += f"- **Collection Id**: `{attributes.get('Collection Id', {}).get('value')}`\n"
                header += f"- **Element Id**: `{attributes.get('Element Id', {}).get('value')}`\n\n"
            
            header += "### Link Properties\n"
            # Exclude standard command identifiers when dumping properties
            for k, v in attributes.items():
                if k not in ["Collection Id", "Element Id", "Digital Product 1", "Digital Product 2",
                             "Dependent Capability", "Supporting Capability", "Supported Capability", "Digital Service", "Subscriber Id", "Subscription", "Resource Id", "Agreement Name", "Item Name", "Qualified Name", "Display Name"]:
                    val = v.get("value")
                    if val:
                        header += f"- **{k}**: {val}\n"
            
            return header

        elif verb in ["Detach", "Unlink", "Remove"]:
            self.last_body = body = set_delete_rel_request_body(object_type, attributes)
            # Explicit relationship GUID, if the user supplied one (as returned
            # by the original Link command) -- required to disambiguate when
            # more than one relationship instance exists between the same
            # pair of elements (AgreementItem/AgreementActor/
            # DigitalProductDependency are all MULTI_LINK; see
            # pyegeria.core.relationship_multiplicity). Falls back to the
            # pair-based lookup below when not supplied, for backward
            # compatibility with markdown written before this attribute
            # existed and for the common single-instance case.
            explicit_rel_guid = (attributes.get("GUID") or {}).get("guid") or (attributes.get("GUID") or {}).get("value")
            if rel_type == "AgreementItem":
                if explicit_rel_guid:
                    await self.client._async_detach_agreement_item_by_id(explicit_rel_guid, body)
                else:
                    await self.client._async_detach_agreement_item(
                        *self._require_guids(attributes, 'Agreement Name', 'Item Name'), body)
            elif rel_type == "AgreementActor":
                if explicit_rel_guid:
                    await self.client._async_detach_agreement_actor(explicit_rel_guid, body)
                else:
                    (guid_ag,) = self._require_guids(attributes, 'Agreement Name')
                    actor_data = attributes.get('Actors') or {}
                    actor_guids = [g for g in (actor_data.get('guid_list')
                                               or ([actor_data.get('guid')] if actor_data.get('guid') else [])) if g]
                    if not actor_guids:
                        raise ValueError(f"{verb} {object_type}: Actors did not resolve to any GUID "
                                         f"({actor_data.get('value')!r}); nothing was sent to Egeria")
                    detached, not_linked = 0, []
                    for guid_ac in actor_guids:
                        rel_guid = await self._async_resolve_agreement_actor_relationship_guid(guid_ag, guid_ac)
                        if rel_guid:
                            await self.client._async_detach_agreement_actor(rel_guid, body)
                            detached += 1
                        else:
                            not_linked.append(guid_ac)
                            logger.warning(
                                f"No AgreementActor relationship found between agreement {guid_ag} and actor {guid_ac} - skipping detach")
                    if not detached:
                        raise ValueError(f"{verb} {object_type}: no AgreementActor relationship found between agreement "
                                         f"{guid_ag} and actor(s) {', '.join(not_linked)}; nothing was sent to Egeria")
                    if not_linked:
                        self._add_warning(f"No AgreementActor relationship for actor(s) {', '.join(not_linked)}; "
                                          f"those were not detached")
            elif rel_type == "CollectionMembership":
                await self.client._async_remove_from_collection(
                    *self._require_guids(attributes, 'Collection Id', 'Element Id'), body)
            elif rel_type == "DigitalProductDependency":
                if explicit_rel_guid:
                    await self.client._async_detach_digital_product_dependency_by_id(explicit_rel_guid, body)
                else:
                    await self.client._async_detach_digital_product_dependency(
                        *self._require_guids(attributes, 'Digital Product 1', 'Digital Product 2'), body)
            elif rel_type == "BusinessCapabilityDependency":
                await self.client._async_detach_business_capability_dependency(
                    *self._require_guids(attributes, 'Dependent Capability', 'Supporting Capability'), body)
            elif rel_type == "DigitalSupport":
                await self.client._async_detach_digital_support(
                    *self._require_guids(attributes, 'Supported Capability', 'Digital Service'), body)
            elif rel_type == "ResourceList":
                await self.client._async_detach_collection(*self._resource_list_ends(attributes), body)
            elif rel_type == "DataDescription":
                await self.client._async_detach_data_description(
                    *self._require_guids(attributes, 'Element Id', 'Collection Id'), body)
            elif rel_type == "DigitalSubscriber":
                await self.client._async_detach_subscriber(
                    *self._require_guids(attributes, 'Subscriber Id', 'Subscription Id'), body)
            else:  # _relationship_type() returned a type with no detach branch
                raise ValueError(f"{verb} {object_type}: no detach handler for {rel_type}; nothing was sent to Egeria")

            logger.success(f"Detached {object_type}")
            return f"\n\n## {verb} {object_type}\n\nOperation completed."

        return self.command.raw_block
