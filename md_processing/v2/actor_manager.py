"""
Actor Manager Processors for Dr.Egeria v2.
"""
from typing import Dict, Any, Optional
from loguru import logger

from pyegeria import PyegeriaException, NO_ELEMENTS_FOUND
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.common_md_utils import (
    set_actor_manager_prop_body, set_create_body, set_update_body,
    update_element_dictionary, set_rel_request_body, set_rel_prop_body,
    set_delete_rel_request_body, _to_egeria_type_name
)

class ActorManagerProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Actor Profiles (Teams, Organizations, Person, IT Profile) and Actor Roles.
    """

    async def apply_changes(self) -> str:
        """
        Execute the create/update action.
        """
        verb = self.command.verb
        object_type = self.command.object_type
        attributes = self.parsed_output.get("attributes", {})
        qualified_name = self.parsed_output.get("qualified_name")
        display_name = self.parsed_output.get("display_name")
        guid = self.parsed_output.get("guid")

        # Use canonical egeria type name for property construction
        egeria_type = self.egeria_type_name or object_type
        
        props = set_actor_manager_prop_body(egeria_type, qualified_name, attributes)

        if verb == "Create":
            body = set_create_body(egeria_type, attributes)
            body["properties"] = props

            if object_type == "Perspective":
                raw_guid = await self.client.actor_manager._async_create_perspective(body=body)
            elif object_type == "Skill":
                raw_guid = await self.client.actor_manager._async_create_skill(body=body)
            elif "Role" in object_type:
                raw_guid = await self.client.actor_manager._async_create_actor_role(body=body)
            else:
                raw_guid = await self.client.actor_manager._async_create_actor_profile(body=body)

            new_guid = self.extract_guid_or_raise(raw_guid, f"Create {object_type}")
            self.parsed_output["guid"] = new_guid
            update_element_dictionary(qualified_name, {'guid': new_guid, 'display_name': display_name})
            logger.success(f"Created {object_type} '{display_name}' with GUID {new_guid}")
            return await self.render_result_markdown(new_guid)

        if verb == "Update":
            if not guid:
                 raise PyegeriaException(f"GUID missing for Update of {object_type} {qualified_name}")

            body = set_update_body(egeria_type, attributes)
            body["properties"] = props

            if object_type == "Perspective":
                await self.client.actor_manager._async_update_perspective(perspective_guid=guid, body=body)
            elif object_type == "Skill":
                await self.client.actor_manager._async_update_skill(skill_guid=guid, body=body)
            elif "Role" in object_type:
                await self.client.actor_manager._async_update_actor_role(actor_role_guid=guid, body=body)
            else:
                await self.client.actor_manager._async_update_actor_profile(actor_profile_guid=guid, body=body)

            logger.success(f"Updated {object_type} '{display_name}' (GUID: {guid})")
            return await self.render_result_markdown(guid)

        return self.command.raw_block

class ActorManagerLinkProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Actor Manager relationship links.
    """

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.canonical_object_type or self.command.object_type
        attributes = self.parsed_output.get("attributes", {})
        egeria_type = self.egeria_type_name or object_type
        
        # Determine the link type and resolve IDs using canonical names from spec
        if object_type == "Team Structure":
            # Canonical: Super Team, Sub Team
            source_guid = attributes.get("Super Team", {}).get("guid")
            target_guid = attributes.get("Sub Team", {}).get("guid")
            
            if verb in ["Link", "Attach", "Add"]:
                body = set_rel_request_body(egeria_type, attributes)
                body["properties"] = set_rel_prop_body(egeria_type, attributes)
                await self.client.people_organizer._async_link_team_structure(
                    super_team_guid=source_guid, subteam_guid=target_guid, body=body
                )
            elif verb in ["Detach", "Remove", "Unlink"]:
                body = set_delete_rel_request_body(egeria_type, attributes)
                await self.client.people_organizer._async_detach_team_structure(
                    super_team_guid=source_guid, subteam_guid=target_guid, body=body
                )
        
        elif "Role Appointment" in object_type:
            if "Person" in object_type:
                # Canonical: Person Role, Person
                role_guid = attributes.get("Person Role", {}).get("guid")
                profile_guid = attributes.get("Person", {}).get("guid")
                link_coro = self.client.actor_manager._async_link_person_role_to_profile
                detach_coro = self.client.actor_manager._async_detach_person_role_from_profile
            elif "Team" in object_type:
                # Canonical: Team Role, Team
                role_guid = attributes.get("Team Role", {}).get("guid")
                profile_guid = attributes.get("Team", {}).get("guid")
                link_coro = self.client.actor_manager._async_link_team_role_to_profile
                detach_coro = self.client.actor_manager._async_detach_team_role_from_profile
            elif "IT Profile" in object_type:
                # Canonical: IT Profile Role, IT Profile
                role_guid = attributes.get("IT Profile Role", {}).get("guid")
                profile_guid = attributes.get("IT Profile", {}).get("guid")
                link_coro = self.client.actor_manager._async_link_it_profile_role_to_profile
                detach_coro = self.client.actor_manager._async_detach_it_profile_role_from_it_profile
            else:
                 raise PyegeriaException(f"Unsupported role appointment type: {object_type}")
            
            if verb in ["Link", "Attach", "Add"]:
                body = set_rel_request_body(egeria_type, attributes)
                body["properties"] = set_rel_prop_body(egeria_type, attributes)
                await link_coro(role_guid, profile_guid, body=body)
            elif verb in ["Detach", "Remove", "Unlink"]:
                body = set_delete_rel_request_body(egeria_type, attributes)
                await detach_coro(role_guid, profile_guid, body=body)
        
        elif object_type in ["Team Leader", "Team Membership", "Assignment Scope"]:
            # Team Leader -> Team, Team Leader Role
            # Team Membership -> Team, Team Member Role
            # Assignment Scope -> Scope Element, Assigned Actor
            scope_guid = (attributes.get("Team", {}).get("guid") or
                          attributes.get("Scope Element", {}).get("guid"))
            actor_guid = (attributes.get("Team Leader Role", {}).get("guid") or
                          attributes.get("Team Member Role", {}).get("guid") or
                          attributes.get("Assigned Actor", {}).get("guid"))

            # Force AssignmentScope for property body construction to ensure correct class name
            rel_egeria_type = "AssignmentScope"
            if verb in ["Link", "Attach", "Add"]:
                body = set_rel_request_body(rel_egeria_type, attributes)
                body["properties"] = set_rel_prop_body(rel_egeria_type, attributes)
                await self.client.actor_manager._async_link_assignment_scope(
                    scope_element_guid=scope_guid, actor_guid=actor_guid, body=body
                )
            elif verb in ["Detach", "Remove", "Unlink"]:
                body = set_delete_rel_request_body(rel_egeria_type, attributes)
                await self.client.actor_manager._async_detach_assignment_scope(
                    scope_element_guid=scope_guid, actor_guid=actor_guid, body=body
                )

        elif object_type == "Associated Skill Set":
            # AssociatedSkillSet: Actor (end1) <-> SkillSet collection (end2)
            # Note: end1 must be an Actor-subtype entity (e.g. ActorRole), not ActorProfile.
            actor_guid = attributes.get("Actor Name", {}).get("guid")
            skill_set_guid = attributes.get("SkillSet Name", {}).get("guid")
            if verb in ["Link", "Attach", "Add"]:
                body = set_rel_request_body(egeria_type, attributes)
                body["properties"] = set_rel_prop_body(egeria_type, attributes)
                await self.client.collection_manager._async_link_associated_skill_set(
                    actor_guid=actor_guid, skill_set_guid=skill_set_guid, body=body
                )
            elif verb in ["Detach", "Remove", "Unlink"]:
                body = set_delete_rel_request_body(egeria_type, attributes)
                await self.client.collection_manager._async_detach_associated_skill_set(
                    actor_guid=actor_guid, skill_set_guid=skill_set_guid, body=body
                )

        else:
             raise PyegeriaException(f"Unsupported Link object type: {object_type}")

        logger.success(f"{verb}ed {object_type}")
        return f"Successfully {verb.lower()}ed {object_type} relationship."
