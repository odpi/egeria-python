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
    update_element_dictionary, add_note_in_dr_e, async_add_note_in_dr_e
)
from pyegeria.core.utils import body_slimmer

class BlueprintProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Solution Blueprints.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Solution Blueprint")

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_solution_blueprint_by_guid(guid)
        except PyegeriaException:
            return None

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        qualified_name = self.parsed_output.get("qualified_name")
        if not qualified_name:
            return None
        try:
            res = await self.client._async_get_solution_blueprints_by_name(qualified_name)
            if isinstance(res, list) and len(res) > 0:
                return res[0]
            return res if isinstance(res, dict) else None
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

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.original_text

            body = set_update_body("Solution Blueprint", attributes)
            body['properties'] = set_element_prop_body("Solution Blueprint", qualified_name, attributes)
            body = body_slimmer(body)
            
            await self.client._async_update_solution_blueprint(guid, body)
            self.parsed_output["guid"] = guid
            # if status:
            #     await self.client._async_update_solution_element_status(guid, status)
            
            await self._sync_components(guid, comp_guids, not merge_update)
            
            if journal_entry:
                await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)

            logger.success(f"Updated Blueprint '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = set_create_body("Solution Blueprint", attributes)
            body['properties'] = set_element_prop_body("Solution Blueprint", qualified_name, attributes)
            body = body_slimmer(body)
            
            guid = await self.client._async_create_solution_blueprint(body)
            if guid:
                self.parsed_output["guid"] = guid
                await self._sync_components(guid, comp_guids, replace_all=True)
                if journal_entry:
                    await self.client._async_add_note_in_dr_e(qualified_name, display_name, journal_entry)
                
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Blueprint '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.original_text

    async def _sync_components(self, guid: str, to_be_guids: Set[str], replace_all: bool):
        bp_element = await self.client._async_get_solution_blueprint_by_guid(guid)
        as_is = {c['elementHeader']['guid'] for c in bp_element.get('solutionComponents', [])}
        
        async def add_fn(comp_guid):
            body = {"class": "NewRelationshipRequestBody", "properties": {"class": "SolutionBlueprintCompositionProperties", "typeName": "SolutionBlueprintComposition", "description": "linked by Dr.Egeria v2"}}
            await self.client._async_link_solution_component_to_blueprint(guid, comp_guid, body)
            
        async def remove_fn(comp_guid):
            await self.client._async_detach_solution_component_from_blueprint(guid, comp_guid, None)
            
        await self.sync_members(as_is, to_be_guids, add_fn, remove_fn, replace_all)

class ComponentProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Solution Components.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Solution Component")

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_solution_component_by_guid(guid)
        except PyegeriaException:
            return None

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        qualified_name = self.parsed_output.get("qualified_name")
        if not qualified_name:
            return None
        try:
            res = await self.client._async_get_solution_components_by_name(qualified_name)
            if isinstance(res, list) and len(res) > 0:
                return res[0]
            return res if isinstance(res, dict) else None
        except PyegeriaException:
            return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        merge_update = attributes.get('Merge Update', {}).get('value', True)
        journal_entry = attributes.get('Journal Entry', {}).get('value')
        
        # 1. Properties
        prop_body = {
            "class": "SolutionComponentProperties",
            "typeName": "SolutionComponent",
            "qualifiedName": qualified_name,
            "displayName": display_name,
            "description": attributes.get('Description', {}).get('value'),
            "solutionComponentType": attributes.get('Solution Component Type', {}).get('value'),
            "versionIdentifier": attributes.get('Version Identifier', {}).get('value'),
            "plannedDeployedImplementationType": attributes.get('Planned Deployed Implementation Type', {}).get('value'),
            "userDefinedStatus": attributes.get('User Defined Status', {}).get('value'),
            "URL": attributes.get('URL', {}).get('value'),
            "effectiveFrom": attributes.get('Effective From', {}).get('value'),
            "effectiveTo": attributes.get('Effective To', {}).get('value')
        }
        
        # Additional/Extended
        for key in ['Additional Properties', 'Extended Properties']:
            val = attributes.get(key, {}).get('value')
            if val:
                prop_body[key.lower().replace(' ', '')] = json.loads(val) if isinstance(val, str) else val

        # 2. Relationships
        actor_guids = set(attributes.get('Actors', {}).get('guid_list', []))
        blueprint_guids = set(attributes.get('In Solution Blueprints', {}).get('guid_list', []))
        supply_chain_guids = set(attributes.get('In Information Supply Chains', {}).get('guid_list', []))
        parent_comp_guids = set(attributes.get('Parent Components', {}).get('guid_list', []))
        keywords = set(attributes.get('Search Keywords', {}).get('value', []))

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.original_text

            body = body_slimmer({
                "class": "UpdateElementRequestBody",
                "mergeUpdate": merge_update,
                "properties": prop_body
            })
            await self.client._async_update_solution_component(guid, body)
            self.parsed_output["guid"] = guid
            
            await self._sync_all_rels(guid, supply_chain_guids, parent_comp_guids, actor_guids, blueprint_guids, keywords, not merge_update)
            
            if journal_entry:
                await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)

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

            guid = await self.client._async_create_solution_component(body)
            if guid:
                self.parsed_output["guid"] = guid
                await self._sync_all_rels(guid, supply_chain_guids, parent_comp_guids, actor_guids, blueprint_guids, keywords, replace_all=True)
                if journal_entry:
                    await self.client._async_add_note_in_dr_e(qualified_name, display_name, journal_entry)
                
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Component '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.original_text

    async def _sync_all_rels(self, guid: str, sc_guids: Set[str], parent_guids: Set[str], actor_guids: Set[str], bp_guids: Set[str], keywords: Set[str], replace_all: bool):
        rel_els = await self._get_component_related_elements(guid)
        
        # 1. Supply Chains
        as_is_sc = set(rel_els.get("supply_chain_guids", []))
        await self.sync_members(as_is_sc, sc_guids,
                               lambda sc: self.client._async_link_design_to_implementation(sc, guid, None),
                               lambda sc: self.client._async_detach_design_from_implementation(sc, guid),
                               replace_all)
                               
        # 2. Parent Components
        as_is_parents = set(rel_els.get("parent_component_guids", []))
        await self.sync_members(as_is_parents, parent_guids,
                               lambda p: self.client._async_link_subcomponent(p, guid, None),
                               lambda p: self.client._async_detach_sub_component(p, guid, None),
                               replace_all)
                               
        # 3. Actors
        as_is_actors = set(rel_els.get("actor_guids", []))
        await self.sync_members(as_is_actors, actor_guids,
                               lambda a: self.client._async_link_component_to_actor(a, guid, None),
                               lambda a: self.client._async_detach_component_actor(a, guid, None),
                               replace_all)
                               
        # 4. Blueprints
        as_is_bps = set(rel_els.get("blueprint_guids", []))
        await self.sync_members(as_is_bps, bp_guids,
                               lambda bp: self.client._async_link_solution_component_to_blueprint(bp, guid, {"class": "NewRelationshipRequestBody", "properties": {"class": "SolutionBlueprintCompositionProperties", "typeName": "SolutionBlueprintComposition", "description": "linked by Dr.Egeria v2"}}),
                               lambda bp: self.client._async_detach_solution_component_from_blueprint(bp, guid, None),
                               replace_all)
        
        # 5. Keywords
        as_is_kw = set(rel_els.get("keywords_list", {}).keys())
        kw_map = rel_els.get("keywords_list", {})
        await self.sync_members(as_is_kw, keywords,
                               lambda k: self.client._async_add_search_keyword_to_element(guid, k),
                               lambda k: self.client._async_remove_search_keyword(kw_map[k]),
                               replace_all)

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

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Information Supply Chain")

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_info_supply_chain_by_guid(guid)
        except PyegeriaException:
            return None

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        qualified_name = self.parsed_output.get("qualified_name")
        if not qualified_name:
            return None
        try:
            res = await self.client._async_get_info_supply_chain_by_name(qualified_name)
            if isinstance(res, list) and len(res) > 0:
                return res[0]
            return res if isinstance(res, dict) else None
        except PyegeriaException:
            return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        merge_update = attributes.get('Merge Update', {}).get('value', True)
        journal_entry = attributes.get('Journal Entry', {}).get('value')
        
        prop_body = {
            "class": "InformationSupplyChainProperties",
            "typeName": "InformationSupplyChain",
            "qualifiedName": qualified_name,
            "displayName": display_name,
            "description": attributes.get('Description', {}).get('value'),
            "scope": attributes.get('Scope', {}).get('value'),
            "purposes": attributes.get('Purposes', {}).get('value'),
            "version": attributes.get('Version Identifier', {}).get('value'),
            "effectiveFrom": attributes.get('Effective From', {}).get('value'),
            "effectiveTo": attributes.get('Effective To', {}).get('value')
        }

        in_sc_guids = set(attributes.get('In Information Supply Chain', {}).get('guid_list', []))
        nested_sc_guids = set(attributes.get('Nested Information Supply Chains', {}).get('guid_list', []))

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.original_text

            body = set_update_body("InformationSupplyChain", attributes)
            body['properties'] = prop_body
            await self.client._async_update_info_supply_chain(guid, body)
            self.parsed_output["guid"] = guid
            
            # Sync parents/nested
            await self._sync_rels(guid, in_sc_guids, nested_sc_guids, not merge_update)
            
            if journal_entry:
                await self.client._async_add_note_in_dr_e(qualified_name, display_name, journal_entry)

            logger.success(f"Updated Supply Chain '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = set_create_body("InformationSupplyChain", attributes)
            body['properties'] = prop_body
            
            guid = await self.client._async_create_info_supply_chain(body)
            if guid:
                self.parsed_output["guid"] = guid
                await self._sync_rels(guid, in_sc_guids, nested_sc_guids, replace_all=True)
                if journal_entry:
                    await self.client._async_add_note_in_dr_e(qualified_name, display_name, journal_entry)
                
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Supply Chain '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.original_text

    async def _sync_rels(self, guid: str, parent_guids: Set[str], nested_guids: Set[str], replace_all: bool):
        rel_els = await self._get_supply_chain_rel_elements(guid)
        
        # 1. Parents
        as_is_parents = set(rel_els.get("parent_guids", []))
        await self.sync_members(as_is_parents, parent_guids,
                               lambda p: self.client._async_compose_info_supply_chains(p, guid, None),
                               lambda p: self.client._async_decompose_info_supply_chains(p, guid, None),
                               replace_all)
                               
        # 2. Nested
        as_is_nested = set(rel_els.get("nested_guids", []))
        await self.sync_members(as_is_nested, nested_guids,
                               lambda n: self.client._async_compose_info_supply_chains(guid, n, None),
                               lambda n: self.client._async_decompose_info_supply_chains(guid, n, None),
                               replace_all)

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

class SolutionLinkProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Component and Supply Chain Peer Linking.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec(self.command.object_type)

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.command.object_type
        attributes = self.parsed_output["attributes"]
        
        id1 = attributes.get('Component1', {}).get('guid') or attributes.get('Segment1', {}).get('guid')
        id2 = attributes.get('Component2', {}).get('guid') or attributes.get('Segment2', {}).get('guid')
        label = attributes.get('Wire Label', {}).get('value') or attributes.get('Link Label', {}).get('value')
        description = attributes.get('Description', {}).get('value')
        
        if not (id1 and id2):
            return self.command.raw_block

        if verb in ["Link", "Attach", "Add"]:
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "SolutionLinkingWireProperties" if "Component" in object_type else "InformationSupplyChainLinkProperties",
                    "label": label,
                    "description": description,
                    "effectiveFrom": attributes.get('Effective From', {}).get('value'),
                    "effectiveTo": attributes.get('Effective To', {}).get('value')
                }
            }
            if "Component" in object_type:
                await self.client._async_link_solution_linking_wire(id1, id2, body)
            else:
                await self.client._async_link_peer_info_supply_chains(id1, id2, body)
            
            logger.success(f"Linked {object_type} via '{label}'")
            return f"\n\n# {verb} {object_type}\n\nLinked {id1} to {id2} via {label}"

        elif verb in ["Detach", "Unlink", "Remove"]:
            body = {"class": "DeleteRelationshipRequestBody"}
            if "Component" in object_type:
                await self.client._async_detach_solution_linking_wire(id1, id2, body)
            else:
                await self.client._async_unlink_peer_info_supply_chains(id1, id2, body)
                
            logger.success(f"Detached {object_type} via '{label}'")
            return f"\n\n# {verb} {object_type}\n\nDetached {id1} from {id2} via {label}"

        return self.command.original_text
