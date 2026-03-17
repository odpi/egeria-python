"""
Standard Glossary and Term Processors for Dr.Egeria v2.
"""
from typing import Dict, Any, Optional, List
from loguru import logger

from pyegeria import EgeriaTech, PyegeriaException
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.md_processing_constants import get_command_spec
from md_processing.md_processing_utils.common_md_utils import (
    set_element_prop_body, set_create_body, set_update_body, 
    set_object_classifications, update_element_dictionary
)

class GlossaryProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Glossary collections (Glossary, Taxonomy, CanonicalVocabulary).
    """

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_glossary_by_guid(guid)
        except PyegeriaException:
            return None


    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.command.object_type
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        
        # 1. Prepare properties
        prop_body = set_element_prop_body("Glossary", qualified_name, attributes)
        prop_body["languager"] = attributes.get('Language', {}).get('value', None)
        prop_body["usage"] = attributes.get('Usage', {}).get('value', None)
        
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        status = attributes.get('Status', {}).get('value', None)

        if verb == "Update":
            guid = self.parsed_output.get("guid")
            if not guid and self.as_is_element:
                guid = self.as_is_element['elementHeader']['guid']
                
            if not guid:
                 logger.error(f"Cannot update {display_name}: GUID not found")
                 return self.command.original_text

            body = set_update_body("Glossary", attributes)
            body['properties'] = prop_body
            
            await self.client._async_update_collection(guid, body)
            self.parsed_output["guid"] = guid
            # if status:
            #     await self.client._async_update_collection_status(guid, status)
                
            logger.success(f"Updated {object_type} '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = set_create_body(object_type, attributes)
            body["initialClassifications"] = set_object_classifications(
                object_type, attributes, ["Taxonomy", "CanonicalVocabulary"]
            )
            
            # Type-specific classification logic
            if object_type == "Taxonomy":
                if 'Taxonomy' in body["initialClassifications"]:
                    body["initialClassifications"]['Taxonomy']['organizingPrinciple'] = attributes.get('Organizing Principle', {}).get('value', None)
            elif object_type == "CanonicalVocabulary":
                if 'CanonicalVocabulary' in body["initialClassifications"]:
                    body["initialClassifications"]['CanonicalVocabulary']['usage'] = attributes.get('Usage', {}).get('value', None)

            body["properties"] = prop_body
            
            guid = await self.client._async_create_collection(body=body)
            if guid:
                self.parsed_output["guid"] = guid
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created {object_type} '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)
            
        return self.command.original_text

class TermProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Glossary Terms.
    """

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_term_by_guid(guid)
        except PyegeriaException:
            return None


    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        status = attributes.get('Status', {}).get('value', None)
        merge_update = attributes.get('Merge Update', {}).get('value', True)

        # 1. Properties
        prop_body = set_element_prop_body("GlossaryTerm", qualified_name, attributes)
        prop_body["aliases"] = attributes.get('Aliases', {}).get('value', None)
        prop_body["summary"] = attributes.get('Summary', {}).get('value', None)
        prop_body["examples"] = attributes.get('Examples', {}).get('value', None)
        prop_body["abbreviation"] = attributes.get('Abbreviation', {}).get('value', None)
        prop_body["usage"] = attributes.get('Usage', {}).get('value', None)
        prop_body["user_defined_status"] = attributes.get('UserDefinedStatus', {}).get('value', None)
        
        glossary_guid = attributes.get("Glossary", {}).get('guid', None)
        folder_guids = attributes.get("Folder", {}).get("guid_list", [])
        to_be_collection_guids = [glossary_guid] + (folder_guids if isinstance(folder_guids, list) else [folder_guids])
        to_be_collection_guids = [g for g in to_be_collection_guids if g]

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.original_text

            body = set_update_body("GlossaryTerm", attributes)
            body['properties'] = prop_body
            
            await self.client._async_update_glossary_term(guid, body)
            self.parsed_output["guid"] = guid
            if status:
                await self.client._async_update_glossary_term_status(guid, status)
            
            # Async sync memberships
            await self._sync_term_memberships(guid, to_be_collection_guids, merge_update)
            
            logger.success(f"Updated Term '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = set_create_body("GlossaryTerm", attributes)
            body["properties"] = prop_body
            
            # Anchor Scope check
            anchor_scope_guid = attributes.get("Anchor Scope", {}).get('guid', None)
            if anchor_scope_guid is None and glossary_guid:
                body["anchorScopeGUID"] = glossary_guid

            guid = await self.client._async_create_glossary_term(body=body)
            if guid:
                self.parsed_output["guid"] = guid
                await self._sync_term_memberships(guid, to_be_collection_guids, replace_all=True)
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Term '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.original_text

    async def _sync_term_memberships(self, term_guid: str, to_be_guids: List[str], replace_all: bool):
        """Standardized helper for term collection sync."""
        # 1. Fetch current (As-Is)
        # We need to find which collections this term is currently in.
        # This usually involves getting terms' collections.
        # For simplicity in this first port, we'll implement the logic here.
        
        # Note: In v1 this was handled by sync_collection_memberships
        # For v2, we'll use the AsyncBaseCommandProcessor.sync_members helper
        
        current_collections = await self.client._async_get_attached_collections(term_guid)
        as_is_guids = {c['elementHeader']['guid'] for c in current_collections} if current_collections and not isinstance(current_collections, str) else set()
        to_be_set = set(to_be_guids)
        
        async def add_fn(collection_guid):
            await self.client._async_add_term_to_collection(term_guid, collection_guid)
            
        async def remove_fn(collection_guid):
            await self.client._async_remove_term_from_collection(term_guid, collection_guid)
            
        await self.sync_members(as_is_guids, to_be_set, add_fn, remove_fn, replace_all)

class TermRelationshipProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Term-to-Term relationships (Link, Attach, Add).
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Term Relationship")

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        # Relationship lookup is more complex; for now we return None to force creation
        return None

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        term1_guid = attributes.get('Term 1', {}).get('guid', None)
        term1_qname = attributes.get('Term 1', {}).get('qualified_name', None)
        term2_guid = attributes.get('Term 2', {}).get('guid', None)
        term2_qname = attributes.get('Term 2', {}).get('qualified_name', None)
        relationship = attributes.get('Relationship', {}).get('value', None)
        
        if not (term1_guid and term2_guid and relationship):
            logger.error(f"TermRelationshipProcessor: Missing required identifiers")
            return self.command.original_text
            
        logger.info(f"TermRelationshipProcessor: Linking '{term1_qname}' to '{term2_qname}' via '{relationship}'")
        
        try:
            await self.client._async_add_relationship_between_terms(term1_guid, term2_guid, relationship)
            logger.success(f"Linked terms via {relationship}")
            
            # Standard v2 relationship output
            return (f"\n\n# Update Term-Term Relationship\n\n"
                    f"## Term 1 Name:\n\n{term1_qname}\n\n"
                    f"## Term 2 Name:\n\n{term2_qname}\n\n"
                    f"## Term Relationship:\n\n{relationship}")
        except PyegeriaException as e:
            logger.error(f"Failed to link terms: {e}")
            return self.command.original_text
