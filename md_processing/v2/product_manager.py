"""
Product Manager Processors for Dr.Egeria v2.
"""
from typing import Dict, Any, Optional, List
from loguru import logger
import json

from pyegeria import EgeriaTech, PyegeriaException
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.md_processing_constants import get_command_spec
from md_processing.md_processing_utils.common_md_utils import (
    set_element_prop_body, set_create_body, set_update_body, 
    set_object_classifications, update_element_dictionary,
    set_product_body, set_rel_request_body, set_delete_request_body
)
from pyegeria.core.utils import body_slimmer

class CollectionProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Collections (Folders, Root Collections).
    """

    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        status = attributes.get('Status', {}).get('value', 'ACTIVE')

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.original_text

            body = set_update_body("Collection", attributes)
            body['properties'] = set_element_prop_body("Collection", qualified_name, attributes)
            
            await self.client._async_update_collection(guid, body)
            self.parsed_output["guid"] = guid
            if status:
                await self.client._async_update_collection_status(guid, status)
            
            logger.success(f"Updated Collection '{display_name}'")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.client._async_get_collection_by_guid(guid, element_type="Collection", output_format='MD')

        elif verb == "Create":
            body = set_create_body(self.command.object_type, attributes)
            # Only add classifications if they are not already implied by the object type (like Folder or RootCollection)
            classifications = ["Folder", "Root Collection"]
            if self.command.object_type in ["Folder", "RootCollection", "Root Collection"]:
                classifications = []
                
            body["initialClassifications"] = set_object_classifications(self.command.object_type, attributes, classifications)
            body["properties"] = set_element_prop_body("Collection", qualified_name, attributes)
            
            parent_guid = body.get('parentGuid')
            if parent_guid:
                body['parentRelationshipTypeName'] = "CollectionMembership"
                body['parentAtEnd1'] = True

            guid = await self.client._async_create_collection(body=body)
            if guid:
                self.parsed_output["guid"] = guid
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Collection '{display_name}'")
                return await self.client._async_get_collection_by_guid(guid, output_format='MD')

        return self.command.original_text

class ProductProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Digital Products.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Digital Product")

    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        
        prop_body = set_product_body(self.command.object_type, qualified_name, attributes)

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.original_text

            body = set_update_body("Digital Product", attributes)
            body['properties'] = prop_body
            await self.client._async_update_digital_product(guid, body)
            self.parsed_output["guid"] = guid
            
            logger.success(f"Updated Product '{display_name}'")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.client._async_get_collection_by_guid(guid, element_type='Digital Product', output_format='MD')

        elif verb == "Create":
            body = set_create_body(self.command.object_type, attributes)
            body["properties"] = prop_body
            
            guid = await self.client._async_create_digital_product(body_slimmer(body))
            if guid:
                self.parsed_output["guid"] = guid
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Product '{display_name}'")
                return await self.client._async_get_collection_by_guid(guid, element_type='Digital Product', output_format='MD')

        return self.command.original_text

class AgreementProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Agreements (Data Sharing Agreements).
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Agreement")

    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.original_text

            body = set_update_body(self.command.object_type, attributes)
            body['properties'] = set_element_prop_body(self.command.object_type, qualified_name, attributes)
            await self.client._async_update_agreement(guid, body)
            self.parsed_output["guid"] = guid
            
            logger.success(f"Updated Agreement '{display_name}'")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.client._async_get_collection_by_guid(guid, element_type=self.command.object_type, output_format='MD')

        elif verb == "Create":
            body = set_create_body(self.command.object_type, attributes)
            body["initialClassifications"] = set_object_classifications(self.command.object_type, attributes, ["Data Sharing Agreement"])
            body["properties"] = set_element_prop_body("Agreement", qualified_name, attributes)
            
            guid = await self.client._async_create_agreement(body=body)
            if guid:
                self.parsed_output["guid"] = guid
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Agreement '{display_name}'")
                return await self.client._async_get_collection_by_guid(guid, element_type=self.command.object_type, output_format='MD')

        return self.command.original_text

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
            return self.command.original_text
            
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        
        guid = await self.client._async_get_create_csv_data_file_element_from_template(
            attributes.get('File Name', {}).get('value'),
            attributes.get('File Type', {}).get('value'),
            attributes.get('File Path', {}).get('value'),
            attributes.get('Version Identifier', {}).get('value'),
            attributes.get('File Encoding', {}).get('value', 'UTF-8'),
            attributes.get('File Extension', {}).get('value', 'csv'),
            attributes.get('File System Name', {}).get('value'),
            attributes.get('Description', {}).get('value')
        )

        if guid:
            self.parsed_output["guid"] = guid
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            logger.success(f"Created CSV Element '{display_name}'")
            return f"# Created CSV Element\n\nGUID: {guid}\nQualified Name: {qualified_name}"

        return self.command.original_text

class ProductLinkProcessor(AsyncBaseCommandProcessor):
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
            
            if "Agreement Item" in object_type:
                guid1 = attributes.get('Agreement Name', {}).get('guid')
                guid2 = attributes.get('Item Name', {}).get('guid')
                body['properties'] = {
                    "class": "AgreementItemProperties",
                    "agreementItemId": attributes.get("Agreement Item Id", {}).get("value"),
                    "agreementItemTypeName": attributes.get("Agreement Item Type", {}).get("value"),
                    "agreementStart": attributes.get("Agreement Start", {}).get("value"),
                    "agreementEnd": attributes.get("Agreement End", {}).get("value"),
                    "restrictions": attributes.get("Restrictions", {}).get("value"),
                    "obligations": attributes.get("Obligations", {}).get("value"),
                    "entitlements": attributes.get("Entitlements", {}).get("value"),
                    "usageMeasurements": attributes.get("Usage Measurements", {}).get("value"),
                    "effectiveFrom": attributes.get("Effective From", {}).get("value"),
                    "effectiveTo": attributes.get("Effective To", {}).get("value")
                }
                await self.client._async_link_agreement_item(guid1, guid2, body)
                
            elif "Collection Member" in object_type:
                guid_coll = attributes.get('Collection Id', {}).get('guid')
                guid_el = attributes.get('Element Id', {}).get('guid')
                body['properties'] = {
                    "class": "CollectionMembershipProperties",
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
                guid1 = attributes.get('Digital Product 1')
                guid2 = attributes.get('Digital Product 2')
                body['properties'] = {
                    "class": "DigitalProductDependencyProperties",
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
                    "resourceUse": attributes.get('Resource Use', {}).get('value'),
                    "resourceDescription": attributes.get('Resource Description', {}).get('value'),
                    "resourceProperties": attributes.get('Resource Properties', {}).get('value'),
                    "effectiveFrom": attributes.get('Effective From', {}).get('value'),
                    "effectiveTo": attributes.get('Effective To', {}).get('value')
                }
                await self.client._async_attach_collection(guid_res, guid_coll, body)
                
            elif "Subscriber" in object_type:
                guid_sub = attributes.get('Subscriber Id', {}).get('guid')
                guid_sn = attributes.get('Subscription', {}).get('guid')
                body['properties'] = {
                    "class": "DigitalSubscriberProperties",
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
            body = set_delete_request_body(object_type, attributes)
            if "Agreement Item" in object_type:
                await self.client._async_detach_agreement_item(attributes.get('Agreement Name', {}).get('guid'), attributes.get('Item Name', {}).get('guid'), body)
            elif "Collection Membership" in object_type or "Collection Member" in object_type:
                await self.client._async_remove_from_collection(attributes.get('Collection Id', {}).get('guid'), attributes.get('Element Id', {}).get('guid'), body)
            elif "Product Dependency" in object_type:
                await self.client._async_detach_digital_product_dependency(attributes.get('Digital Product 1'), attributes.get('Digital Product 2'), body)
            elif "Attach Collection" in object_type or "Resource List" in object_type:
                await self.client._async_detach_collection(attributes.get('Resource Id', {}).get('guid'), attributes.get('Collection Id', {}).get('guid'), body)
            elif "Subscriber" in object_type:
                await self.client._async_detach_subscriber(attributes.get('Subscriber Id', {}).get('guid'), attributes.get('Subscription', {}).get('guid'), body)
                
            logger.success(f"Detached {object_type}")
            return f"\n\n# {verb} {object_type}\n\nOperation completed."

        return self.command.original_text
