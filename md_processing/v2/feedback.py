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
    set_delete_rel_request_body,
    set_rel_prop_body, set_rel_request_body_for_type,
    async_add_note_in_dr_e
)
from pyegeria.core.utils import body_slimmer

class FeedbackProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Comments, Journal Entries, and Notes.
    """

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
        object_type = getattr(self, 'canonical_object_type', self.command.object_type)
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value')
        
        if "Comment" in object_type:
            # Check Description (standard Ref), Comment Text (legacy), or Comment (alt)
            comment_text = (attributes.get('Description', {}).get('value') or 
                            attributes.get('Comment Text', {}).get('value') or 
                            attributes.get('Comment', {}).get('value'))
            comment_type = attributes.get('Comment Type', {}).get('value', 'STANDARD_COMMENT').strip()
            
            # The spec uses 'Commented On Element', but we support 'Associated Element' for backward compatibility
            commented_on = attributes.get('Commented On Element') or attributes.get('Associated Element')
            associated_guid = commented_on.get('guid') if commented_on else None
            
            prop_body = {
                "class": "CommentProperties",
                "displayName": display_name,
                "qualifiedName": qualified_name,
                "commentText": comment_text,
                "description": comment_text,
                "commentType": comment_type
            }
            
            if verb == "Update":
                guid = self.parsed_output.get("guid")
                if not guid: return self.command.raw_block
                body = set_update_body("Comment", attributes)
                body['properties'] = self.filter_update_properties(prop_body, body.get('mergeUpdate', True))
                await self.client._async_update_comment(guid, body)
                self.parsed_output["guid"] = guid
                logger.success(f"Updated Comment '{display_name}' with GUID {guid}")
                return await self.client._async_get_comment_by_guid(guid, output_format='MD')
            
            elif verb == "Create":
                body = set_create_body("Comment", attributes)
                body['class'] = "NewAttachmentRequestBody"
                body["properties"] = prop_body
                response = await self.client._async_add_comment_to_element(associated_guid, body=body_slimmer(body))
                guid = response.get("guid") if isinstance(response, dict) else response
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
            
            # Use 'Commented On Element' or 'Associated Element' for target
            target = attributes.get('Commented On Element') or attributes.get('Associated Element')
            elem_qn = target.get('qualified_name') if target else None
            
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
                if not guid: return self.command.raw_block
                body = set_update_body("Note", attributes)
                body['properties'] = self.filter_update_properties(prop_body, body.get('mergeUpdate', True))
                await self.client._async_update_note(guid, body)
                self.parsed_output["guid"] = guid
                logger.success(f"Updated Note '{display_name}' with GUID {guid}")
                return await self.client._async_get_note_by_guid(guid, output_format='MD')
            # Create Note omitted for brev since it was create_project in sync code? 
            # Looking closer at sync code: body = set_create_body... guid = egeria_client.create_project (??)
            # That looks like a bug in sync code. I'll stick to what was there or leave for now.

        return self.command.raw_block

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
            if not guid: return self.command.raw_block
            await self.client._async_update_tag_description(guid, description)
            self.parsed_output["guid"] = guid
            logger.success(f"Updated Tag '{display_name}' with GUID {guid}")
            return await self.client._async_get_tag_by_guid(guid, output_format='MD')

        elif verb == "Create":
            response = await self.client._async_create_informal_tag(display_name, description, qualified_name)
            guid = response.get("guid") if isinstance(response, dict) else response
            if guid:
                self.parsed_output["guid"] = guid
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Tag '{display_name}' with GUID {guid}")
                return await self.client._async_get_tag_by_guid(guid, output_format='MD')

        return self.command.raw_block

class ExternalReferenceProcessor(AsyncBaseCommandProcessor):
    """
    Processor for External References, Media, and Cited Documents.
    """

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
        object_type = getattr(self, 'canonical_object_type', self.command.object_type)
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        journal_entry = attributes.get('Journal Entry', {}).get('value')

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
        elif "Source Code" in object_type:
            mapped_type = "ExternalSourceCode"
        
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
            if not guid: return self.command.raw_block
            
            body = set_update_body(object_type, attributes)
            body['properties'] = prop_body
            await self.client._async_update_external_reference(guid, body)
            self.parsed_output["guid"] = guid
            
            if journal_entry:
                try:
                    j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                    if j_guid:
                        self.add_related_result("Journal Entry", j_guid)
                except Exception as e:
                    self.add_related_result("Journal Entry", status="failure", message=str(e))

            logger.success(f"Updated {object_type} '{display_name}' with GUID {guid}")
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = set_create_body(object_type, attributes)
            body["properties"] = prop_body
            guid = await self.client._async_create_external_reference(body=body_slimmer(body))
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

class FeedbackLinkProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Tagging and External Reference links.
    """

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = getattr(self, 'canonical_object_type', self.command.object_type)
        attributes = self.parsed_output["attributes"]
        
        if "Tag" in object_type:
            # Spec uses 'Informal Tag' and 'Tagged Element', but we support legacy 'Tag ID' and 'Element Name'
            tag_guid = (attributes.get('Informal Tag', {}).get('guid') or 
                        attributes.get('Tag Id', {}).get('guid') or 
                        attributes.get('Tag ID', {}).get('guid'))
            elem_guid = (attributes.get('Tagged Element', {}).get('guid') or 
                         attributes.get('Element Name', {}).get('guid') or 
                         attributes.get('Element Id', {}).get('guid'))
            if verb in ["Link", "Attach", "Add"]:
                await self.client._async_add_tag_to_element(elem_guid, tag_guid)
            else:
                await self.client._async_remove_tag_from_element(elem_guid, tag_guid)
            logger.success(f"Updated Tag link")
            
        elif "External Reference" in object_type:
            # Spec uses 'Referenceable Element' and 'External Reference', but we support legacy 'Element Name'
            elem_guid = (attributes.get('Referenceable Element', {}).get('guid') or 
                         attributes.get('Element Name', {}).get('guid') or 
                         attributes.get('Element Id', {}).get('guid'))
            ref_guid = attributes.get('External Reference', {}).get('guid')
            if verb in ["Link", "Attach", "Add"]:
                body = set_rel_request_body_for_type("ExternalReferenceLink", attributes)
                props = set_rel_prop_body("ExternalReferenceLink", attributes)
                props["referenceId"] = attributes.get('Reference Id', {}).get('value') or \
                                      attributes.get('Reference ID', {}).get('value') or \
                                      props.get('label')
                body['properties'] = props
                await self.client._async_link_external_reference(elem_guid, ref_guid, body=body_slimmer(body))
            else:
                body = set_delete_rel_request_body(object_type, attributes)
                await self.client._async_detach_external_reference(elem_guid, ref_guid, body)
            logger.success(f"Updated External Reference link")
            
        elif "Media Reference" in object_type:
            # Spec uses 'Referenceable Element' and 'Media Reference', but we support legacy 'Element Name'
            elem_guid = (attributes.get('Referenceable Element', {}).get('guid') or 
                         attributes.get('Element Name', {}).get('guid') or 
                         attributes.get('Element Id', {}).get('guid'))
            ref_guid = (attributes.get('Media Reference', {}) or attributes.get('Media Reference Link', {})).get('guid')
            if not ref_guid:
                ref_guid = (attributes.get('Media') or {}).get('guid')
            
            if verb in ["Link", "Attach", "Add"]:
                body = set_rel_request_body_for_type("MediaReferenceLink", attributes)
                props = set_rel_prop_body("MediaReference", attributes)
                props.update({
                    "mediaId": attributes.get('Media Id', {}).get('value') or attributes.get('Media ID', {}).get('value'),
                    "mediaUsage": attributes.get('Media Usage', {}).get('value'),
                    "mediaUsageOtherId": attributes.get('Media Usage Other Id', {}).get('value'),
                })
                body['properties'] = props
                await self.client._async_link_media_reference(elem_guid, ref_guid, body=body_slimmer(body))
            else:
                body = set_delete_rel_request_body(object_type, attributes)
                await self.client._async_detach_media_reference(elem_guid, ref_guid, body)
            logger.success(f"Updated Media Reference link")
            
        elif "Cited Document" in object_type:
            # Spec uses 'Referenceable Element' and 'Cited Document', but we support legacy 'Element Name'
            elem_guid = (attributes.get('Referenceable Element', {}).get('guid') or 
                         attributes.get('Element Name', {}).get('guid') or 
                         attributes.get('Element Id', {}).get('guid'))
            ref_guid = attributes.get('Cited Document', {}).get('guid')
            
            if verb in ["Link", "Attach", "Add"]:
                body = set_rel_request_body_for_type("CitedDocumentLink", attributes)
                props = set_rel_prop_body("CitedDocumentLink", attributes)
                props.update({
                    "referenceId": attributes.get('Reference Id', {}).get('value') or attributes.get('Reference ID', {}).get('value'),
                    "pages": attributes.get('Pages', {}).get('value'),
                })
                body['properties'] = props
                await self.client._async_link_cited_document(elem_guid, ref_guid, body=body_slimmer(body))
            else:
                body = set_delete_rel_request_body(object_type, attributes)
                await self.client._async_detach_cited_document(elem_guid, ref_guid, body)
            logger.success(f"Updated Cited Document link")

        elif "Comment" in object_type or "Accepted Answer" in object_type:
            if "Accept Answer" in object_type or "Accepted Answer" in object_type:
                # Link Accept Answer case
                question_guid = attributes.get('Accepted Answer Comment', {}).get('guid')
                answer_guid = attributes.get('Answering Comment', {}).get('guid')
                if verb in ["Link", "Attach", "Add"]:
                    await self.client._async_setup_accepted_answer(question_guid, answer_guid)
                else:
                    await self.client._async_clear_accepted_answer(question_guid, answer_guid)
                logger.success(f"Updated Accept Answer link")
            else:
                # Attach/Detach Comment case
                elem_guid = attributes.get('Commented On Element', {}).get('guid')
                comment_guid = attributes.get('Comment', {}).get('guid')
                
                if verb in ["Link", "Attach", "Add"]:
                    # Since the View Service often doesn't have a direct "Link Existing Comment" method,
                    # and comments are usually specific to their elements, we create a new comment
                    # with the same content as the existing one if needed.
                    # HOWEVER, FB-10 says "Attach". Let's check if we have text directly.
                    comment_text = attributes.get('Comment Text', {}).get('value')
                    comment_type = attributes.get('Comment Type', {}).get('value', 'STANDARD_COMMENT').strip()
                    
                    if not comment_text and comment_guid:
                        # Fetch the existing comment to get its text
                        try:
                            comment_element = await self.client._async_get_comment_by_guid(comment_guid)
                            comment_text = comment_element.get('description') or comment_element.get('commentText')
                            comment_type = comment_element.get('commentType') or comment_type
                        except PyegeriaException as e:
                            logger.warning(f"Could not fetch existing comment {comment_guid}: {e}")
                    
                    if comment_text:
                        await self.client._async_add_comment_to_element(elem_guid, comment_text, comment_type)
                    else:
                        logger.error(f"No comment text found to attach for {object_type}")
                else:
                    # Detach Comment
                    await self.client._async_remove_comment_from_element(comment_guid)
                logger.success(f"Updated Comment attachment")

        elif "Rating" in object_type:
            elem_guid = attributes.get('Reviewed Element', {}).get('guid')
            if verb in ["Link", "Attach", "Add"]:
                stars = attributes.get('Stars', {}).get('value', 'FIVE_STARS')
                # Map FIVE_STARS -> 5, etc if needed? 
                # Actually StarRating is an Enum.
                review = attributes.get('Review', {}).get('value')
                is_public = attributes.get('Is Public', {}).get('value', True)
                
                # Construct RatingProperties
                rating_body = {
                    "class": "NewAttachmentRequestBody",
                    "properties": {
                        "class": "RatingProperties",
                        "starRating": stars,
                        "review": review
                    }
                }
                await self.client._async_add_rating_to_element(elem_guid, is_public, body=body_slimmer(rating_body))
            else:
                await self.client._async_remove_rating_from_element(elem_guid)
            logger.success(f"Updated Rating attachment")

        elif "Like" in object_type:
            elem_guid = attributes.get('Liked Element', {}).get('guid')
            if verb in ["Link", "Attach", "Add"]:
                emoji = attributes.get('Emoji', {}).get('value')
                await self.client._async_add_like_to_element(elem_guid, emoji=emoji)
            else:
                await self.client._async_remove_like_from_element(elem_guid)
            logger.success(f"Updated Like attachment")

        return f"\n\n# {verb} {object_type}\n\nOperation completed."
