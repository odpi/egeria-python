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
    set_delete_rel_request_body,
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

        # "In Data Value Specification"/"Specializes Data Value Specification"
        # both describe the same DataValueHierarchy parent -- near-synonym
        # descriptions in the compact spec, treated as aliases of one
        # relationship (see PYEGERIA_ISSUES.md ISSUE-101 follow-up).
        value_spec_parent_guids = set(attributes.get('In Data Value Specification', {}).get('guid_list', []))
        if attributes.get('In Data Value Specification', {}).get('guid'):
            value_spec_parent_guids.add(attributes['In Data Value Specification']['guid'])
        value_spec_parent_guids |= set(attributes.get('Specializes Data Value Specification', {}).get('guid_list', []))
        if attributes.get('Specializes Data Value Specification', {}).get('guid'):
            value_spec_parent_guids.add(attributes['Specializes Data Value Specification']['guid'])

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block

            self.last_body = body = {"class": "UpdateElementRequestBody", "properties": props}
            await self.client.data_designer._async_update_data_value_specification(guid, body)
            self.parsed_output["guid"] = guid

            await self._sync_value_spec_parent(guid, value_spec_parent_guids, replace_all=True)

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

                await self._sync_value_spec_parent(guid, value_spec_parent_guids, replace_all=True, known_new=True)

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

    async def _sync_value_spec_parent(self, guid: str, to_be_guids: set, replace_all: bool, known_new: bool = False):
        """Sync this element's DataValueHierarchy parent(s)."""
        if known_new:
            as_is = set()
        else:
            rel_els = await self.client.data_designer._async_get_data_value_specification_rel_elements(guid) or {}
            as_is = set(rel_els.get("specialized_data_value_spec_guids", []))
        sync_res = await self.sync_members(as_is, to_be_guids,
                               lambda p: self.client.data_designer._async_link_specialized_data_value_specification(p, guid, None),
                               lambda p: self.client.data_designer._async_detach_specialized_data_value_specification(p, guid, None),
                               replace_all)
        if sync_res.get("added") or sync_res.get("removed"):
            self.add_related_result("Data Value Specification Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
        if sync_res.get("errors"):
            self.add_related_result("Data Value Specification Sync", status="failure", message="; ".join(sync_res["errors"]))

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
        prop_body['namespacePath'] = attributes.get('Namespace Path', {}).get('value', None)
        prop_body['namePatterns'] = attributes.get('Name Patterns', {}).get('value', None)
        
        # Collection memberships
        in_data_spec = attributes.get("In Data Specification", {})
        data_spec_guids = in_data_spec.get("guid_list") or ([in_data_spec["guid"]] if in_data_spec.get("guid") else [])
        in_data_dict = attributes.get("In Data Dictionary", {})
        data_dict_guids = in_data_dict.get("guid_list") or ([in_data_dict["guid"]] if in_data_dict.get("guid") else [])
        to_be_guids = {g for g in (data_spec_guids + data_dict_guids) if g}

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
                # known_new=True: this GUID was just created, so it cannot have
                # any existing memberships yet -- skip the as-is fetch.
                await self._sync_memberships(guid, to_be_guids, replace_all=True, known_new=True)

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

    async def _sync_memberships(self, guid: str, to_be_guids: set, replace_all: bool, known_new: bool = False):
        # Fetch current memberships (skipped entirely for a just-created
        # element via known_new -- it cannot have any memberships yet).
        if known_new:
            as_is: set = set()
        else:
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
        if attributes.get('In Data Structure', {}).get('guid'):
            data_struct_guids.add(attributes['In Data Structure']['guid'])
        parent_field_guids = set(attributes.get('In Data Field', {}).get('guid_list', []))
        if attributes.get('In Data Field', {}).get('guid'):
            parent_field_guids.add(attributes['In Data Field']['guid'])
        term_guids = set(attributes.get('Glossary Term', {}).get('guid_list', []))
        if attributes.get('Glossary Term', {}).get('guid'):
            term_guids.add(attributes['Glossary Term']['guid'])
        data_class_guid = attributes.get('Data Class', {}).get('guid')
        data_dict_guids = set(attributes.get('In Data Dictionary', {}).get('guid_list', []))
        if attributes.get('In Data Dictionary', {}).get('guid'):
            data_dict_guids.add(attributes['In Data Dictionary']['guid'])

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block

            self.last_body = body = set_update_body(om_type or "Data Field", attributes)
            body['properties'] = self.filter_update_properties(props_body, body.get('mergeUpdate', True))
            await self.client.data_designer._async_update_data_field(guid, body)
            self.parsed_output["guid"] = guid
            
            await self._sync_all_rels(guid, data_struct_guids, parent_field_guids, term_guids, data_class_guid, data_dict_guids, not merge_update, attributes=attributes)
            
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
                # known_new=True: this GUID was just created, so it cannot have
                # any existing relationships yet -- skip the as-is fetches.
                await self._sync_all_rels(guid, data_struct_guids, parent_field_guids, term_guids, data_class_guid, data_dict_guids, replace_all=True, known_new=True, attributes=attributes)

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

    async def _sync_all_rels(self, guid: str, ds_guids: set, parent_guids: set, term_guids: set, dc_guid: str, dict_guids: set,
                              replace_all: bool, known_new: bool = False, attributes: dict = None):
        """
        Unified relationship sync for Data Field.

        known_new=True (pass this for a just-created field) skips both
        as-is fetches below entirely -- a brand-new field cannot have any
        existing relationships of any of these types yet.
        """
        if known_new:
            rel_els: Dict[str, Any] = {}
        else:
            # This is a complex sync involving multiple relationship types
            rel_els = await self.client.data_designer._async_get_data_field_rel_elements(guid)

        # 1. Data Structures
        attributes = attributes or {}
        member_field_body = body_slimmer({
            "class": "NewRelationshipRequestBody",
            "properties": {"class": "MemberDataFieldProperties", **_part_of_props(attributes)},
        })
        nested_field_body = body_slimmer({
            "class": "NewRelationshipRequestBody",
            "properties": {"class": "NestedDataFieldProperties", **_part_of_props(attributes)},
        })
        as_is_ds = set(rel_els.get("data_structure_guids", []))
        sync_res = await self.sync_members(as_is_ds, ds_guids,
                               lambda ds: self.client.data_designer._async_link_member_data_field(ds, guid, member_field_body),
                               lambda ds: self.client.data_designer._async_detach_member_data_field(ds, guid, None),
                               replace_all)
        if sync_res.get("added") or sync_res.get("removed"):
            self.add_related_result("Data Structures Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
        if sync_res.get("errors"):
            self.add_related_result("Data Structures Sync", status="failure", message="; ".join(sync_res["errors"]))

        # 2. Parent Fields
        as_is_parents = set(rel_els.get("parent_guids", []))
        sync_res = await self.sync_members(as_is_parents, parent_guids,
                               lambda p: self.client.data_designer._async_link_nested_data_field(p, guid, nested_field_body),
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

        # 4. Data Class (DataValueDefinition)
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
        if known_new:
            as_is_dicts = set()
        else:
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
            "allowsDuplicateValues": attributes.get('Allow Duplicate Values', {}).get('value', True),
            "isCaseSensitive": attributes.get('Is Case Sensitive', {}).get('value'),
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
        data_dict_guids = set(attributes.get('In Data Dictionary', {}).get('guid_list', []))
        if attributes.get('In Data Dictionary', {}).get('guid'):
            data_dict_guids.add(attributes['In Data Dictionary']['guid'])
        # "In Data Value Specification"/"Specializes Data Value Specification"
        # both describe the same DataValueHierarchy parent -- near-synonym
        # descriptions in the compact spec, treated as aliases of one
        # relationship (see PYEGERIA_ISSUES.md ISSUE-101 follow-up).
        value_spec_parent_guids = set(attributes.get('In Data Value Specification', {}).get('guid_list', []))
        if attributes.get('In Data Value Specification', {}).get('guid'):
            value_spec_parent_guids.add(attributes['In Data Value Specification']['guid'])
        value_spec_parent_guids |= set(attributes.get('Specializes Data Value Specification', {}).get('guid_list', []))
        if attributes.get('Specializes Data Value Specification', {}).get('guid'):
            value_spec_parent_guids.add(attributes['Specializes Data Value Specification']['guid'])

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block

            self.last_body = body = {"class": "UpdateElementRequestBody", "properties": props}
            await self.client.data_designer._async_update_data_value_specification(guid, body)
            self.parsed_output["guid"] = guid

            await self._sync_all_rels(guid, containing_dc_guids, term_guids, data_dict_guids, not merge_update, value_spec_parent_guids=value_spec_parent_guids)
            
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
                # known_new=True: this GUID was just created, so it cannot have
                # any existing relationships yet -- skip the as-is fetches.
                await self._sync_all_rels(guid, containing_dc_guids, term_guids, data_dict_guids, replace_all=True, known_new=True, value_spec_parent_guids=value_spec_parent_guids)

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

    async def _sync_all_rels(self, guid: str, cont_guids: set, term_guids: set, dict_guids: set,
                              replace_all: bool, known_new: bool = False, value_spec_parent_guids: set = None):
        """known_new=True skips both as-is fetches below (see DataFieldProcessor._sync_all_rels)."""
        rel_els = {} if known_new else (await self.client.data_designer._async_get_data_class_rel_elements(guid) or {})


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
                               
        # 3. Data Dictionaries
        if known_new:
            as_is_dicts: set = set()
        else:
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

        # 4. Data Value Specification parent (DataValueHierarchy)
        if value_spec_parent_guids is not None:
            as_is_value_spec = set(rel_els.get("specialized_data_value_spec_guids", []))
            sync_res = await self.sync_members(as_is_value_spec, value_spec_parent_guids,
                                   lambda p: self.client.data_designer._async_link_specialized_data_value_specification(p, guid, None),
                                   lambda p: self.client.data_designer._async_detach_specialized_data_value_specification(p, guid, None),
                                   replace_all)
            if sync_res.get("added") or sync_res.get("removed"):
                self.add_related_result("Data Value Specification Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
            if sync_res.get("errors"):
                self.add_related_result("Data Value Specification Sync", status="failure", message="; ".join(sync_res["errors"]))

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
        props_body["grainStatement"] = attributes.get('Grain Statement', {}).get('value')
        props_body["granularityBasis"] = attributes.get('Granularity Basis', {}).get('value')
        props_body["interval"] = attributes.get('Interval', {}).get('value')

        # "In Data Value Specification"/"Specializes Data Value Specification"
        # both describe the same DataValueHierarchy parent -- near-synonym
        # descriptions in the compact spec, treated as aliases of one
        # relationship (see PYEGERIA_ISSUES.md ISSUE-101 follow-up).
        value_spec_parent_guids = set(attributes.get('In Data Value Specification', {}).get('guid_list', []))
        if attributes.get('In Data Value Specification', {}).get('guid'):
            value_spec_parent_guids.add(attributes['In Data Value Specification']['guid'])
        value_spec_parent_guids |= set(attributes.get('Specializes Data Value Specification', {}).get('guid_list', []))
        if attributes.get('Specializes Data Value Specification', {}).get('guid'):
            value_spec_parent_guids.add(attributes['Specializes Data Value Specification']['guid'])

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block

            self.last_body = body = set_update_body(om_type or "Data Grain", attributes)
            body['properties'] = self.filter_update_properties(props_body, body.get('mergeUpdate', True))
            await self.client.data_designer._async_update_data_value_specification(guid, body)
            self.parsed_output["guid"] = guid

            await self._sync_value_spec_parent(guid, value_spec_parent_guids, replace_all=True)

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

                await self._sync_value_spec_parent(guid, value_spec_parent_guids, replace_all=True, known_new=True)

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

    async def _sync_value_spec_parent(self, guid: str, to_be_guids: set, replace_all: bool, known_new: bool = False):
        """Sync this element's DataValueHierarchy parent(s) -- shared by
        DataGrainProcessor and DataValueSpecificationProcessor."""
        if known_new:
            as_is = set()
        else:
            rel_els = await self.client.data_designer._async_get_data_value_specification_rel_elements(guid) or {}
            as_is = set(rel_els.get("specialized_data_value_spec_guids", []))
        sync_res = await self.sync_members(as_is, to_be_guids,
                               lambda p: self.client.data_designer._async_link_specialized_data_value_specification(p, guid, None),
                               lambda p: self.client.data_designer._async_detach_specialized_data_value_specification(p, guid, None),
                               replace_all)
        if sync_res.get("added") or sync_res.get("removed"):
            self.add_related_result("Data Value Specification Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
        if sync_res.get("errors"):
            self.add_related_result("Data Value Specification Sync", status="failure", message="; ".join(sync_res["errors"]))


_LINK_VERBS = ("Link", "Attach", "Add")
_DETACH_VERBS = ("Detach", "Unlink", "Remove")


def _labeled_props(attributes: dict) -> dict:
    """LabeledRelationshipProperties fields (label, description)."""
    return {
        "label": attributes.get('Label', {}).get('value'),
        "description": attributes.get('Description', {}).get('value'),
    }


def _part_of_props(attributes: dict) -> dict:
    """PartOfRelationshipProperties fields, shared by MemberDataField and NestedDataField."""
    return {
        "position": attributes.get('Position', {}).get('value'),
        "minCardinality": attributes.get('Minimum Cardinality', {}).get('value'),
        "maxCardinality": attributes.get('Maximum Cardinality', {}).get('value'),
        "coverageCategory": attributes.get('Coverage Category', {}).get('value'),
    }


def _linked_data_field_props(attributes: dict) -> dict:
    return {
        "relationshipTypeName": attributes.get('Link Relationship Type Name', {}).get('value'),
        "relationshipEnd": attributes.get('Relationship End', {}).get('value'),
        "minCardinality": attributes.get('Minimum Cardinality', {}).get('value'),
        "maxCardinality": attributes.get('Maximum Cardinality', {}).get('value'),
        # LinkedDataFieldProperties has displayName rather than label.
        "displayName": attributes.get('Label', {}).get('value'),
        "description": attributes.get('Description', {}).get('value'),
    }


# OM_TYPE -> (end1 attribute, end2 attribute, link method, detach method, relationship properties builder).
# Relationship ends and properties follow Egeria types 0540/0580/0581; each link/detach method takes
# (end1_guid, end2_guid, body) in that order.
DATA_DESIGNER_LINKS: Dict[str, tuple] = {
    "MemberDataField": ("Data Structure", "Data Field",
                        "_async_link_member_data_field", "_async_detach_member_data_field", _part_of_props),
    "NestedDataField": ("Parent Data Field", "Nested Data Field",
                        "_async_link_nested_data_field", "_async_detach_nested_data_field", _part_of_props),
    "LinkedDataField": ("Linked Data Field 1", "Linked Data Field 2",
                        "_async_link_linked_data_field", "_async_detach_linked_data_field", _linked_data_field_props),
    "SchemaAttributeDefinition": ("Data Field", "Schema Attribute",
                                  "_async_link_schema_attribute_definition",
                                  "_async_detach_schema_attribute_definition", _labeled_props),
    "SchemaTypeDefinition": ("Data Structure", "Schema Type",
                             "_async_link_schema_type_definition",
                             "_async_detach_schema_type_definition", _labeled_props),
    "DataStructureDefinition": ("Certification Type", "Data Structure",
                                "_async_link_certification_type_to_data_structure",
                                "_async_detach_certification_type_from_data_structure", _labeled_props),
    "DataValueDefinition": ("Element Id", "Data Value Specification",
                            "_async_link_data_class_definition",
                            "_async_detach_data_class_definition", _labeled_props),
    "DataValueHierarchy": ("Data Value Specification", "Data Value Specification Child",
                           "_async_link_specialized_data_value_specification",
                           "_async_detach_specialized_data_value_specification", _labeled_props),
    "DataClassComposition": ("Data Class", "Data Class Child",
                             "_async_link_nested_data_class", "_async_detach_nested_data_class", _labeled_props),
}


class DataDesignerLinkProcessor(AsyncBaseCommandProcessor):
    """
    Link/Detach processor for every Data Designer relationship command, driven by
    the command's OM_TYPE through DATA_DESIGNER_LINKS.

    Registering "Link X" also routes "Detach/Unlink/Remove X" here (LINK_VERBS
    expansion), so apply_changes() branches on the verb -- the per-relationship
    processors this replaced always linked, so a "Detach ..." command silently
    created the relationship instead of removing it.
    """

    def supports_target_element_lookup(self) -> bool:
        # Relationship-only processor -- see GovernanceLinkProcessor
        # (md_processing/v2/governance.py): without this, the base class's
        # Create<->Update upsert transition can rewrite the verb (ISSUE-68).
        return False

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = getattr(self, 'canonical_object_type', None) or self.command.object_type
        attributes = self.parsed_output["attributes"]
        om_type = (self.get_command_spec() or {}).get("OM_TYPE")

        link_spec = DATA_DESIGNER_LINKS.get(om_type)
        if not link_spec:
            raise PyegeriaException(f"No Data Designer relationship mapping for OM_TYPE '{om_type}' ({object_type})")
        end1_attr, end2_attr, link_method, detach_method, props_fn = link_spec

        end1_guid = attributes.get(end1_attr, {}).get('guid')
        end2_guid = attributes.get(end2_attr, {}).get('guid')
        if not (end1_guid and end2_guid):
            missing = [f"'{a}'" for a, g in ((end1_attr, end1_guid), (end2_attr, end2_guid)) if not g]
            raise ValueError(f"Cannot {verb.lower()} {object_type}: resolution failed for {', '.join(missing)}")

        client = self.client.data_designer
        if verb in _DETACH_VERBS:
            self.last_body = body = body_slimmer(set_delete_rel_request_body(om_type, attributes))
            await getattr(client, detach_method)(end1_guid, end2_guid, body)
            logger.success(f"Detached {om_type} between {end1_guid} and {end2_guid}")
            return (f"\n\n## {verb} {object_type}\n\n"
                    f"Detached the {om_type} relationship between {end1_guid} and {end2_guid}")

        if verb not in _LINK_VERBS:
            return self.command.raw_block

        body = set_rel_request_body(om_type, attributes)
        body["properties"] = {"class": f"{om_type}Properties", **props_fn(attributes)}
        self.last_body = body = body_slimmer(body)
        await getattr(client, link_method)(end1_guid, end2_guid, body)
        logger.success(f"Linked {end1_guid} to {end2_guid} with {om_type}")
        return f"\n\n## {verb} {object_type}\n\nLinked {end1_guid} to {end2_guid} ({om_type})"

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        return None


class DataFieldPrimaryKeyProcessor(AsyncBaseCommandProcessor):
    """
    Classify/Declassify a data field as a primary key. Egeria's archive patches
    PrimaryKey (0534) so it may be attached to a DataField as well as a
    RelationalColumn; the Schema Maker primary-key endpoint classifies whatever
    GUID it is given, so it is reused here for data fields.
    """

    def supports_target_element_lookup(self) -> bool:
        return False

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = getattr(self, 'canonical_object_type', None) or self.command.object_type
        attributes = self.parsed_output["attributes"]
        field_guid = attributes.get('Data Field', {}).get('guid')
        if not field_guid:
            raise ValueError(f"Cannot {verb.lower()} {object_type}: resolution failed for 'Data Field'")

        if verb in ("Declassify", "Unset"):
            await self.client.schema_maker._async_remove_primary_key_classification(field_guid)
            logger.success(f"Removed PrimaryKey classification from data field {field_guid}")
            return f"\n\n## {verb} {object_type}\n\nRemoved PrimaryKey classification from {field_guid}."

        self.last_body = body = body_slimmer({
            "class": "NewClassificationRequestBody",
            "properties": {
                "class": "PrimaryKeyProperties",
                "displayName": attributes.get('Primary Key Name', {}).get('value'),
                "keyPattern": attributes.get('Primary Key Pattern', {}).get('value'),
            },
        })
        await self.client.schema_maker._async_add_primary_key_classification(field_guid, body)
        logger.success(f"Classified data field {field_guid} as a primary key")
        return f"\n\n## {verb} {object_type}\n\nApplied PrimaryKey classification to {field_guid}."

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        return None


class AssignDataValueSpecificationProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Assign/Attach Data Value Specification to Element commands,
    and (verb-branched, see apply_changes) Detach Data Value Specification
    from Element -- the two share this one processor because the "to
    Element"/"from Element" noun-phrase pair both expand, via LINK_VERBS, to
    the identical set of six verb phrasings (register_processor ->
    build_command_variants), so a separate detach-only processor class would
    only ever handle whichever of the two reg() calls happened to register
    last -- a silent collision, not a routing choice. Branching on verb here
    instead makes the outcome independent of registration order.
    """
    def get_command_spec(self) -> Dict[str, Any]:
        # Use the full normalized command (verb + object_type) for spec lookup
        return get_command_spec(f"{self.command.verb} {self.command.object_type}")

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        if self.command.verb in ("Detach", "Unlink", "Remove"):
            return None
        return await super().fetch_as_is()

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        spec_guid = attributes.get('Data Value Specification', {}).get('guid')
        elem_guid = attributes.get('Element Id', {}).get('guid')

        if self.command.verb in ("Detach", "Unlink", "Remove"):
            if not spec_guid or not elem_guid:
                logger.error("Both Data Value Specification and Element Id are required")
                return self.command.raw_block
            try:
                body = set_delete_rel_request_body("DataValueAssignment", attributes)
                await self.client.data_designer._async_detach_data_value_assignment(
                    elem_guid, spec_guid, body_slimmer(body)
                )
                logger.success(f"Detached Data Value Specification {spec_guid} from element {elem_guid}")
                return f"\n\n## {self.command.verb} {self.command.object_type}\n\nOperation completed."
            except Exception as e:
                logger.error(f"Error detaching data value specification: {e}")
                return self.command.raw_block

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
            body = set_rel_request_body("DataValueAssignment", attributes)
            body["properties"] = {
                "class": "DataValueAssignmentProperties",
                "assignmentStatus": attributes.get("Assignment Status", {}).get("value"),
                "confidence": attributes.get("Confidence", {}).get("value"),
                "method": attributes.get("Method", {}).get("value"),
                "source": attributes.get("Source", {}).get("value"),
                "steward": attributes.get("Steward", {}).get("value"),
                "stewardPropertyName": attributes.get("Steward Property Name", {}).get("value"),
                "stewardTypeName": attributes.get("Steward Type Name", {}).get("value"),
                "threshold": attributes.get("Threshold", {}).get("value"),
            }

            await self.client.data_designer._async_link_data_value_assignment(
                elem_guid, spec_guid, body_slimmer(body)
            )
            logger.success(f"Assigned Data Value Specification {spec_guid} to element {elem_guid}")
            return "Assignment created successfully"
        except Exception as e:
            logger.error(f"Error assigning data value specification: {e}")
            return self.command.raw_block

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        return None

