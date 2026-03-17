"""
Data Designer Processors for Dr.Egeria v2.
"""
from typing import Dict, Any, Optional, List
from loguru import logger

from pyegeria import EgeriaTech, PyegeriaException
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.v2.utils import parse_key_value
from md_processing.md_processing_utils.md_processing_constants import get_command_spec
from md_processing.md_processing_utils.common_md_utils import (
    set_element_prop_body, set_create_body, set_update_body, 
    set_rel_request_body, set_rel_prop_body, set_data_field_body,
    update_element_dictionary
)
from pyegeria.core.utils import body_slimmer

class DataCollectionProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Data Specifications and Data Dictionaries.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec(self.command.object_type)


    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.command.object_type
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        status = attributes.get('Status', {}).get('value', None)

        # 1. Map type
        mapped_type = "Collection"
        if "Specification" in object_type: 
            mapped_type = "DataSpec"
        elif "Dictionary" in object_type: 
            mapped_type = "DataDictionary"
            
        prop_body = set_element_prop_body(mapped_type, qualified_name, attributes)

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.original_text

            body = set_update_body(object_type, attributes)
            body['properties'] = prop_body
            
            await self.client._async_update_collection(guid, body)
            self.parsed_output["guid"] = guid
            if status:
                await self.client._async_update_collection_status(guid, status)
            
            logger.success(f"Updated {object_type} '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = set_create_body(object_type, attributes)
            body["properties"] = prop_body
            
            # Handle parent hierarchy if present
            parent_guid = body.get('parentGuid')
            if parent_guid:
                body['parentRelationshipTypeName'] = "CollectionMembership"
                body['parentAtEnd1'] = True

            guid = await self.client._async_create_collection(body=body)
            if guid:
                self.parsed_output["guid"] = guid
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created {object_type} '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.original_text

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_data_collection_by_guid(guid)
        except PyegeriaException:
            return None

class DataStructureProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Data Structures.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Data Structure")


    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        merge_update = attributes.get('Merge Update', {}).get('value', True)

        prop_body = set_element_prop_body("Data Structure", qualified_name, attributes)
        prop_body['namespace'] = attributes.get('Namespace', {}).get('value', None)
        
        # Collection memberships
        data_spec_guids = attributes.get("In Data Specification", {}).get("guid_list", [])
        data_dict_guids = attributes.get("In Data Dictionary", {}).get("guid_list", [])
        to_be_guids = set((data_spec_guids if isinstance(data_spec_guids, list) else [data_spec_guids]) + 
                          (data_dict_guids if isinstance(data_dict_guids, list) else [data_dict_guids]))
        to_be_guids = {g for g in to_be_guids if g}

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.original_text

            body = set_update_body("Data Structure", attributes)
            body['properties'] = prop_body
            await self.client._async_update_data_structure(guid, body)
            self.parsed_output["guid"] = guid
            
            await self._sync_memberships(guid, to_be_guids, not merge_update)
            
            logger.success(f"Updated Data Structure '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = set_create_body("Data Structure", attributes)
            body['properties'] = prop_body
            
            guid = await self.client._async_create_data_structure(body_slimmer(body))
            if guid:
                self.parsed_output["guid"] = guid
                await self._sync_memberships(guid, to_be_guids, replace_all=True)
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Data Structure '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.original_text

    async def _sync_memberships(self, guid: str, to_be_guids: set, replace_all: bool):
        # Fetch current memberships
        # This wrapper logic should be async
        memberships = await self.client._async_get_data_memberships(self.client._async_get_data_structure_by_guid, guid)
        as_is = set(memberships.get("DictList", [])) | set(memberships.get("SpecList", []))
        
        async def add_fn(coll_guid):
            await self.client._async_add_to_collection(coll_guid, guid)
            
        async def remove_fn(coll_guid):
            await self.client._async_remove_from_collection(coll_guid, guid)
            
        await self.sync_members(as_is, to_be_guids, add_fn, remove_fn, replace_all)

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_data_structure_by_guid(guid)
        except PyegeriaException:
            return None

class DataFieldProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Data Fields.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Data Field")


    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        merge_update = attributes.get('Merge Update', {}).get('value', False) # Default to false for fields?

        # 1. Properties
        props_body = set_data_field_body("Data Field", qualified_name, attributes)
        
        # 2. Relationships
        data_struct_guids = set(attributes.get('In Data Structure', {}).get('guid_list', []))
        parent_field_guids = set(attributes.get('Parent Data Field', {}).get('guid_list', []))
        term_guids = set(attributes.get('Glossary Term', {}).get('guid_list', []))
        if attributes.get('Glossary Term', {}).get('guid'):
            term_guids.add(attributes['Glossary Term']['guid'])
        data_class_guid = attributes.get('Data Class', {}).get('guid')
        data_dict_guids = set(attributes.get('In Data Dictionary', {}).get('guid_list', []))

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                 return self.command.original_text

            body = set_update_body("Data Field", attributes)
            body['properties'] = props_body
            await self.client._async_update_data_field(guid, body)
            self.parsed_output["guid"] = guid
            
            await self._sync_all_rels(guid, data_struct_guids, parent_field_guids, term_guids, data_class_guid, data_dict_guids, not merge_update)
            
            logger.success(f"Updated Data Field '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = set_create_body("Data Field", attributes)
            body['properties'] = props_body
            
            guid = await self.client._async_create_data_field(body)
            if guid:
                self.parsed_output["guid"] = guid
                await self._sync_all_rels(guid, data_struct_guids, parent_field_guids, term_guids, data_class_guid, data_dict_guids, replace_all=True)
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Data Field '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.original_text

    async def _sync_all_rels(self, guid: str, ds_guids: set, parent_guids: set, term_guids: set, dc_guid: str, dict_guids: set, replace_all: bool):
        """Unified relationship sync for Data Field."""
        # This is a complex sync involving multiple relationship types
        rel_els = await self.client._async_get_data_field_rel_elements(guid)
        
        # 1. Data Structures
        as_is_ds = set(rel_els.get("data_structure_guids", []))
        await self.sync_members(as_is_ds, ds_guids, 
                               lambda ds: self.client._async_link_member_data_field(ds, guid, None),
                               lambda ds: self.client._async_detach_member_data_field(ds, guid, None),
                               replace_all)
        
        # 2. Parent Fields
        as_is_parents = set(rel_els.get("parent_guids", []))
        await self.sync_members(as_is_parents, parent_guids,
                               lambda p: self.client._async_link_nested_data_field(p, guid, None),
                               lambda p: self.client._async_detach_nested_data_field(p, guid, None),
                               replace_all)
        
        # 3. Terms (Semantic Definitions)
        as_is_terms = set(rel_els.get("assigned_meanings_guids", []))
        await self.sync_members(as_is_terms, term_guids,
                               lambda t: self.client._async_link_semantic_definition(guid, t, None),
                               lambda t: self.client._async_detach_semantic_definition(guid, t, None),
                               replace_all)
                               
        # 4. Data Class
        as_is_dc = set(rel_els.get("data_class_guids", []))
        to_be_dc = {dc_guid} if dc_guid else set()
        await self.sync_members(as_is_dc, to_be_dc,
                               lambda dc: self.client._async_link_data_class_definition(guid, dc, None),
                               lambda dc: self.client._async_detach_data_class_definition(guid, dc, None),
                               replace_all)

        # 5. Data Dictionaries (Collections)
        memberships = await self.client._async_get_data_memberships(self.client._async_get_data_field_by_guid, guid)
        as_is_dicts = set(memberships.get("DictList", []))
        await self.sync_members(as_is_dicts, dict_guids,
                               lambda d: self.client._async_add_to_collection(d, guid),
                               lambda d: self.client._async_remove_from_collection(d, guid),
                               replace_all)

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_data_field_by_guid(guid)
        except PyegeriaException:
            return None

class DataClassProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Data Classes.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Data Class")


    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        merge_update = attributes.get('Merge Update', {}).get('value', True)

        # 1. Complex Property Body
        # (Leveraging the existing pattern from v1, but could be cleaner)
        props = {
            "class": "DataClassProperties",
            "qualifiedName": qualified_name,
            "displayName": display_name,
            "description": attributes.get('Description', {}).get('value'),
            "namespacePath": attributes.get('Namespace', {}).get('value'),
            "matchPropertyNames": attributes.get('Match Property Names', {}).get('value', []),
            "matchThreshold": attributes.get('Match Threshold', {}).get('value', 0),
            "specification": attributes.get('Specification', {}).get('value'),
            "specificationDetails": attributes.get('Specification Details', {}).get('value', {}),
            "dataType": attributes.get('Data Type', {}).get('value'),
            "allowsDuplicateValues": attributes.get('Allow Duplicates', {}).get('value', True),
            "isNullable": attributes.get('Is Nullable', {}).get('value', True),
            "defaultValue": attributes.get('Default Value', {}).get('value'),
            "averageValue": attributes.get('Average Value', {}).get('value'),
            "valueList": attributes.get('Value List', {}).get('value'),
            "valueRangeFrom": attributes.get('Value Range From', {}).get('value'),
            "valueRangeTo": attributes.get('Value Range To', {}).get('value'),
            "sampleValues": attributes.get('Sample Values', {}).get('value', []),
            "dataPatterns": attributes.get('Data Patterns', {}).get('value', []),
            "additionalProperties": attributes.get('Additional Properties', {}).get('value', {})
        }

        # 2. Relationships
        containing_dc_guids = set(attributes.get('Containing Data Class', {}).get('guid_list', []))
        term_guids = set(attributes.get('Glossary Term', {}).get('guid_list', []))
        if attributes.get('Glossary Term', {}).get('guid'):
            term_guids.add(attributes['Glossary Term']['guid'])
        specializes_dc_guids = set(attributes.get('Specializes Data Class', {}).get('guid_list', []))
        if attributes.get('Specializes Data Class', {}).get('guid'):
            specializes_dc_guids.add(attributes['Specializes Data Class']['guid'])
        data_dict_guids = set(attributes.get('In Data Dictionary', {}).get('guid_list', []))

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.original_text

            body = {"class": "UpdateElementRequestBody", "properties": props}
            await self.client._async_update_data_class(guid, body, not merge_update)
            self.parsed_output["guid"] = guid
            
            await self._sync_all_rels(guid, containing_dc_guids, term_guids, specializes_dc_guids, data_dict_guids, not merge_update)
            
            logger.success(f"Updated Data Class '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.client._async_get_data_class_by_guid(guid, None, 'MD')

        elif verb == "Create":
            body = {"class": "NewElementRequestBody", "properties": props}
            guid = await self.client._async_create_data_class(body)
            if guid:
                self.parsed_output["guid"] = guid
                await self._sync_all_rels(guid, containing_dc_guids, term_guids, specializes_dc_guids, data_dict_guids, replace_all=True)
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Data Class '{display_name}' with GUID {guid}")
                return await self.client._async_get_data_class_by_guid(guid, None, 'MD')

        return self.command.original_text

    async def _sync_all_rels(self, guid: str, cont_guids: set, term_guids: set, spec_guids: set, dict_guids: set, replace_all: bool):
        rel_els = await self.client._async_get_data_class_rel_elements(guid)
        
        # 1. Containing Classes
        as_is_cont = set(rel_els.get("nested_data_class_guids", []))
        await self.sync_members(as_is_cont, cont_guids,
                               lambda dc: self.client._async_link_nested_data_class(dc, guid),
                               lambda dc: self.client._async_detach_nested_data_class(dc, guid),
                               replace_all)
                               
        # 2. Terms
        as_is_terms = set(rel_els.get("assigned_meanings_guids", []))
        await self.sync_members(as_is_terms, term_guids,
                               lambda t: self.client._async_link_semantic_definition(guid, t),
                               lambda t: self.client._async_detach_semantic_definition(guid, t),
                               replace_all)
                               
        # 3. Specializes
        as_is_spec = set(rel_els.get("specialized_data_class_guids", []))
        await self.sync_members(as_is_spec, spec_guids,
                               lambda dc: self.client._async_link_specialist_data_class(dc, guid),
                               lambda dc: self.client._async_detach_specialist_data_class(dc, guid),
                               replace_all)

        # 4. Data Dictionaries
        memberships = await self.client._async_get_data_memberships(self.client._async_get_data_class_by_guid, guid)
        as_is_dicts = set(memberships.get("DictList", []))
        await self.sync_members(as_is_dicts, dict_guids,
                               lambda d: self.client._async_add_to_collection(d, guid),
                               lambda d: self.client._async_remove_from_collection(d, guid),
                               replace_all)

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_data_class_by_guid(guid)
        except PyegeriaException:
            return None
