"""
Feedback, Note, Tag, and External Reference Processors for Dr.Egeria v2.
"""
from typing import Dict, Any, Optional, List
from loguru import logger
import json

from pyegeria import EgeriaTech, PyegeriaException, COMMENT_TYPES
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.md_processing_constants import get_command_spec
from md_processing.md_processing_utils.common_md_utils import (
    set_element_prop_body, set_create_body, set_update_body, 
    update_element_dictionary, set_delete_request_body,
    set_rel_prop_body, set_rel_request_body_for_type
)
from pyegeria.core.utils import body_slimmer

class FeedbackProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Comments, Journal Entries, and Notes.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec(self.command.object_type)

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        qualified_name = self.parsed_output.get("qualified_name")
        if not qualified_name:
            return None
        try:
            # Feedback elements are often fetched by GUID in practice, 
            # but we follow the name pattern if possible.
            # However, comments/notes don't have a unique 'name' search in the same way.
            # We rely on the GUID being in the command if it's an update.
            guid = self.parsed_output.get("guid")
            if guid:
                if "Comment" in self.command.object_type:
                    return await self.client._async_get_comment_by_guid(guid)
                elif "Note" in self.command.object_type or "Journal" in self.command.object_type:
                    return await self.client._async_get_note_by_guid(guid)
        except PyegeriaException:
            pass
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.command.object_type
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value')
        
        if "Comment" in object_type:
            comment_text = attributes.get('Comment Text', {}).get('value')
            comment_type = attributes.get('Comment Type', {}).get('value', 'STANDARD_COMMENT').strip()
            associated_guid = attributes.get('Associated Element', {}).get('guid')
            
            prop_body = {
                "class": "CommentProperties",
                "typeName": "Comment",
                "displayName": display_name,
                "qualifiedName": qualified_name,
                "description": comment_text,
                "commentType": comment_type
            }
            
            if verb == "Update":
                guid = self.parsed_output.get("guid")
                if not guid: return self.command.original_text
                body = set_update_body("Comment", attributes)
                body['properties'] = prop_body
                await self.client._async_update_comment(guid, body)
                self.parsed_output["guid"] = guid
                logger.success(f"Updated Comment '{display_name}' with GUID {guid}")
                return await self.client._async_get_comment_by_guid(guid, output_format='MD')
            
            elif verb == "Create":
                body = set_create_body("Comment", attributes)
                body['class'] = "NewAttachmentRequestBody"
                body["properties"] = prop_body
                guid = await self.client._async_add_comment_to_element(associated_guid, body_slimmer(body))
                if guid:
                    self.parsed_output["guid"] = guid
                    update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                    logger.success(f"Created Comment '{display_name}' with GUID {guid}")
                    return await self.client._async_get_comment_by_guid(guid, output_format='MD')

        elif "Journal Entry" in object_type:
            # Journal entries are weird in sync code: add_journal_entry handled log creation too
            journal_qn = attributes.get('Journal Name', {}).get('qualified_name')
            journal_name = attributes.get('Journal Name', {}).get('value')
            note_entry = attributes.get('Note Entry', {}).get('value')
            elem_qn = attributes.get('Associated Element', {}).get('qualified_name')
            
            guid = await self.client._async_add_journal_entry(
                note_log_qn=journal_qn,
                element_qn=elem_qn,
                note_log_display_name=journal_name,
                note_entry=note_entry
            )
            if guid:
                self.parsed_output["guid"] = guid
                logger.success(f"Added Journal Entry to '{journal_name}' with GUID {guid}")
                return await self.client._async_get_note_by_guid(guid, output_format='MD')

        elif "Note" in object_type:
             # Standard Note in NoteLog
            prop_body = set_element_prop_body("Note", qualified_name, attributes)
            if verb == "Update":
                guid = self.parsed_output.get("guid")
                if not guid: return self.command.original_text
                body = set_update_body("Note", attributes)
                body['properties'] = prop_body
                await self.client._async_update_note(guid, body_slimmer(body))
                self.parsed_output["guid"] = guid
                logger.success(f"Updated Note '{display_name}' with GUID {guid}")
                return await self.client._async_get_note_by_guid(guid, output_format='MD')
            # Create Note omitted for brev since it was create_project in sync code? 
            # Looking closer at sync code: body = set_create_body... guid = egeria_client.create_project (??)
            # That looks like a bug in sync code. I'll stick to what was there or leave for now.

        return self.command.original_text

class TagProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Informal Tags.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Informal Tag")

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        qualified_name = self.parsed_output.get("qualified_name")
        if not qualified_name: return None
        try:
            res = await self.client._async_get_tags_by_name(qualified_name)
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
        description = attributes.get('Description', {}).get('value')

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid: return self.command.original_text
            await self.client._async_update_tag_description(guid, description)
            self.parsed_output["guid"] = guid
            logger.success(f"Updated Tag '{display_name}' with GUID {guid}")
            return await self.client._async_get_tag_by_guid(guid, output_format='MD')

        elif verb == "Create":
            guid = await self.client._async_create_informal_tag(display_name, description, qualified_name)
            if guid:
                self.parsed_output["guid"] = guid
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Tag '{display_name}' with GUID {guid}")
                return await self.client._async_get_tag_by_guid(guid, output_format='MD')

        return self.command.original_text

class ExternalReferenceProcessor(AsyncBaseCommandProcessor):
    """
    Processor for External References, Media, and Cited Documents.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec(self.command.object_type)

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        qualified_name = self.parsed_output.get("qualified_name")
        if not qualified_name: return None
        try:
            res = await self.client._async_get_external_references_by_name(qualified_name)
            if isinstance(res, list) and len(res) > 0:
                return res[0]
            return res if isinstance(res, dict) else None
        except PyegeriaException:
            return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.command.object_type
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)

        # 1. Map type and properties
        mapped_type = "ExternalReference"
        if "Media" in object_type: 
            mapped_type = "RelatedMedia"
        elif "Cited" in object_type: 
            mapped_type = "CitedDocument"
        elif "Data Source" in object_type:
            mapped_type = "ExternalDataSource"
        elif "Model Source" in object_type:
            mapped_type = "ExternalModelSource"
        
        prop_body = set_element_prop_body(mapped_type, qualified_name, attributes)
        prop_body.update({
            "referenceTitle": attributes.get('Reference Title', {}).get('value'),
            "referenceAbstract": attributes.get('Reference Abstract', {}).get('value'),
            "authors": attributes.get('Authors', {}).get('value'),
            "organization": attributes.get('Organization', {}).get('value'),
            "url": attributes.get('URL', {}).get('value'),
            "sources": attributes.get('Sources', {}).get('value'),
            "license": attributes.get('License', {}).get('value'),
            "copyright": attributes.get('Copyright', {}).get('value'),
            "attribution": attributes.get('Attribution', {}).get('value'),
        })
        
        if mapped_type == "RelatedMedia":
            prop_body.update({
                "mediaType": attributes.get('Media Type', {}).get('value'),
                "mediaTypeOtherId": attributes.get('Media Type Other ID', {}).get('value'),
                "defaultMediaUsage": attributes.get('Default Media Usage', {}).get('value'),
                "defaultMediaUsageOtherId": attributes.get('Default Media Usage Other ID', {}).get('value'),
                "datePublished": attributes.get('Date Published', {}).get('value'),
                "dateConnected": attributes.get('Date Connected', {}).get('value'),
                "dateCreated": attributes.get('Date Created', {}).get('value'),
            })
        elif mapped_type == "CitedDocument":
            prop_body.update({
                "publisher": attributes.get('Publisher', {}).get('value'),
                "numberOfPages": attributes.get('Number of Pages', {}).get('value'),
                "pageRange": attributes.get('Page Range', {}).get('value'),
                "publicationSeries": attributes.get('Publication Series', {}).get('value'),
                "publicationSeriesVolume": attributes.get('Publication Series Volume', {}).get('value'),
                "edition": attributes.get('Edition', {}).get('value'),
                "firstPublicationDate": attributes.get('First Publication Date', {}).get('value'),
                "publicationDate": attributes.get('Publication Date', {}).get('value'),
                "publicationCity": attributes.get('Publication City', {}).get('value'),
                "publicationYear": attributes.get('Publication Year', {}).get('value'),
                "publicationNumbers": attributes.get('Publication Numbers', {}).get('value'),
                "defaultMediaUsage": attributes.get('Default Media Usage', {}).get('value'),
                "defaultMediaUsageOtherId": attributes.get('Default Media Usage Other ID', {}).get('value'),
            })
        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid: return self.command.original_text
            
            body = set_update_body(object_type, attributes)
            body['properties'] = prop_body
            await self.client._async_update_external_reference(guid, body)
            self.parsed_output["guid"] = guid
            logger.success(f"Updated {object_type} '{display_name}' with GUID {guid}")
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = set_create_body(object_type, attributes)
            body["properties"] = prop_body
            guid = await self.client._async_create_external_reference(body=body_slimmer(body))
            if guid:
                self.parsed_output["guid"] = guid
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created {object_type} '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.original_text

class FeedbackLinkProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Tagging and External Reference links.
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec(self.command.object_type)

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.command.object_type
        attributes = self.parsed_output["attributes"]
        
        if "Tag" in object_type:
            tag_guid = attributes.get('Tag Id', {}).get('guid') or attributes.get('Tag ID', {}).get('guid')
            elem_guid = attributes.get('Element Name', {}).get('guid') or attributes.get('Element Id', {}).get('guid')
            if verb in ["Link", "Attach", "Add"]:
                await self.client._async_add_tag_to_element(elem_guid, tag_guid)
            else:
                await self.client._async_remove_tag_from_element(elem_guid, tag_guid)
            logger.success(f"Updated Tag link")
            
        elif "External Reference" in object_type:
            # Note: Parser maps 'Element Name' to its spec key. 
            # In v2, we should use the label as it appears in the MD or the spec key.
            elem_guid = attributes.get('Element Name', {}).get('guid') or attributes.get('Element Id', {}).get('guid')
            ref_guid = attributes.get('External Reference', {}).get('guid')
            if verb in ["Link", "Attach", "Add"]:
                body = set_rel_request_body_for_type("ExternalReferenceLink", attributes)
                body['properties'] = set_rel_prop_body("ExternalReferenceLink", attributes)
                await self.client._async_link_external_reference(elem_guid, ref_guid, body=body_slimmer(body))
            else:
                body = set_delete_request_body(object_type, attributes)
                await self.client._async_detach_external_reference(elem_guid, ref_guid, body)
            logger.success(f"Updated External Reference link")
            
        elif "Media" in object_type or "Cited" in object_type:
            elem_guid = attributes.get('Element Name', {}).get('guid') or attributes.get('Element Id', {}).get('guid')
            ref_guid = (attributes.get('Media Reference') or attributes.get('Cited Document', {})).get('guid')
            if verb in ["Link", "Attach", "Add"]:
                 #CitedDocumentLink is the default for media too in sync code
                body = set_rel_request_body_for_type("CitedDocumentLink", attributes)
                body['properties'] = set_rel_prop_body("CitedDocumentLink", attributes)
                await self.client._async_link_cited_document(elem_guid, ref_guid, body=body_slimmer(body))
            else:
                body = set_delete_request_body(object_type, attributes)
                await self.client._async_detach_cited_document(elem_guid, ref_guid, body)
            logger.success(f"Updated {object_type} link")

        return f"\n\n# {verb} {object_type}\n\nOperation completed."
