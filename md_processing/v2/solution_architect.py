"""
Solution Architect Processors for Dr.Egeria v2.
"""
from typing import Dict, Any, Optional, List, Set
from loguru import logger
import json

from pyegeria import EgeriaTech, PyegeriaException
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.md_processing_constants import get_command_spec
from md_processing.md_processing_utils.common_md_utils import (
    set_element_prop_body, set_create_body, set_update_body, 
    set_rel_request_body, set_rel_prop_body,
    update_element_dictionary, add_note_in_dr_e, async_add_note_in_dr_e,
    set_delete_request_body, set_delete_rel_request_body
)
from pyegeria.core.utils import body_slimmer

class BlueprintProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Solution Blueprints.
    """

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_solution_blueprint_by_guid(guid)
        except PyegeriaException:
            return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        status = attributes.get('Status', {}).get('value', 'ACTIVE')
        merge_update = attributes.get('Merge Update', {}).get('value', True)
        journal_entry = attributes.get('Journal Entry', {}).get('value')
        
        comp_guids = set(attributes.get('Solution Components', {}).get('guid_list', []))

        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block

            body = set_update_body(om_type or "Solution Blueprint", attributes)
            prop_body = set_element_prop_body(om_type or "Solution Blueprint", qualified_name, attributes)
            body['properties'] = self.filter_update_properties(prop_body, body.get('mergeUpdate', True))
            
            await self.client._async_update_solution_blueprint(guid, body)
            self.parsed_output["guid"] = guid
            # if status:
            #     await self.client._async_update_solution_element_status(guid, status)
            
            sync_res = await self._sync_components(guid, comp_guids, not merge_update)
            if sync_res.get("added") or sync_res.get("removed"):
                self.add_related_result("Components Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
            if sync_res.get("errors"):
                self.add_related_result("Components Sync", status="failure", message="; ".join(sync_res["errors"]))
            
            if journal_entry:
                try:
                    j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                    if j_guid:
                        self.add_related_result("Journal Entry", j_guid)
                except Exception as e:
                    self.add_related_result("Journal Entry", status="failure", message=str(e))

            logger.success(f"Updated Blueprint '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = set_create_body(om_type or "Solution Blueprint", attributes)
            body['properties'] = set_element_prop_body(om_type or "Solution Blueprint", qualified_name, attributes)
            body = body_slimmer(body)
            
            raw_guid = await self.client._async_create_solution_blueprint(body)
            guid = self.extract_guid_or_raise(raw_guid, "Create Solution Blueprint")
            if guid:
                self.parsed_output["guid"] = guid
                sync_res = await self._sync_components(guid, comp_guids, replace_all=True)
                if sync_res.get("added") or sync_res.get("removed"):
                    self.add_related_result("Components Sync", message=f"Added {len(sync_res['added'])}, Removed {len(sync_res['removed'])}")
                if sync_res.get("errors"):
                    self.add_related_result("Components Sync", status="failure", message="; ".join(sync_res["errors"]))

                if journal_entry:
                    try:
                        j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                        if j_guid:
                            self.add_related_result("Journal Entry", j_guid)
                    except Exception as e:
                        self.add_related_result("Journal Entry", status="failure", message=str(e))
                
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Blueprint '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.raw_block

    async def _sync_components(self, guid: str, to_be_guids: Set[str], replace_all: bool) -> Dict[str, Any]:
        bp_element = await self.client._async_get_solution_blueprint_by_guid(guid)
        as_is = {c['elementHeader']['guid'] for c in bp_element.get('solutionComponents', [])}
        
        async def add_fn(comp_guid):
            body = {"class": "NewRelationshipRequestBody", "properties": {"class": "SolutionBlueprintCompositionProperties", "typeName": "SolutionBlueprintComposition", "description": "linked by Dr.Egeria v2"}}
            await self.client._async_link_solution_component_to_blueprint(guid, comp_guid, body)
            
        async def remove_fn(comp_guid):
            await self.client._async_detach_solution_component_from_blueprint(guid, comp_guid, None)
            
        return await self.sync_members(as_is, to_be_guids, add_fn, remove_fn, replace_all)

class ComponentProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Solution Components.
    """

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_solution_component_by_guid(guid)
        except PyegeriaException:
            return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        merge_update = attributes.get('Merge Update', {}).get('value', True)
        journal_entry = attributes.get('Journal Entry', {}).get('value')
        
        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")

        # 1. Properties
        prop_body = set_element_prop_body(om_type or "SolutionComponent", qualified_name, attributes)
        
        # 2. Relationships
        actor_guids = set(attributes.get('Actors', {}).get('guid_list', []))
        blueprint_guids = set(attributes.get('In Solution Blueprints', {}).get('guid_list', []))
        supply_chain_guids = set(attributes.get('In Information Supply Chains', {}).get('guid_list', []))
        parent_comp_guids = set(attributes.get('Parent Components', {}).get('guid_list', []))
        keywords = set(attributes.get('Search Keywords', {}).get('value', []))

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block

            body = body_slimmer({
                "class": "UpdateElementRequestBody",
                "mergeUpdate": merge_update,
                "properties": prop_body
            })
            await self.client._async_update_solution_component(guid, body)
            self.parsed_output["guid"] = guid
            
            sync_res = await self._sync_all_rels(guid, supply_chain_guids, parent_comp_guids, actor_guids, blueprint_guids, keywords, not merge_update)
            if any(sync_res.values()):
                self.add_related_result("Relationships Sync", message=f"Updated relationships (Success: {len(sync_res['added']) + len(sync_res['removed'])}, Errors: {len(sync_res['errors'])})")
            
            if journal_entry:
                try:
                    j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                    if j_guid:
                        self.add_related_result("Journal Entry", j_guid)
                except Exception as e:
                    self.add_related_result("Journal Entry", status="failure", message=str(e))

            logger.success(f"Updated Component '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = body_slimmer({
                "class": "NewElementRequestBody",
                "properties": prop_body,
                "initialStatus": attributes.get('Status', {}).get('value', 'ACTIVE')
            })
            # Anchor/Parent logic
            body["anchorGUID"] = attributes.get('Anchor ID', {}).get('guid')
            body["parentGUID"] = attributes.get('Parent ID', {}).get('guid')
            body["parentRelationshipTypeName"] = attributes.get('Parent Relationship Type Name', {}).get('value')
            body["isOwnAnchor"] = attributes.get('Is Own Anchor', {}).get('value', body["parentGUID"] is None)

            raw_guid = await self.client._async_create_solution_component(body)
            guid = self.extract_guid_or_raise(raw_guid, "Create Solution Component")
            if guid:
                self.parsed_output["guid"] = guid
                sync_res = await self._sync_all_rels(guid, supply_chain_guids, parent_comp_guids, actor_guids, blueprint_guids, keywords, replace_all=True)
                if any(sync_res.values()):
                    self.add_related_result("Relationships Sync", message=f"Initial relationships (Success: {len(sync_res['added']) + len(sync_res['removed'])}, Errors: {len(sync_res['errors'])})")

                if journal_entry:
                    try:
                        j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                        if j_guid:
                            self.add_related_result("Journal Entry", j_guid)
                    except Exception as e:
                        self.add_related_result("Journal Entry", status="failure", message=str(e))
                
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Component '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.raw_block

    async def _sync_all_rels(self, guid: str, sc_guids: Set[str], parent_guids: Set[str], actor_guids: Set[str], bp_guids: Set[str], keywords: Set[str], replace_all: bool) -> Dict[str, Any]:
        rel_els = await self._get_component_related_elements(guid)
        combined_results = {"added": [], "removed": [], "errors": []}
        
        # 1. Supply Chains
        as_is_sc = set(rel_els.get("supply_chain_guids", []))
        res = await self.sync_members(as_is_sc, sc_guids,
                               lambda sc: self.client._async_link_design_to_implementation(sc, guid, None),
                               lambda sc: self.client._async_detach_design_from_implementation(sc, guid),
                               replace_all)
        for k in combined_results: combined_results[k].extend(res.get(k, []))
                               
        # 2. Parent Components
        as_is_parents = set(rel_els.get("parent_component_guids", []))
        res = await self.sync_members(as_is_parents, parent_guids,
                               lambda p: self.client._async_link_subcomponent(p, guid, None),
                               lambda p: self.client._async_detach_sub_component(p, guid, None),
                               replace_all)
        for k in combined_results: combined_results[k].extend(res.get(k, []))
                               
        # 3. Actors
        as_is_actors = set(rel_els.get("actor_guids", []))
        res = await self.sync_members(as_is_actors, actor_guids,
                               lambda a: self.client._async_link_component_to_actor(a, guid, None),
                               lambda a: self.client._async_detach_component_actor(a, guid, None),
                               replace_all)
        for k in combined_results: combined_results[k].extend(res.get(k, []))
                               
        # 4. Blueprints
        as_is_bps = set(rel_els.get("blueprint_guids", []))
        res = await self.sync_members(as_is_bps, bp_guids,
                               lambda bp: self.client._async_link_solution_component_to_blueprint(bp, guid, {"class": "NewRelationshipRequestBody", "properties": {"class": "SolutionBlueprintCompositionProperties", "typeName": "SolutionBlueprintComposition", "description": "linked by Dr.Egeria v2"}}),
                               lambda bp: self.client._async_detach_solution_component_from_blueprint(bp, guid, None),
                               replace_all)
        for k in combined_results: combined_results[k].extend(res.get(k, []))
        
        # 5. Keywords
        as_is_kw = set(rel_els.get("keywords_list", {}).keys())
        kw_map = rel_els.get("keywords_list", {})
        res = await self.sync_members(as_is_kw, keywords,
                               lambda k: self.client._async_add_search_keyword_to_element(guid, k),
                               lambda k: self.client._async_remove_search_keyword(kw_map[k]),
                               replace_all)
        for k in combined_results: combined_results[k].extend(res.get(k, []))

        return combined_results

    async def _get_component_related_elements(self, guid: str) -> Dict[str, Any]:
        response = await self.client._async_get_solution_component_by_guid(guid)
        if not isinstance(response, dict):
            return {}

        res = {
            "sub_component_guids": [],
            "actor_guids": [],
            "blueprint_guids": [],
            "supply_chain_guids": [],
            "parent_component_guids": [],
            "keywords_list": {},
        }

        # memberOfCollections
        for member in response.get('memberOfCollections', []):
            m_guid = member['relatedElement']['elementHeader'].get('guid')
            type_name = member['relatedElement']['elementHeader']['type'].get('typeName')
            if type_name == 'SolutionBlueprint':
                res["blueprint_guids"].append(m_guid)
            elif type_name == 'InformationSupplyChain':
                res["supply_chain_guids"].append(m_guid)

        # derivedFrom
        for mem in response.get('derivedFrom', []):
            m_guid = mem['relatedElement']['elementHeader'].get('guid')
            type_name = mem['relatedElement']['elementHeader']['type'].get('typeName')
            if type_name == 'SolutionBlueprint' or type_name == 'InformationSupplyChain':
                res["supply_chain_guids"].append(m_guid)

        # searchKeywords
        for mem in response.get('searchKeywords', []):
            m_guid = mem['relatedElement']['elementHeader'].get('guid')
            keyword = mem['relatedElement']['properties'].get('displayName') or mem['relatedElement']['properties'].get('keyword')
            if keyword:
                res["keywords_list"][keyword] = m_guid

        # nestedSolutionComponents
        for comp in response.get('nestedSolutionComponents', []):
            res["sub_component_guids"].append(comp['relatedElement']['elementHeader'].get('guid'))

        # subComponents
        for comp in response.get('subComponents', []):
            res["sub_component_guids"].append(comp['elementHeader'].get('guid'))

        # usedInSolutionComponents (Parents)
        for comp in response.get('usedInSolutionComponents', []):
            res["parent_component_guids"].append(comp['relatedElement']['elementHeader'].get('guid'))

        # actors
        for actor in response.get('actors', []):
            res["actor_guids"].append(actor['elementHeader'].get('guid'))

        return res

class SupplyChainProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Information Supply Chains.
    """

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_info_supply_chain_by_guid(guid)
        except PyegeriaException:
            return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        merge_update = attributes.get('Merge Update', {}).get('value', True)
        journal_entry = attributes.get('Journal Entry', {}).get('value')
        
        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")

        prop_body = set_element_prop_body(om_type or "InformationSupplyChain", qualified_name, attributes)

        in_sc_guids = set(attributes.get('In Information Supply Chain', {}).get('guid_list', []))
        nested_sc_guids = set(attributes.get('Nested Information Supply Chains', {}).get('guid_list', []))

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block

            body = set_update_body(om_type or "InformationSupplyChain", attributes)
            body['properties'] = self.filter_update_properties(prop_body, body.get('mergeUpdate', True))
            await self.client._async_update_info_supply_chain(guid, body)
            self.parsed_output["guid"] = guid
            
            # Sync parents/nested
            sync_res = await self._sync_rels(guid, in_sc_guids, nested_sc_guids, not merge_update)
            if any(sync_res.values()):
                self.add_related_result("Relationships Sync", message=f"Updated relationships (Success: {len(sync_res['added']) + len(sync_res['removed'])}, Errors: {len(sync_res['errors'])})")
            
            if journal_entry:
                try:
                    j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                    if j_guid:
                        self.add_related_result("Journal Entry", j_guid)
                except Exception as e:
                    self.add_related_result("Journal Entry", status="failure", message=str(e))

            logger.success(f"Updated Supply Chain '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = set_create_body(om_type or "InformationSupplyChain", attributes)
            body['properties'] = prop_body
            
            raw_guid = await self.client._async_create_info_supply_chain(body)
            guid = self.extract_guid_or_raise(raw_guid, "Create Information Supply Chain")
            if guid:
                self.parsed_output["guid"] = guid
                sync_res = await self._sync_rels(guid, in_sc_guids, nested_sc_guids, replace_all=True)
                if any(sync_res.values()):
                    self.add_related_result("Relationships Sync", message=f"Initial relationships (Success: {len(sync_res['added']) + len(sync_res['removed'])}, Errors: {len(sync_res['errors'])})")

                if journal_entry:
                    try:
                        j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                        if j_guid:
                            self.add_related_result("Journal Entry", j_guid)
                    except Exception as e:
                        self.add_related_result("Journal Entry", status="failure", message=str(e))
                
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Supply Chain '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.raw_block

    async def _sync_rels(self, guid: str, parent_guids: Set[str], nested_guids: Set[str], replace_all: bool) -> Dict[str, Any]:
        rel_els = await self._get_supply_chain_rel_elements(guid)
        combined_results = {"added": [], "removed": [], "errors": []}
        
        # 1. Parents
        as_is_parents = set(rel_els.get("parent_guids", []))
        res = await self.sync_members(as_is_parents, parent_guids,
                               lambda p: self.client._async_compose_info_supply_chains(p, guid, None),
                               lambda p: self.client._async_decompose_info_supply_chains(p, guid, None),
                               replace_all)
        for k in combined_results: combined_results[k].extend(res.get(k, []))
                               
        # 2. Nested
        as_is_nested = set(rel_els.get("nested_guids", []))
        res = await self.sync_members(as_is_nested, nested_guids,
                               lambda n: self.client._async_compose_info_supply_chains(guid, n, None),
                               lambda n: self.client._async_decompose_info_supply_chains(guid, n, None),
                               replace_all)
        for k in combined_results: combined_results[k].extend(res.get(k, []))

        return combined_results

    async def _get_supply_chain_rel_elements(self, guid: str) -> Dict[str, Any]:
        el_struct = await self.client._async_get_info_supply_chain_by_guid(guid)
        if not isinstance(el_struct, dict):
            return {}

        res = {
            "parent_guids": [],
            "nested_guids": [],
            "implemented_by_guids": [],
            "supply_to_guids": [],
            "supply_from_guids": [],
        }

        # Parents
        for parent in el_struct.get("parents", []):
            res["parent_guids"].append(parent['relatedElement']['elementHeader']["guid"])

        # Nested (Collection Members or nestedDataClasses)
        for element in el_struct.get("collectionMembers", []):
            res["nested_guids"].append(element['relatedElement']['elementHeader']['guid'])

        # Implemented By
        for element in el_struct.get("implementedByList", []):
            res["implemented_by_guids"].append(element['relatedElement']['elementHeader']['guid'])

        # Supply To
        for element in el_struct.get("supplyTo", []):
            res["supply_to_guids"].append(element['relatedElement']['elementHeader']['guid'])

        # Supply From
        for element in el_struct.get("supplyFrom", []):
            res["supply_from_guids"].append(element['relatedElement']['elementHeader']['guid'])

        return res

class SolutionArchitectProcessor(AsyncBaseCommandProcessor):
    """
    Generic Processor for Solution Architect elements (Supply Chain, Blueprint, Component, Role).
    """

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")
        try:
            if om_type == "InformationSupplyChain":
                return await self.client._async_get_info_supply_chain_by_guid(guid)
            elif om_type == "SolutionBlueprint":
                return await self.client._async_get_solution_blueprint_by_guid(guid)
            elif om_type == "SolutionComponent":
                return await self.client._async_get_solution_component_by_guid(guid)
            elif om_type == "SolutionRole" or om_type == "SolutionActorRole":
                return await self.client._async_get_solution_role_by_guid(guid)
            return None
        except PyegeriaException:
            return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
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

            body = set_update_body(om_type, attributes)
            prop_body = set_element_prop_body(om_type, qualified_name, attributes)
            body['properties'] = self.filter_update_properties(prop_body, body.get('mergeUpdate', True))
            
            if om_type == "InformationSupplyChain":
                await self.client._async_update_info_supply_chain(guid, body)
            elif om_type == "SolutionBlueprint":
                await self.client._async_update_solution_blueprint(guid, body)
            elif om_type == "SolutionComponent":
                await self.client._async_update_solution_component(guid, body)
            elif om_type == "SolutionActorRole":
                await self.client._async_update_solution_role(guid, body)
            
            self.parsed_output["guid"] = guid
            
            if journal_entry:
                await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)

            logger.success(f"Updated {om_type} '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = set_create_body(om_type, attributes)
            body['properties'] = set_element_prop_body(om_type, qualified_name, attributes)
            body = body_slimmer(body)
            
            raw_guid = None
            if om_type == "InformationSupplyChain":
                raw_guid = await self.client._async_create_info_supply_chain(body)
            elif om_type == "SolutionBlueprint":
                raw_guid = await self.client._async_create_solution_blueprint(body)
            elif om_type == "SolutionComponent":
                raw_guid = await self.client._async_create_solution_component(body)
            elif om_type == "SolutionActorRole":
                raw_guid = await self.client._async_create_solution_role(body)
            
            guid = self.extract_guid_or_raise(raw_guid, f"Create {om_type}")
            if guid:
                self.parsed_output["guid"] = guid
                if journal_entry:
                    await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)

                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created {om_type} '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.raw_block

class SolutionLinkProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Solution Architect relationships (Linking Wire, Supply Chain Link, SubComponent, Actor Link, etc.).
    """

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = getattr(self, 'canonical_object_type', self.command.object_type)
        attributes = self.parsed_output["attributes"]
        
        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")

        # Determine IDs based on spec custom_attributes or fallbacks
        custom_attrs = spec.get("custom_attributes", [])
        
        id1_key = None
        id2_key = None
        
        if len(custom_attrs) >= 2:
            id1_key = custom_attrs[0]
            id2_key = custom_attrs[1]
        else:
            # Fallback for ID1
            for k in ["Component1", "Segment1", "Blueprint", "Collection Id", "Parent Id", "ISC Parent", "Parent", "Isc Parent", "Element Id"]:
                if k in attributes:
                    id1_key = k
                    break
            
            # Fallback for ID2
            for k in ["Component2", "Segment2", "Element", "Member Id", "Child Id", "ISC Child", "Actor", "Role", "Child", "Element2 Id", "Element Id", "Component Child", "Isc Child"]:
                if k in attributes and k != id1_key:
                    id2_key = k
                    break
                    
            if not (id1_key and id2_key):
                # Final attempt: just take the first two attributes that have GUIDs
                candidates = [k for k, v in attributes.items() if v.get('guid')]
                if len(candidates) >= 2:
                    id1_key = candidates[0]
                    id2_key = candidates[1]

        if not (id1_key and id2_key):
            logger.error(f"Command {object_type} has fewer than 2 attributes for linking - {attributes.keys()}")
            return self.command.raw_block
            
        id1 = attributes.get(id1_key, {}).get('guid')
        id2 = attributes.get(id2_key, {}).get('guid')
        
        if not (id1 and id2):
            logger.warning(f"Missing GUIDs for {object_type}: {id1_key}={id1}, {id2_key}={id2}")
            return self.command.raw_block

        label = attributes.get('Wire Label', {}).get('value') or attributes.get('Link Label', {}).get('value') or attributes.get('Label', {}).get('value', "")
        description = attributes.get('Description', {}).get('value', "")
        
        if verb in ["Link", "Attach", "Add"]:
            properties = {
                "class": f"{om_type}Properties",
                "description": description,
                "effectiveFrom": attributes.get('Effective From', {}).get('value'),
                "effectiveTo": attributes.get('Effective To', {}).get('value')
            }
            
            # Determine which property to use for the 'label/role' field
            if om_type in ["SolutionLinkingWire", "InformationSupplyChainLink", "InformationSupplyChainComposition"]:
                 properties["label"] = label
            elif om_type == "CollectionMembership":
                 properties["membershipRationale"] = description
            else:
                 # Composition and Design relationships use 'role'
                 properties["role"] = attributes.get("Role", {}).get("value") or attributes.get("Solution Role", {}).get("value") or label

            body = {
                "class": "NewRelationshipRequestBody",
                "properties": properties
            }
            
            if om_type == "SolutionLinkingWire":
                await self.client._async_link_solution_linking_wire(id1, id2, body)
            elif om_type == "InformationSupplyChainLink":
                await self.client._async_link_peer_info_supply_chains(id1, id2, body)
            elif om_type == "InformationSupplyChainComposition":
                await self.client._async_compose_info_supply_chains(id1, id2, body)
            elif om_type == "SolutionComposition":
                await self.client._async_link_subcomponent(id1, id2, body)
            elif om_type == "SolutionComponentActor":
                # Method signature: role_guid, component_guid
                # Spec has Component1, Role. Role is id2.
                await self.client._async_link_component_to_actor(id2, id1, body)
            elif om_type == "SolutionBlueprintComposition":
                await self.client._async_link_solution_component_to_blueprint(id1, id2, body)
            elif om_type == "SolutionDesign":
                await self.client._async_link_solution_design(id1, id2, body)
            elif om_type == "CollectionMembership":
                 await self.client._async_add_to_collection(id1, id2, body)
            else:
                 logger.warning(f"OM_TYPE {om_type} not yet supported in SolutionLinkProcessor")
                 return self.command.raw_block

            logger.success(f"Linked {object_type} ({om_type})")
            return f"\n\n# {verb} {object_type}\n\nLinked {id1} to {id2}"

        elif verb in ["Detach", "Unlink", "Remove"]:
            body = {"class": "DeleteRelationshipRequestBody"}
            if om_type == "SolutionLinkingWire":
                await self.client._async_detach_solution_linking_wire(id1, id2, body)
            elif om_type == "InformationSupplyChainLink":
                await self.client._async_unlink_peer_info_supply_chains(id1, id2, body)
            elif om_type == "InformationSupplyChainComposition":
                await self.client._async_decompose_info_supply_chains(id1, id2, body)
            elif om_type == "SolutionComposition":
                await self.client._async_detach_sub_component(id1, id2, body)
            elif om_type == "SolutionComponentActor":
                await self.client._async_detach_component_actor(id2, id1, body)
            elif om_type == "SolutionBlueprintComposition":
                await self.client._async_detach_solution_component_from_blueprint(id1, id2, body)
            elif om_type == "SolutionDesign":
                await self.client._async_detach_solution_design(id1, id2, body)
            elif om_type == "CollectionMembership":
                await self.client._async_remove_from_collection(id1, id2, body)
            else:
                logger.warning(f"OM_TYPE {om_type} not yet supported in SolutionLinkProcessor for detach")
                return self.command.raw_block
                
            logger.success(f"Detached {object_type} ({om_type})")
            return f"\n\n# {verb} {object_type}\n\nDetached {id1} from {id2}"

        return self.command.raw_block
