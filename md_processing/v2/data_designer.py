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
    update_element_dictionary, async_add_note_in_dr_e
)
from pyegeria.core.utils import body_slimmer

# --- DataValueSpecificationProcessor ---
class DataValueSpecificationProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Data Value Specification create/update with upsert logic.
    """
    def get_command_spec(self) -> Dict[str, Any]:
        # Use the full normalized command (verb + object_type) for spec lookup
        return get_command_spec(f"{self.command.verb} {self.command.object_type}")

    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        merge_update = attributes.get('Merge Update', {}).get('value', True)
        journal_entry = attributes.get('Journal Entry', {}).get('value')

        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE") if spec else None

        # Build properties dict
        props = {
            "class": f"{om_type or 'DataValueSpecification'}Properties",
            "qualifiedName": qualified_name,
            "displayName": display_name,
            "description": attributes.get('Description', {}).get('value'),
            "namespacePath": attributes.get('Namespace Path', {}).get('value'),
            "matchPropertyNames": attributes.get('Match Property Names', {}).get('value', []),
            "matchThreshold": attributes.get('Match Threshold', {}).get('value', 0),
            "specification": attributes.get('Specification', {}).get('value'),
            "specificationDetails": attributes.get('Specification Details', {}).get('value', {}),
            "dataType": attributes.get('Data Type', {}).get('value'),
            "units": attributes.get('Units', {}).get('value'),
            "absoluteUncertainty": attributes.get('Absolute Uncertainty', {}).get('value'),
            "relativeUncertainty": attributes.get('Relative Uncertainty', {}).get('value'),
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

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block

            self.last_body = body = {"class": "UpdateElementRequestBody", "properties": props}
            await self.client.data_designer._async_update_data_value_specification(guid, body)
            self.parsed_output["guid"] = guid

            if journal_entry:
                try:
                    j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                    if j_guid:
                        self.add_related_result("Journal Entry", j_guid)
                except Exception as e:
                    self.add_related_result("Journal Entry", status="failure", message=str(e))

            logger.success(f"Updated Data Value Specification '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            self.last_body = body = {"class": "NewElementRequestBody", "properties": props}
            raw_guid = await self.client.data_designer._async_create_data_value_specification(body)
            guid = self.extract_guid_or_raise(raw_guid, "Create Data Value Specification")
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
                logger.success(f"Created Data Value Specification '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.raw_block

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client.data_designer._async_get_data_value_specification_by_guid(guid)
        except PyegeriaException:
            return None

class DataCollectionProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Data Specifications and Data Dictionaries.
    """


    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = getattr(self, 'canonical_object_type', self.command.object_type)
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        status = attributes.get('Status', {}).get('value', None)
        journal_entry = attributes.get('Journal Entry', {}).get('value')

        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")

        # 1. Map type
        mapped_type = om_type or "Collection"
        if not om_type:
            if "Specification" in object_type: 
                mapped_type = "DataSpec"
            elif "Dictionary" in object_type: 
                mapped_type = "DataDictionary"
            
        prop_body = set_element_prop_body(mapped_type, qualified_name, attributes)

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block

            self.last_body = body = set_update_body(om_type or object_type, attributes)
            body['properties'] = self.filter_update_properties(prop_body, body.get('mergeUpdate', True))
            
            await self.client.data_designer._async_update_collection(guid, body)
            self.parsed_output["guid"] = guid
            if status:
                await self.client.data_designer._async_update_collection_status(guid, status)

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
            self.last_body = body = set_create_body(om_type or object_type, attributes)
            body["properties"] = prop_body
            
            # Handle parent hierarchy if present
            parent_guid = body.get('parentGuid')
            if parent_guid:
                body['parentRelationshipTypeName'] = "CollectionMembership"
                body['parentAtEnd1'] = True

            raw_guid = await self.client.data_designer._async_create_collection(body=body)
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

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client.data_designer._async_get_data_collection_by_guid(guid)
        except PyegeriaException:
            return None

class DataStructureProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Data Structures.
    """


    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        merge_update = attributes.get('Merge Update', {}).get('value', True)
        journal_entry = attributes.get('Journal Entry', {}).get('value')

        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")

        prop_body = set_element_prop_body(om_type or "Data Structure", qualified_name, attributes)
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
                return self.command.raw_block

            self.last_body = body = set_update_body(om_type or "Data Structure", attributes)
            body['properties'] = self.filter_update_properties(prop_body, body.get('mergeUpdate', True))
            await self.client.data_designer._async_update_data_structure(guid, body)
            self.parsed_output["guid"] = guid
            
            await self._sync_memberships(guid, to_be_guids, not merge_update)
            
            if journal_entry:
                try:
                    j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                    if j_guid:
                        self.add_related_result("Journal Entry", j_guid)
                except Exception as e:
                    self.add_related_result("Journal Entry", status="failure", message=str(e))

            logger.success(f"Updated Data Structure '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            self.last_body = body = set_create_body("Data Structure", attributes)
            body['properties'] = prop_body
            
            raw_guid = await self.client.data_designer._async_create_data_structure(body_slimmer(body))
            guid = self.extract_guid_or_raise(raw_guid, "Create Data Structure")
            if guid:
                self.parsed_output["guid"] = guid
                await self._sync_memberships(guid, to_be_guids, replace_all=True)

                if journal_entry:
                    try:
                        j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                        if j_guid:
                            self.add_related_result("Journal Entry", j_guid)
                    except Exception as e:
                        self.add_related_result("Journal Entry", status="failure", message=str(e))

                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Data Structure '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.raw_block

    async def _sync_memberships(self, guid: str, to_be_guids: set, replace_all: bool):
        # Fetch current memberships
        # This wrapper logic should be async
        memberships = await self._extract_memberships_async(
            self.client.data_designer._async_get_data_structure_by_guid, guid)
        as_is = set(memberships.get("DictList", [])) | set(memberships.get("SpecList", []))
        
        async def add_fn(coll_guid):
            await self.client.collection_manager._async_add_to_collection(coll_guid, guid)

        async def remove_fn(coll_guid):
            await self.client.collection_manager._async_remove_from_collection(coll_guid, guid)

        sync_res = await self.sync_members(as_is, to_be_guids, add_fn, remove_fn, replace_all)
        if sync_res.get("added") or sync_res.get("removed"):
            self.add_related_result("Collection Memberships Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
        if sync_res.get("errors"):
            self.add_related_result("Collection Memberships Sync", status="failure", message="; ".join(sync_res["errors"]))

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client.data_designer._async_get_data_structure_by_guid(guid)
        except PyegeriaException:
            return None

class DataFieldProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Data Fields.
    """


    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        merge_update = attributes.get('Merge Update', {}).get('value', False) # Default to false for fields?
        journal_entry = attributes.get('Journal Entry', {}).get('value')

        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")

        # 1. Properties
        props_body = set_data_field_body(om_type or "Data Field", qualified_name, attributes)
        
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
                return self.command.raw_block

            self.last_body = body = set_update_body(om_type or "Data Field", attributes)
            body['properties'] = self.filter_update_properties(props_body, body.get('mergeUpdate', True))
            await self.client.data_designer._async_update_data_field(guid, body)
            self.parsed_output["guid"] = guid
            
            await self._sync_all_rels(guid, data_struct_guids, parent_field_guids, term_guids, data_class_guid, data_dict_guids, not merge_update)
            
            if journal_entry:
                try:
                    j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                    if j_guid:
                        self.add_related_result("Journal Entry", j_guid)
                except Exception as e:
                    self.add_related_result("Journal Entry", status="failure", message=str(e))

            logger.success(f"Updated Data Field '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            self.last_body = body = set_create_body(om_type or "Data Field", attributes)
            body['properties'] = props_body
            
            raw_guid = await self.client.data_designer._async_create_data_field(body)
            guid = self.extract_guid_or_raise(raw_guid, "Create Data Field")
            if guid:
                self.parsed_output["guid"] = guid
                await self._sync_all_rels(guid, data_struct_guids, parent_field_guids, term_guids, data_class_guid, data_dict_guids, replace_all=True)

                if journal_entry:
                    try:
                        j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                        if j_guid:
                            self.add_related_result("Journal Entry", j_guid)
                    except Exception as e:
                        self.add_related_result("Journal Entry", status="failure", message=str(e))

                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Data Field '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.raw_block

    async def _sync_all_rels(self, guid: str, ds_guids: set, parent_guids: set, term_guids: set, dc_guid: str, dict_guids: set, replace_all: bool):
        """Unified relationship sync for Data Field."""
        # This is a complex sync involving multiple relationship types
        rel_els = await self.client.data_designer._async_get_data_field_rel_elements(guid)

        # 1. Data Structures
        as_is_ds = set(rel_els.get("data_structure_guids", []))
        sync_res = await self.sync_members(as_is_ds, ds_guids, 
                               lambda ds: self.client.data_designer._async_link_member_data_field(ds, guid, None),
                               lambda ds: self.client.data_designer._async_detach_member_data_field(ds, guid, None),
                               replace_all)
        if sync_res.get("added") or sync_res.get("removed"):
            self.add_related_result("Data Structures Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
        if sync_res.get("errors"):
            self.add_related_result("Data Structures Sync", status="failure", message="; ".join(sync_res["errors"]))
        
        # 2. Parent Fields
        as_is_parents = set(rel_els.get("parent_guids", []))
        sync_res = await self.sync_members(as_is_parents, parent_guids,
                               lambda p: self.client.data_designer._async_link_nested_data_field(p, guid, None),
                               lambda p: self.client.data_designer._async_detach_nested_data_field(p, guid, None),
                               replace_all)
        if sync_res.get("added") or sync_res.get("removed"):
            self.add_related_result("Parent Fields Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
        if sync_res.get("errors"):
            self.add_related_result("Parent Fields Sync", status="failure", message="; ".join(sync_res["errors"]))
        
        # 3. Terms (Semantic Definitions)
        as_is_terms = set(rel_els.get("assigned_meanings_guids", []))
        sync_res = await self.sync_members(as_is_terms, term_guids,
                               lambda t: self.client.data_designer._async_link_semantic_definition(guid, t, None),
                               lambda t: self.client.data_designer._async_detach_semantic_definition(guid, t, None),
                               replace_all)
        if sync_res.get("added") or sync_res.get("removed"):
            self.add_related_result("Semantic Definitions Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
        if sync_res.get("errors"):
            self.add_related_result("Semantic Definitions Sync", status="failure", message="; ".join(sync_res["errors"]))
                               
        # 4. Data Class
        as_is_dc = set(rel_els.get("data_class_guids", []))
        to_be_dc = {dc_guid} if dc_guid else set()
        sync_res = await self.sync_members(as_is_dc, to_be_dc,
                               lambda dc: self.client.data_designer._async_link_data_class_definition(guid, dc, None),
                               lambda dc: self.client.data_designer._async_detach_data_class_definition(guid, dc, None),
                               replace_all)
        if sync_res.get("added") or sync_res.get("removed"):
            self.add_related_result("Data Class Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
        if sync_res.get("errors"):
            self.add_related_result("Data Class Sync", status="failure", message="; ".join(sync_res["errors"]))

        # 5. Data Dictionaries (Collections)
        memberships = await self._extract_memberships_async(
            self.client.data_designer._async_get_data_field_by_guid, guid)
        as_is_dicts = set(memberships.get("DictList", []))
        sync_res = await self.sync_members(as_is_dicts, dict_guids,
                               lambda d: self.client.collection_manager._async_add_to_collection(d, guid),
                               lambda d: self.client.collection_manager._async_remove_from_collection(d, guid),
                               replace_all)
        if sync_res.get("added") or sync_res.get("removed"):
            self.add_related_result("Data Dictionaries Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
        if sync_res.get("errors"):
            self.add_related_result("Data Dictionaries Sync", status="failure", message="; ".join(sync_res["errors"]))

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client.data_designer._async_get_data_field_by_guid(guid)
        except PyegeriaException:
            return None

class DataClassProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Data Classes.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        # Use the full normalized command (verb + object_type) for spec lookup
        return get_command_spec(f"{self.command.verb} {self.command.object_type}")


    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        merge_update = attributes.get('Merge Update', {}).get('value', True)
        journal_entry = attributes.get('Journal Entry', {}).get('value')

        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")

        # 1. Complex Property Body
        # (Leveraging the existing pattern from v1, but could be cleaner)
        props = {
            "class": f"{om_type or 'DataClass'}Properties",
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
                return self.command.raw_block

            self.last_body = body = {"class": "UpdateElementRequestBody", "properties": props}
            await self.client.data_designer._async_update_data_value_specification(guid, body)
            self.parsed_output["guid"] = guid
            
            await self._sync_all_rels(guid, containing_dc_guids, term_guids, specializes_dc_guids, data_dict_guids, not merge_update)
            
            if journal_entry:
                try:
                    j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                    if j_guid:
                        self.add_related_result("Journal Entry", j_guid)
                except Exception as e:
                    self.add_related_result("Journal Entry", status="failure", message=str(e))

            logger.success(f"Updated Data Class '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            self.last_body = body = {"class": "NewElementRequestBody", "properties": props}
            raw_guid = await self.client.data_designer._async_create_data_class(body)
            guid = self.extract_guid_or_raise(raw_guid, "Create Data Class")
            if guid:
                self.parsed_output["guid"] = guid
                await self._sync_all_rels(guid, containing_dc_guids, term_guids, specializes_dc_guids, data_dict_guids, replace_all=True)

                if journal_entry:
                    try:
                        j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                        if j_guid:
                            self.add_related_result("Journal Entry", j_guid)
                    except Exception as e:
                        self.add_related_result("Journal Entry", status="failure", message=str(e))

                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Data Class '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.raw_block

    async def _sync_all_rels(self, guid: str, cont_guids: set, term_guids: set, spec_guids: set, dict_guids: set, replace_all: bool):
        rel_els = self.client.data_designer.get_data_class_rel_elements(guid) or {}
        
        # 1. Containing Classes
        as_is_cont = set(rel_els.get("nested_data_class_guids", []))
        sync_res = await self.sync_members(as_is_cont, cont_guids,
                               lambda dc: self.client.data_designer._async_link_nested_data_class(dc, guid, None),
                               lambda dc: self.client.data_designer._async_detach_nested_data_class(dc, guid, None),
                               replace_all)
        if sync_res.get("added") or sync_res.get("removed"):
            self.add_related_result("Containing Classes Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
        if sync_res.get("errors"):
            self.add_related_result("Containing Classes Sync", status="failure", message="; ".join(sync_res["errors"]))
                               
        # 2. Terms
        as_is_terms = set(rel_els.get("assigned_meanings_guids", []))
        sync_res = await self.sync_members(as_is_terms, term_guids,
                               lambda t: self.client.data_designer._async_link_semantic_definition(guid, t),
                               lambda t: self.client.data_designer._async_detach_semantic_definition(guid, t),
                               replace_all)
        if sync_res.get("added") or sync_res.get("removed"):
            self.add_related_result("Semantic Definitions Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
        if sync_res.get("errors"):
            self.add_related_result("Semantic Definitions Sync", status="failure", message="; ".join(sync_res["errors"]))
                               
        # 3. Specializes
        as_is_spec = set(rel_els.get("specialized_data_class_guids", []))
        sync_res = await self.sync_members(as_is_spec, spec_guids,
                               lambda dc: self.client.data_designer._async_link_specialist_data_class(dc, guid, None),
                               lambda dc: self.client.data_designer._async_detach_specialist_data_class(dc, guid, None),
                               replace_all)
        if sync_res.get("added") or sync_res.get("removed"):
            self.add_related_result("Specializes Classes Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
        if sync_res.get("errors"):
            self.add_related_result("Specializes Classes Sync", status="failure", message="; ".join(sync_res["errors"]))

        # 4. Data Dictionaries
        memberships = await self._extract_memberships_async(
            self.client.data_designer._async_get_data_class_by_guid, guid)
        as_is_dicts = set(memberships.get("DictList", []))
        sync_res = await self.sync_members(as_is_dicts, dict_guids,
                               lambda d: self.client.collection_manager._async_add_to_collection(d, guid),
                               lambda d: self.client.collection_manager._async_remove_from_collection(d, guid),
                               replace_all)
        if sync_res.get("added") or sync_res.get("removed"):
            self.add_related_result("Data Dictionaries Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
        if sync_res.get("errors"):
            self.add_related_result("Data Dictionaries Sync", status="failure", message="; ".join(sync_res["errors"]))

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client.data_designer._async_get_data_class_by_guid(guid)
        except PyegeriaException:
            return None

class DataGrainProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Data Grains.
    """


    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        journal_entry = attributes.get('Journal Entry', {}).get('value')

        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")

        props_body = set_element_prop_body(om_type or "Data Grain", qualified_name, attributes)

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block

            self.last_body = body = set_update_body(om_type or "Data Grain", attributes)
            body['properties'] = self.filter_update_properties(props_body, body.get('mergeUpdate', True))
            await self.client.data_designer._async_update_data_value_specification(guid, body)
            self.parsed_output["guid"] = guid

            if journal_entry:
                try:
                    j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                    if j_guid:
                        self.add_related_result("Journal Entry", j_guid)
                except Exception as e:
                    self.add_related_result("Journal Entry", status="failure", message=str(e))

            logger.success(f"Updated Data Grain '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            self.last_body = body = set_create_body(om_type or "Data Grain", attributes)
            body['properties'] = props_body

            raw_guid = await self.client.data_designer._async_create_data_grain(body)
            guid = self.extract_guid_or_raise(raw_guid, "Create Data Grain")
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
                logger.success(f"Created Data Grain '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.raw_block

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client.data_designer._async_get_data_value_specification_by_guid(guid, element_type="DataGrain")
        except PyegeriaException:
            return None


class LinkDataFieldProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Link Data Field commands.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Link Data Field")

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        field1_guid = attributes.get('Linked Data Field 1', {}).get('guid')
        field2_guid = attributes.get('Linked Data Field 2', {}).get('guid')
        rel_type = attributes.get('Link Relationship Type Name', {}).get('value')
        description = attributes.get('Description', {}).get('value')

        if not field1_guid or not field2_guid:
            logger.error("Both Linked Data Field 1 and Linked Data Field 2 are required")
            return self.command.raw_block

        try:
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "NestedDataFieldProperties"
                }
            }
            if rel_type:
                body['properties']['linkRelationshipTypeName'] = rel_type

            await self.client.data_designer._async_link_nested_data_field(field1_guid, field2_guid, body)
            logger.success(f"Linked Data Fields with relationship type '{rel_type or 'default'}'")
            return "Link created successfully"
        except Exception as e:
            logger.error(f"Error linking data fields: {e}")
            return self.command.raw_block

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        return None


class LinkFieldToStructureProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Link Field to Structure commands (MemberDataField).
    """


    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        field_guid = attributes.get('Data Field', {}).get('guid')
        struct_guid = attributes.get('Data Structure', {}).get('guid')
        description = attributes.get('Description', {}).get('value')

        if not field_guid or not struct_guid:
            logger.error("Both Data Field and Data Structure are required")
            return self.command.raw_block

        try:
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "MemberDataFieldProperties"
                }
            }

            await self.client.data_designer._async_link_member_data_field(struct_guid, field_guid, body)
            logger.success(f"Linked Data Field to Data Structure")
            return "Link created successfully"
        except Exception as e:
            logger.error(f"Error linking field to structure: {e}")
            return self.command.raw_block

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        return None


class LinkDataValueDefinitionProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Link Data Value Definition commands.
    """


    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        spec_guid = attributes.get('Data Value Specification', {}).get('guid')
        elem_guid = attributes.get('Element Id', {}).get('guid')
        description = attributes.get('Description', {}).get('value')

        if not spec_guid or not elem_guid:
            logger.error("Both Data Value Specification and Element Id are required")
            return self.command.raw_block

        try:
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "DataValueDefinitionProperties"
                }
            }

            await self.client.data_designer._async_link_data_value_assignment(elem_guid, spec_guid, body)
            logger.success(f"Linked Data Value Definition")
            return "Link created successfully"
        except Exception as e:
            logger.error(f"Error linking data value definition: {e}")
            return self.command.raw_block

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        return None


class LinkDataValueCompositionProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Link Data Value Composition commands.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Link Data Value Composition")

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        parent_spec_guid = attributes.get('Data Value Specification', {}).get('guid')
        child_spec_guid = attributes.get('Data Value Specification Child', {}).get('guid')
        description = attributes.get('Description', {}).get('value')

        if not parent_spec_guid or not child_spec_guid:
            logger.error("Both Data Value Specification (parent) and Child are required")
            return self.command.raw_block

        try:
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "DataValueHierarchyProperties"
                }
            }

            await self.client.data_designer._async_link_specialized_data_value_specification(
                parent_spec_guid, child_spec_guid, body)
            logger.success(f"Linked Data Value Composition (parent to child)")
            return "Link created successfully"
        except Exception as e:
            logger.error(f"Error linking data value composition: {e}")
            return self.command.raw_block

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        return None


class LinkDataClassCompositionProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Link Data Class Composition commands.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Link Data Class Composition")

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        parent_dc_guid = attributes.get('Data Class', {}).get('guid')
        child_dc_guid = attributes.get('Data Class Child', {}).get('guid')
        description = attributes.get('Description', {}).get('value')

        if not parent_dc_guid or not child_dc_guid:
            logger.error("Both Data Class (parent) and Child are required")
            return self.command.raw_block

        try:
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "DataClassCompositionProperties"
                }
            }

            await self.client.data_designer._async_link_nested_data_class(parent_dc_guid, child_dc_guid, body)
            logger.success(f"Linked Data Class Composition (parent to child)")
            return "Link created successfully"
        except Exception as e:
            logger.error(f"Error linking data class composition: {e}")
            return self.command.raw_block

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        return None


class LinkCertificationTypeToStructureProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Link Certification Type to Data Structure commands.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Link Certification Type to Data Structure")

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        struct_guid = attributes.get('Data Structure', {}).get('guid')
        cert_type_guid = attributes.get('Certification Type', {}).get('guid')
        description = attributes.get('Description', {}).get('value')

        if not struct_guid or not cert_type_guid:
            logger.error("Both Data Structure and Certification Type are required")
            return self.command.raw_block

        try:
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "DataStructureDefinitionProperties"
                }
            }

            await self.client.data_designer._async_link_certification_type_to_data_structure(
                cert_type_guid, struct_guid, body)
            logger.success(f"Linked Certification Type to Data Structure")
            return "Link created successfully"
        except Exception as e:
            logger.error(f"Error linking certification type to structure: {e}")
            return self.command.raw_block

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        return None


class AttachDataDescriptionProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Attach Data Description to Element commands.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Attach Data Description to Element")

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        coll_guid = attributes.get('Collection Id', {}).get('guid')
        elem_guid = attributes.get('Element Id', {}).get('guid')
        description = attributes.get('Description', {}).get('value')

        if not coll_guid or not elem_guid:
            logger.error("Both Collection Id and Element Id are required")
            return self.command.raw_block

        try:
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "DataDescriptionProperties"
                }
            }

            await self.client.collection_manager._async_attach_data_description(elem_guid, coll_guid, body)
            logger.success(f"Attached Data Description to Element")
            return "Link created successfully"
        except Exception as e:
            logger.error(f"Error attaching data description: {e}")
            return self.command.raw_block

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        return None


class AssignDataValueSpecificationProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Assign/Attach Data Value Specification to Element commands.
    """
    def get_command_spec(self) -> Dict[str, Any]:
        # Use the full normalized command (verb + object_type) for spec lookup
        return get_command_spec(f"{self.command.verb} {self.command.object_type}")

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        spec_guid = attributes.get('Data Value Specification', {}).get('guid')
        elem_guid = attributes.get('Element Id', {}).get('guid')
        description = attributes.get('Description', {}).get('value')

        if not spec_guid or not elem_guid:
            logger.error("Both Data Value Specification and Element Id are required")
            return self.command.raw_block

        # Upsert logic: check if assignment already exists
        exists = False
        try:
            # Try to fetch existing assignments for this element
            rels = []  # TODO: implement get_data_value_assignments_for_element when SDK supports it
            if rels and isinstance(rels, list):
                for rel in rels:
                    rel_props = rel.get('relationshipProperties', {})
                    rel_spec_guid = rel_props.get('dataValueSpecificationGUID') or rel_props.get('specificationGUID')
                    if rel_spec_guid == spec_guid:
                        exists = True
                        break
        except Exception as e:
            logger.warning(f"Could not check for existing Data Value Assignment: {e}")

        if exists:
            logger.info(f"Assignment already exists for element {elem_guid} and spec {spec_guid}. Skipping create.")
            return "Assignment already exists. No action taken."

        try:
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "DataValueAssignmentProperties"
                }
            }
            if description:
                body['properties']['description'] = description

            await self.client.data_designer._async_link_data_value_assignment(elem_guid, spec_guid, body)
            logger.success(f"Assigned Data Value Specification {spec_guid} to element {elem_guid}")
            return "Assignment created successfully"
        except Exception as e:
            logger.error(f"Error assigning data value specification: {e}")
            return self.command.raw_block

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        return None


class AttachDataValueSpecificationProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Attach Data Value Specification to Element commands.
    Follows the same pattern as AssignDataValueSpecificationProcessor.
    """
    def get_command_spec(self) -> Dict[str, Any]:
        # Use the full normalized command (verb + object_type) for spec lookup
        return get_command_spec(f"{self.command.verb} {self.command.object_type}")

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        spec_guid = attributes.get('Data Value Specification', {}).get('guid')
        elem_guid = attributes.get('Element Id', {}).get('guid')
        description = attributes.get('Description', {}).get('value')

        if not spec_guid or not elem_guid:
            logger.error("Both Data Value Specification and Element Id are required")
            return self.command.raw_block

        # Upsert logic: check if attachment already exists
        exists = False
        try:
            rels = []  # TODO: implement get_data_value_assignments_for_element when SDK supports it
            if rels and isinstance(rels, list):
                for rel in rels:
                    rel_props = rel.get('relationshipProperties', {})
                    rel_spec_guid = rel_props.get('dataValueSpecificationGUID') or rel_props.get('specificationGUID')
                    if rel_spec_guid == spec_guid:
                        exists = True
                        break
        except Exception as e:
            logger.warning(f"Could not check for existing Data Value Assignment: {e}")

        if exists:
            logger.info(f"Attachment already exists for element {elem_guid} and spec {spec_guid}. Skipping create.")
            return "Assignment already exists. No action taken."

        try:
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "DataValueAssignmentProperties"
                }
            }
            if description:
                body['properties']['description'] = description

            await self.client.data_designer._async_link_data_value_assignment(elem_guid, spec_guid, body)
            logger.success(f"Attached Data Value Specification {spec_guid} to element {elem_guid}")
            return "Assignment created successfully"
        except Exception as e:
            logger.error(f"Error attaching data value specification: {e}")
            return self.command.raw_block

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        return None

