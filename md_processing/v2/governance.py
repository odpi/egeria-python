"""
Governance Officer Processors for Dr.Egeria v2.
"""
from typing import Dict, Any, Optional, List
from loguru import logger
import json
from inflect import engine

from pyegeria import EgeriaTech, PyegeriaException
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.md_processing_constants import get_command_spec
from md_processing.md_processing_utils.common_md_utils import (
    set_gov_prop_body, set_create_body, set_update_body, 
    update_element_dictionary, set_delete_request_body,
    set_peer_gov_def_request_body, set_rel_prop_body,
    set_rel_request_body, ALL_GOVERNANCE_DEFINITIONS
)
from pyegeria.core.utils import body_slimmer

class GovernanceProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Governance Definitions.
    """

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_governance_definition_by_guid(guid)
        except PyegeriaException:
            return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.command.object_type
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        
        # 1. Properties
        prop_body = set_gov_prop_body(object_type, qualified_name, attributes)

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.original_text
            self.parsed_output["guid"] = guid

            body = body_slimmer({
                "class": "UpdateElementRequestBody",
                "properties": prop_body
            })
            await self.client._async_update_governance_definition(guid, body)
            
            # Relationships
            await self._sync_rels(guid, attributes)
            
            logger.success(f"Updated {object_type} '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = set_create_body(object_type, attributes)
            body['properties'] = prop_body
            
            guid = await self.client._async_create_governance_definition(body_slimmer(body))
            if guid:
                self.parsed_output["guid"] = guid
                await self._sync_rels(guid, attributes)
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created {object_type} '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.original_text

    async def _sync_rels(self, guid: str, attributes: Dict[str, Any]):
        to_be_supports = attributes.get("Supports Policies", {}).get("guid_list", [])
        to_be_drivers = attributes.get("Governance Drivers", {}).get("guid_list", [])
        
        for policy in to_be_supports:
            await self.client._async_attach_supporting_definitions(policy, "GovernanceImplementation", guid)
        for driver in to_be_drivers:
            await self.client._async_attach_supporting_definitions(driver, "GovernanceResponse", guid)

class GovernanceLinkProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Governance Peer/Supporting/Governed-By links.
    """



    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.command.object_type
        attributes = self.parsed_output["attributes"]
        
        guid1 = (attributes.get('Definition 1') or attributes.get('Referenceable', {})).get('guid')
        guid2 = (attributes.get('Definition 2') or attributes.get('Governance Definition', {})).get('guid')
        label = attributes.get('Link Label', {}).get('value', "")
        
        if not (guid1 and guid2):
            return self.command.original_text

        # Determine relationship type name
        rel_type = ""
        if "Peer" in object_type:
            parts = object_type.split()
            word = parts[2] if len(parts) >= 3 else parts[-1]
            inflector = engine()
            singular = inflector.singular_noun(word) or word
            rel_type = f"Governance{singular}Link"
        elif "Supporting" in object_type:
            rel_type = object_type.replace(' ', '')
        elif "Governed By" in object_type:
            rel_type = "GovernedBy" # Standard for Referenceable -> GovDef

        if verb in ["Link", "Attach", "Add"]:
            if "Peer" in object_type or "Supporting" in object_type:
                body = set_peer_gov_def_request_body(object_type, attributes)
                if "Supporting" in object_type:
                    body['properties'] = {
                        "class": "SupportingDefinitionProperties",
                        "typeName": rel_type,
                        "rationale": attributes.get('Rationale', {}).get('value'),
                        "effectiveFrom": attributes.get('Effective From', {}).get('value'),
                        "effectiveTo": attributes.get('Effective To', {}).get('value'),
                    }
                if "Peer" in object_type:
                    await self.client._async_link_peer_definitions(guid1, rel_type, guid2, body)
                else:
                    await self.client._async_attach_supporting_definitions(guid1, rel_type, guid2, body)
            elif "Governed By" in object_type:
                body = body_slimmer({
                    "class": "NewRelationshipRequestBody",
                    "properties": set_rel_prop_body(object_type, attributes)
                })
                await self.client._async_attach_governed_by_definition(guid1, guid2, body)
                
            logger.success(f"Linked Governance {object_type}")
            return f"\n\n# {verb} {object_type}\n\nOperation completed."

        elif verb in ["Detach", "Unlink", "Remove"]:
            body = set_delete_request_body(object_type, attributes)
            if "Peer" in object_type:
                await self.client._async_detach_peer_definitions(guid1, rel_type, guid2, body)
            elif "Supporting" in object_type:
                await self.client._async_detach_supporting_definitions(guid1, rel_type, guid2, body)
            elif "Governed By" in object_type:
                await self.client._async_detach_governed_by_definitions(guid1, guid2, body)
                
            logger.success(f"Detached Governance {object_type}")
            return f"\n\n# {verb} {object_type}\n\nOperation completed."

        return self.command.original_text

class GovernanceContextProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Governance Definition Context retrieval.
    """



    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        guid = self.parsed_output.get("guid")
        output_format = attributes.get('Output Format', {}).get('value', 'LIST')
        
        if not guid:
            return self.command.original_text
            
        body = set_update_body(self.command.object_type, attributes)
        struct = await self.client._async_get_gov_def_in_context(guid, body=body, output_format=output_format)
        
        if output_format.upper() == "DICT":
            return f"\n# Context Graph for {guid}\n\n```json\n{json.dumps(struct, indent=4)}\n```"
        return f"\n# Context Graph for {guid}\n\n{struct}"
