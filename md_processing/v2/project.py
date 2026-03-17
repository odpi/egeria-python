"""
Project Processors for Dr.Egeria v2.
"""
from typing import Dict, Any, Optional, List
from loguru import logger

from pyegeria import EgeriaTech, PyegeriaException
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.md_processing_constants import get_command_spec
from md_processing.md_processing_utils.common_md_utils import (
    set_element_prop_body, set_create_body, set_update_body, 
    set_object_classifications, update_element_dictionary,
    set_delete_request_body, set_rel_request_body_for_type
)
from pyegeria.core.utils import body_slimmer

class ProjectProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Projects.
    """

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_project_by_guid(guid)
        except PyegeriaException:
            return None


    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        
        # Ensure we use "Project" as the base type for the property package
        base_type = "Project"
        project_types = ["Campaign", "Task", "Personal Project", "Study Project"]
        
        # 1. Properties
        # ProjectManager expects 'name' instead of 'displayName' and 'plannedEndDate' instead of 'endDate'
        prop_body = {
            "class": "ProjectProperties",
            "typeName": self.command.object_type.replace(" ", ""),
            "qualifiedName": qualified_name,
            "name": display_name,
            "description": attributes.get('Description', {}).get('value'),
            "identifier": attributes.get('Identifier', {}).get('value'),
            "projectStatus": attributes.get('Project Status', {}).get('value'),
            "projectPhase": attributes.get('Project Phase', {}).get('value'),
            "projectHealth": attributes.get('Project Health', {}).get('value'),
            "startDate": attributes.get('Start Date', {}).get('value'),
            "plannedEndDate": attributes.get('End Date', {}).get('value'),
        }

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                 return self.command.original_text
            self.parsed_output["guid"] = guid

            body = set_update_body(base_type, attributes)
            body['properties'] = prop_body
            await self.client._async_update_project(guid, body)
            
            logger.success(f"Updated Project '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            body = set_create_body(base_type, attributes)
            # Apply classifications based on the actual object_type (e.g., Campaign)
            body["initialClassifications"] = set_object_classifications(self.command.object_type, attributes, project_types)
            body["properties"] = prop_body
            
            guid = await self.client._async_create_project(body=body_slimmer(body))
            if guid:
                self.parsed_output["guid"] = guid
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Project '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.original_text

class ProjectLinkProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Project Hierarchy and Dependency.
    """



    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = self.command.object_type
        attributes = self.parsed_output["attributes"]
        
        parent_guid = attributes.get('Parent Project', {}).get('guid')
        child_guid = attributes.get('Child Project', {}).get('guid')
        label = attributes.get('Link Label', {}).get('value', "")
        
        if not (parent_guid and child_guid):
            return self.command.original_text

        if verb in ["Link", "Attach", "Add"]:
            if "Hierarchy" in object_type:
                await self.client._async_set_project_hierarchy(project_guid=child_guid, parent_project_guid=parent_guid)
            else:
                body = set_rel_request_body_for_type("ProjectDependency", attributes)
                await self.client._async_set_project_dependency(project_guid=child_guid, upstream_project_guid=parent_guid, body=body_slimmer(body))
            
            logger.success(f"Linked Project {object_type}")
            return f"\n\n# {verb} {object_type}\n\nLinked {child_guid} to {parent_guid} ({label})"

        elif verb in ["Detach", "Unlink", "Remove"]:
            body = set_delete_request_body(object_type, attributes)
            if "Hierarchy" in object_type:
                await self.client._async_clear_project_hierarchy(child_guid, parent_guid, body)
            else:
                await self.client._async_clear_project_dependency(child_guid, parent_guid, body)
                
            logger.success(f"Detached Project {object_type}")
            return f"\n\n# {verb} {object_type}\n\nDetached {child_guid} from {parent_guid} ({label})"

        return self.command.original_text
