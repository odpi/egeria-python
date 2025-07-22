"""
This file contains project-related object_action functions for processing Egeria Markdown
"""

from rich.markdown import Markdown

from md_processing.md_processing_utils.common_md_utils import (debug_level, print_msg, is_valid_iso_date, setup_log)
from md_processing.md_processing_utils.extraction_utils import (extract_command, process_simple_attribute)
from md_processing.md_processing_utils.md_processing_constants import ALWAYS, ERROR, INFO, pre_command
from pyegeria._globals import NO_PROJECTS_FOUND
from pyegeria.project_manager_omvs import ProjectManager

setup_log()

def process_per_proj_upsert_command(egeria_client: ProjectManager, txt: str, directive: str = "display") -> str | None:
    """
    Processes a personal project create or update object_action by extracting key attributes such as
    glossary name, language, description, and usage from the given cell.

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.md_processing_utils.common_md_utils import set_debug_level

    command = extract_command(txt)
    print(Markdown(f"# {command}\n"))

    object = command.split()
    object_type = f"{object[1]} {object[2]}"
    object_action = object[0]
    set_debug_level(directive)

    project_name = process_simple_attribute(txt, ['Project Name'])
    description = process_simple_attribute(txt, ['Description'])
    project_identifier = process_simple_attribute(txt, ['Project Identifier'])
    project_status = process_simple_attribute(txt, ['Status'])
    project_phase = process_simple_attribute(txt, ['Project Phase'])
    project_health = process_simple_attribute(txt, ['Project Health'])
    start_date = process_simple_attribute(txt, ['Start Date'])
    planned_end_date = process_simple_attribute(txt, ['Planned End Date'])
    print(Markdown(f"{pre_command} `\'{command}\'` for project: `{project_name}` with directive: `{directive}` "))

    project_display = (f"\n* Command: {command}\n\t* Project: {project_name}\n\t"
                       f"* Status: {project_status}\n\t* Description: {description}\n\t"
                       f"* Phase: {project_phase}\n\t* Health: {project_health}\n\t"
                       f"* Start Date: {start_date}\n\t* Planned End Date: {planned_end_date}\n")

    def validate_project(obj_action: str) -> tuple[bool, bool, str, str]:
        valid = True
        msg = ""
        known_guid = None
        known_q_name = None

        project_details = egeria_client.get_projects_by_name(project_name)
        if project_details == NO_PROJECTS_FOUND:
            project_exists = False
        else:
            project_exists = True

        if project_name is None:
            msg = f"* {ERROR}Project name is missing\n"
            valid = False
        if project_status is None:
            msg += f"* {INFO}No Project status found\n"

        if description is None:
            msg += f"* {INFO}No Description found\n"

        if project_identifier is None:
            msg += f"* {INFO}No Project Identifier found\n"

        if project_phase is None:
            msg += f"* {INFO}No Project Phase found\n"

        if project_health is None:
            msg += f"* {INFO}No Project Health found\n"

        if start_date is None:
            msg += f"* {INFO}No Start Date found\n"
        elif not is_valid_iso_date(start_date):
            msg += f"* {ERROR}Start Date is not a valid ISO date of form  YYYY-MM-DD\n"
            valid = False

        if planned_end_date is None:
            msg += f"* {INFO} No Planned End Date found\n"
        elif not is_valid_iso_date(planned_end_date):
            msg += f"* {ERROR}Planned End Date is not a valid ISO date of form  YYYY-MM-DD\n"
            valid = False

        if obj_action == "Update":
            q_name = process_simple_attribute(txt, 'Qualified Name')

            if not project_exists:
                msg += f"* {ERROR}Project {project_name} does not exist\n"
                valid = False
            if len(project_details) > 1 and project_exists:
                msg += f"* {ERROR}More than one project with name {project_name} found\n"
                valid = False
            if len(project_details) == 1:
                known_guid = project_details[0]['elementHeader'].get('guid', None)
                known_q_name = project_details[0]['glossaryProperties'].get('qualifiedName', None)
            if q_name is None:
                msg += f"* {INFO}Qualified Name is missing => can use known qualified name of {known_q_name}\n"
                valid = True
            elif q_name != known_q_name:
                msg += (f"* {ERROR}Project {project_name} qualifiedName mismatch between {q_name} and {known_q_name}\n")
                valid = False
            if valid:
                msg += project_display
                msg += f"* -->Project {project_name} exists and can be updated\n"
            else:
                msg += f"* --> validation failed\n"
            msg += '---'
            print(Markdown(msg))
            return valid, project_exists, known_guid, known_q_name

        elif obj_action == "Create":
            if project_exists:
                msg += f"\n{ERROR}Project {project_name} already exists"
            else:
                msg += f"\n-->It is valid to create Project \'{project_name}\' with:\n"
            print(Markdown(msg))
            return valid, project_exists, known_guid, known_q_name

    if directive == "display":
        print(Markdown(project_display))
        return None
    elif directive == "validate":
        valid, project_exists, known_guid, known_q_name = validate_project(object_action)
        return valid
    elif directive == "process":
        valid, project_exists, known_guid, known_q_name = validate_project(object_action)
        if valid:
            if object_action == "Create":
                if project_exists:
                    print(f"\n{ERROR}Project {project_name} already exists\n")
                    return None
                else:
                    project_guid = egeria_client.create_personal_project(project_name, description, project_identifier,
                                                                         project_status, project_phase, project_health,
                                                                         start_date, planned_end_date)
                    if project_guid:
                        print_msg(ALWAYS, f"Created Project {project_name} with GUID {project_guid}", debug_level)
                        return egeria_client.get_project_by_guid(project_guid, output_format='MD')
                    else:
                        print_msg(ERROR, f"Failed to create Project {project_name}", debug_level)
                        return None
            elif object_action == "Update":
                if not project_exists:
                    print(f"\n{ERROR}Project {project_name} does not exist\n")
                    return None
                else:
                    project_guid = egeria_client.update_personal_project(known_guid, project_name, description,
                                                                         project_identifier, project_status,
                                                                         project_phase, project_health, start_date,
                                                                         planned_end_date)
                    if project_guid:
                        print_msg(ALWAYS, f"Updated Project {project_name} with GUID {project_guid}", debug_level)
                        return egeria_client.get_project_by_guid(project_guid, output_format='MD')
                    else:
                        print_msg(ERROR, f"Failed to update Project {project_name}", debug_level)
                        return None
        else:
            return None
