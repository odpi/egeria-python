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
    set_object_classifications, update_element_dictionary,
    async_add_note_in_dr_e
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
        prop_body["language"] = attributes.get('Language', {}).get('value', None)
        prop_body["usage"] = attributes.get('Usage', {}).get('value', None)
        
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        status = attributes.get('Status', {}).get('value', None)
        journal_entry = attributes.get('Journal Entry', {}).get('value')

        if verb == "Update":
            guid = self.parsed_output.get("guid")
            if not guid and self.as_is_element:
                guid = self.as_is_element['elementHeader']['guid']
                
            if not guid:
                logger.error(f"Cannot update {display_name}: GUID not found")
                return self.command.original_text

            body = set_update_body("Glossary", attributes)
            body['properties'] = self.filter_update_properties(prop_body, body.get('mergeUpdate', True))
            
            await self.client._async_update_collection(guid, body)
            self.parsed_output["guid"] = guid
            # if status:
            #     await self.client._async_update_collection_status(guid, status)
            
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
        journal_entry = attributes.get('Journal Entry', {}).get('value')

        # 1. Properties
        prop_body = set_element_prop_body("GlossaryTerm", qualified_name, attributes)
        prop_body["aliases"] = attributes.get('Aliases', {}).get('value', None)
        prop_body["summary"] = attributes.get('Summary', {}).get('value', None)
        prop_body["examples"] = attributes.get('Examples', {}).get('value', None)
        prop_body["abbreviation"] = attributes.get('Abbreviation', {}).get('value', None)
        prop_body["usage"] = attributes.get('Usage', {}).get('value', None)
        prop_body["user_defined_status"] = attributes.get('UserDefinedStatus', {}).get('value', None)
        
        # 2. Extract collection GUIDs
        # We may have one or more collections listed (Glossary Name, Folders)
        glossary_guids = attributes.get("Glossary Name", {}).get("guid_list", [])
        if not glossary_guids and attributes.get("Glossary Name", {}).get("guid"):
            glossary_guids = [attributes["Glossary Name"]["guid"]]
            
        folder_guids = attributes.get("Folders", {}).get("guid_list", [])
        if not folder_guids and attributes.get("Folders", {}).get("guid"):
            folder_guids = [attributes["Folders"]["guid"]]
            
        to_be_collection_guids = list(set(glossary_guids) | set(folder_guids))
        to_be_collection_guids = [g for g in to_be_collection_guids if g]

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.original_text

            body = set_update_body("GlossaryTerm", attributes)
            body['properties'] = self.filter_update_properties(prop_body, body.get('mergeUpdate', True))
            
            await self.client._async_update_glossary_term(guid, body)
            self.parsed_output["guid"] = guid
            if status:
                await self.client._async_update_glossary_term_status(guid, status)
            
            # Sync memberships: if merge_update is True, we only add (replace_all=False)
            # If merge_update is False, we synchronize (replace_all=True)
            await self._sync_term_memberships(guid, to_be_collection_guids, not merge_update)
            
            if journal_entry:
                try:
                    j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                    if j_guid:
                        self.add_related_result("Journal Entry", j_guid)
                except Exception as e:
                    self.add_related_result("Journal Entry", status="failure", message=str(e))
            
            logger.success(f"Updated Term '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = set_create_body("GlossaryTerm", attributes)
            body["properties"] = prop_body
            
            # Anchor Scope check
            anchor_scope_guid = attributes.get("Anchor Scope", {}).get('guid', None)
            if anchor_scope_guid is None and glossary_guids:
                body["anchorScopeGUID"] = glossary_guids[0] # Use first glossary as anchor if not specified

            guid = await self.client._async_create_glossary_term(body=body)
            if guid:
                self.parsed_output["guid"] = guid
                # For Create, we always want to ensure it's in all listed collections
                await self._sync_term_memberships(guid, to_be_collection_guids, replace_all=True)

                if journal_entry:
                    try:
                        j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                        if j_guid:
                            self.add_related_result("Journal Entry", j_guid)
                    except Exception as e:
                        self.add_related_result("Journal Entry", status="failure", message=str(e))

                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Term '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.original_text

    async def _sync_term_memberships(self, term_guid: str, to_be_guids: List[str], replace_all: bool):
        """Standardized helper for term collection sync."""
        current_collections = await self.client._async_get_attached_collections(term_guid)
        as_is_guids = {c['elementHeader']['guid'] for c in current_collections} if current_collections and not isinstance(current_collections, str) else set()
        
        # Build map of GUID to name for current collections for better feedback
        guid_to_name = {}
        if current_collections and not isinstance(current_collections, str):
            for c in current_collections:
                guid = c['elementHeader']['guid']
                name = c.get('properties', {}).get('displayName') or c.get('properties', {}).get('qualifiedName') or guid
                guid_to_name[guid] = name
                
        to_be_set = set(to_be_guids)
        
        async def add_fn(collection_guid):
            await self.client._async_add_to_collection(collection_guid, term_guid)
            
        async def remove_fn(collection_guid):
            await self.client._async_remove_from_collection(collection_guid, term_guid)
            
        sync_res = await self.sync_members(as_is_guids, to_be_set, add_fn, remove_fn, replace_all)
        
        if sync_res.get("added") or sync_res.get("removed"):
            added_names = []
            for g in sync_res["added"]:
                # Try to find name in input attributes if it matched a guid
                added_names.append(g) # For now just GUID
                
            removed_names = [guid_to_name.get(g, g) for g in sync_res["removed"]]
            
            msg = f"Sync: Added {len(sync_res['added'])} collection(s), Removed {len(sync_res['removed'])} collection(s)."
            if sync_res["added"]:
                msg += f" Added: {', '.join(sync_res['added'])}"
            if sync_res["removed"]:
                msg += f" Removed: {', '.join(removed_names)}"
                
            self.add_related_result("Collection Memberships Sync", message=msg)
            
        if sync_res.get("errors"):
            self.add_related_result("Collection Memberships Sync", status="failure", message="; ".join(sync_res["errors"]))

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
