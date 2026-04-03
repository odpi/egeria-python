"""
Collection Manager Processors for Dr.Egeria v2.
"""
from typing import Dict, Any, Optional
from loguru import logger

from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.md_processing_constants import (
    get_command_spec
)
from md_processing.md_processing_utils.common_md_utils import (
    set_create_body, set_update_body,
    update_element_dictionary,
    set_collection_manager_body, set_rel_request_body, set_delete_request_body,
    set_delete_rel_request_body,
    async_add_note_in_dr_e, set_object_classifications
)
from pyegeria.core.utils import body_slimmer


class CollectionManagerProcessor(AsyncBaseCommandProcessor):
    """
    Unified Processor for Collection Manager elements (Collections, Products, Agreements, etc.).
    Supports subtypes like Folders, Root Collections, Digital Products, and Agreements.
    """

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = getattr(self, 'canonical_object_type', self.command.object_type)
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        status = attributes.get('Status', {}).get('value', 'ACTIVE')
        journal_entry = attributes.get('Journal Entry', {}).get('value')

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block

            actual_object_type = "Agreement" if object_type == "Data Sharing Agreement" else object_type
            body = set_update_body(actual_object_type, attributes)
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
            if status:
                # Most collection manager types support status updates
                try:
                    await self.client._async_update_collection_status(guid, status)
                except Exception:
                    logger.debug(f"Status update not supported for {object_type}")
            
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
            actual_object_type = "Agreement" if object_type == "Data Sharing Agreement" else object_type
            body = set_create_body(actual_object_type, attributes)
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
                # Default classifications for Glossary if not specified
                body["initialClassifications"] = {
                    "Taxonomy": {"class": "TaxonomyProperties"},
                    "CanonicalVocabulary": {"class": "CanonicalVocabularyProperties"}
                }
            

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

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("CSV Element")

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
            return f"# Created CSV Element\n\nGUID: {guid}\nQualified Name: {qualified_name}"

        return self.command.raw_block

class CollectionLinkProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Agreement Items, Collection Membership, product dependencies, etc.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec(self.command.object_type)

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.canonical_object_type
        attributes = self.parsed_output["attributes"]
        
        if verb in ["Link", "Attach", "Add"]:
            body = set_rel_request_body(object_type, attributes)
            
            if "Agreement Item" in object_type or "Agreement to Item" in object_type:
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
                await self.client._async_link_agreement_item(guid1, guid2, body)
                
            elif "Agreement Actor" in object_type or "Agreement to Actor" in object_type:
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
                for guid_ac in actor_guids:
                    if guid_ac:
                        await self.client._async_link_agreement_actor(guid_ag, guid_ac, body)
                
            elif "Collection Member" in object_type or "Member to Collection" in object_type:
                guid_coll = attributes.get('Collection Id', {}).get('guid')
                guid_el = attributes.get('Element Id', {}).get('guid')
                body['properties'] = {
                    "class": "CollectionMembershipProperties",
                    "typeName": "CollectionMembership",
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
                
            elif "Product Dependency" in object_type:
                guid1 = attributes.get('Digital Product 1', {}).get('guid')
                guid2 = attributes.get('Digital Product 2', {}).get('guid')
                body['properties'] = {
                    "class": "DigitalProductDependencyProperties",
                    "typeName": "DigitalProductDependency",
                    "label": attributes.get('Label', {}).get('value'),
                    "description": attributes.get('Description', {}).get('value'),
                    "effectiveFrom": attributes.get('Effective From', {}).get('value'),
                    "effectiveTo": attributes.get('Effective To', {}).get('value')
                }
                await self.client._async_link_digital_product_dependency(guid1, guid2, body)
                
            elif "Attach Collection" in object_type:
                guid_coll = attributes.get('Collection Id', {}).get('guid')
                guid_res = attributes.get('Resource Id', {}).get('guid')
                body['properties'] = {
                    "class": "ResourceListProperties",
                    "typeName": "ResourceList",
                    "resourceUse": attributes.get('Resource Use', {}).get('value'),
                    "resourceDescription": attributes.get('Resource Description', {}).get('value'),
                    "resourceProperties": attributes.get('Resource Properties', {}).get('value'),
                    "effectiveFrom": attributes.get('Effective From', {}).get('value'),
                    "effectiveTo": attributes.get('Effective To', {}).get('value')
                }
                await self.client._async_attach_collection(guid_res, guid_coll, body)
                
            elif "Subscriber" in object_type:
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

            logger.success(f"Linked {object_type}")
            
            # Format the output with attributes for better feedback
            header = f"\n\n# {verb} {object_type}\n\nOperation completed.\n\n"
            if "Member to Collection" in object_type or "Collection Member" in object_type:
                header += "## Associated Elements\n"
                header += f"- **Collection Id**: `{attributes.get('Collection Id', {}).get('value')}`\n"
                header += f"- **Element Id**: `{attributes.get('Element Id', {}).get('value')}`\n\n"
            
            header += "## Link Properties\n"
            # Exclude standard command identifiers when dumping properties
            for k, v in attributes.items():
                if k not in ["Collection Id", "Element Id", "Digital Product 1", "Digital Product 2", "Subscriber Id", "Subscription", "Resource Id", "Agreement Name", "Item Name", "Qualified Name", "Display Name"]:
                    val = v.get("value")
                    if val:
                        header += f"- **{k}**: {val}\n"
            
            return header

        elif verb in ["Detach", "Unlink", "Remove"]:
            body = set_delete_rel_request_body(object_type, attributes)
            if "Agreement Item" in object_type or "Agreement to Item" in object_type:
                await self.client._async_detach_agreement_item(attributes.get('Agreement Name', {}).get('guid'), attributes.get('Item Name', {}).get('guid'), body)
            elif "Agreement Actor" in object_type or "Agreement to Actor" in object_type:
                guid_ag = attributes.get('Agreement Name', {}).get('guid')
                actor_data = attributes.get('Actors', {})
                actor_guids = actor_data.get('guid_list') or ([actor_data.get('guid')] if actor_data.get('guid') else [])
                for guid_ac in actor_guids:
                    if guid_ac:
                        await self.client._async_detach_agreement_actor(guid_ag, guid_ac, body)
            elif "Collection Membership" in object_type or "Collection Member" in object_type:
                await self.client._async_remove_from_collection(attributes.get('Collection Id', {}).get('guid'), attributes.get('Element Id', {}).get('guid'), body)
            elif "Product Dependency" in object_type:
                await self.client._async_detach_digital_product_dependency(attributes.get('Digital Product 1', {}).get('guid'), attributes.get('Digital Product 2', {}).get('guid'), body)
            elif "Attach Collection" in object_type or "Resource List" in object_type:
                await self.client._async_detach_collection(attributes.get('Resource Id', {}).get('guid'), attributes.get('Collection Id', {}).get('guid'), body)
            elif "Subscriber" in object_type:
                await self.client._async_detach_subscriber(attributes.get('Subscriber Id', {}).get('guid'), attributes.get('Subscription Id', {}).get('guid'), body)
                
            logger.success(f"Detached {object_type}")
            return f"\n\n# {verb} {object_type}\n\nOperation completed."

        return self.command.raw_block
