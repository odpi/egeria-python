"""
This file contains blueprint/solution-related command functions for processing Egeria Markdown
"""
from typing import Optional

from rich.markdown import Markdown

from pyegeria.egeria_tech_client import EgeriaTech
from md_processing.md_processing_utils.common_utils import (
    debug_level, print_msg, update_element_dictionary
)
from md_processing.md_processing_utils.extraction_utils import (
    extract_command_plus, process_simple_attribute, process_name_list, process_element_identifiers, update_a_command
)

from md_processing.md_processing_utils.md_processing_constants import (
    BLUEPRINT_NAME_LABELS, COMPONENT_NAME_LABELS, ALWAYS, ERROR, INFO, pre_command, EXISTS_REQUIRED,
    )

def process_blueprint_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a solution blueprint create or update command by extracting key attributes such as
    blueprint name, description, and usage from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting blueprint-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.md_processing_utils.common_utils import set_debug_level
    
    command, object_type, object_action = extract_command_plus(txt)
    set_debug_level(directive)

    blueprint_name = process_simple_attribute(txt, BLUEPRINT_NAME_LABELS, ERROR)
    print(Markdown(f"{pre_command} `{object_action}` `{object_type}` for blueprint: `\'{blueprint_name}\'` with directive: `{directive}` "))
    description = process_simple_attribute(txt, ['Description'], INFO)
    usage = process_simple_attribute(txt, ['Usage'], INFO)
    q_name = process_simple_attribute(txt, ['Qualified Name'], INFO)
    valid = True

    if blueprint_name is None:
        valid = False
        known_q_name = None
        known_guid = None
        blueprint_exists = False
    else:
        element_labels = BLUEPRINT_NAME_LABELS
        element_labels.append('Display Name')
        known_q_name, known_guid, valid, blueprint_exists = process_element_identifiers(egeria_client, object_type,
                                                                                       element_labels, txt,
                                                                                       object_action, None)

    blueprint_display = (f"\n* Command: `{command}`\n\t* Blueprint Name: {blueprint_name}\n\t"
                        f"* Description: {description}\n\t* Usage: {usage}\n")

    if object_action == 'Update':
        guid = process_simple_attribute(txt, ['GUID', 'guid', 'Guid'])
        blueprint_display += f"* Qualified Name: `{q_name}`\n\t* GUID: {guid}\n\n"
        if not blueprint_exists:
            msg = f"Blueprint can't be updated; `{blueprint_name}` not found"
            print_msg("ERROR", msg, debug_level)
            valid = False
        else:
            msg = f"Blueprint can be updated; `{blueprint_name}` found"
            print_msg(ALWAYS, msg, debug_level)

    elif object_action == "Create":
        if blueprint_exists:
            msg = f"Blueprint `{blueprint_name}` can't be created because it already exists.\n"
            print_msg("ERROR", msg, debug_level)
            valid = False
        elif valid:
            msg = f"It is valid to create Blueprint `{blueprint_name}` with:\n"
            print_msg("ALWAYS", msg, debug_level)

    if directive == "display":
        print(Markdown(blueprint_display))
        return None

    elif directive == "validate":
        if valid:
            print(Markdown(blueprint_display))
        else:
            msg = f"Validation failed for Blueprint `{blueprint_name}`\n"
            print_msg(ERROR, msg, debug_level)
            print(Markdown(blueprint_display))

        return valid

    elif directive == "process":
        if valid:
            print(Markdown(blueprint_display))
        else:
            if blueprint_exists and object_action == "Create":
                msg = f"Create failed because blueprint `{blueprint_name}` exists - changing `Create` to `Update` in processed output \n"
                print_msg(ERROR, msg, debug_level)
                print(Markdown(blueprint_display))
                return update_a_command(txt, command, object_type, known_q_name, known_guid)
            else:
                return None

        if object_action == "Update":
            if not blueprint_exists:
                print(f"\n{ERROR}Blueprint `{blueprint_name}` does not exist! Updating result document with Create "
                      f"command\n")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)

            body = {
                "class": "ReferenceableRequestBody", "elementProperties": {
                    "class": "SolutionBlueprintProperties", "qualifiedName": known_q_name, "description": description,
                    "usage": usage
                    }
                }
            egeria_client.update_solution_blueprint(known_guid, body)
            print_msg(ALWAYS, f"Updated Blueprint `{blueprint_name}` with GUID {known_guid}", debug_level)
            update_element_dictionary(known_q_name, {
                'guid': known_guid, 'display_name': blueprint_name
                })
            return egeria_client.get_solution_blueprint_by_guid(known_guid, output_format='MD')

        elif object_action == "Create":
            if blueprint_exists:
                print(f"\nBlueprint `{blueprint_name}` already exists and result document updated\n")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)
            else:
                blueprint_guid = egeria_client.create_solution_blueprint(blueprint_name, description, usage)
                if blueprint_guid:
                    print_msg(ALWAYS, f"Created Blueprint `{blueprint_name}` with GUID {blueprint_guid}", debug_level)
                    return egeria_client.get_solution_blueprint_by_guid(blueprint_guid, output_format='MD')
                else:
                    print_msg(ERROR, f"Failed to create Blueprint `{blueprint_name}`", debug_level)
                    return None


def process_solution_component_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a solution component create or update command by extracting key attributes such as
    component name, description, and parent components from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting component-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.md_processing_utils.common_utils import set_debug_level
    
    command, object_type, object_action = extract_command_plus(txt)
    set_debug_level(directive)

    component_name = process_simple_attribute(txt, COMPONENT_NAME_LABELS, ERROR)
    print(Markdown(f"{pre_command} `{object_action}` `{object_type}` for component: `\'{component_name}\'` with directive: `{directive}` "))
    description = process_simple_attribute(txt, ['Description'], INFO)
    q_name = process_simple_attribute(txt, ['Qualified Name'], INFO)
    valid = True

    if component_name is None:
        valid = False
        known_q_name = None
        known_guid = None
        component_exists = False
    else:
        element_labels = COMPONENT_NAME_LABELS
        element_labels.append('Display Name')
        known_q_name, known_guid, valid, component_exists = process_element_identifiers(egeria_client, object_type,
                                                                                       element_labels, txt,
                                                                                       object_action, None)

    # Get the blueprint this component is in
    blueprint_name = process_simple_attribute(txt, BLUEPRINT_NAME_LABELS)
    if blueprint_name:
        known_blueprint_q_name, known_blueprint_guid, blueprint_valid, blueprint_exists = process_element_identifiers(
            egeria_client, "Solution Blueprint", BLUEPRINT_NAME_LABELS, txt, EXISTS_REQUIRED, None)
        if not blueprint_exists:
            valid = False
    else:
        known_blueprint_q_name = None
        known_blueprint_guid = None
        blueprint_valid = True
        blueprint_exists = False

    # Get the parent components if specified
    parent_components = process_simple_attribute(txt, ['Parent Components', 'Parent Component'])
    if parent_components:
        parent_components_list, parent_q_name_list, parents_valid, parents_exist = process_name_list(
            egeria_client, 'Solution Components', txt, COMPONENT_NAME_LABELS)
        if not parents_exist:
            valid = False
    else:
        parent_components_list = None
        parent_q_name_list = None
        parents_valid = True
        parents_exist = False

    component_display = (f"\n* Command: `{command}`\n\t* Component Name: {component_name}\n\t"
                        f"* Blueprint: {blueprint_name}\n\t* Parent Components: {parent_components}\n\t"
                        f"* Description: {description}\n")

    if object_action == 'Update':
        guid = process_simple_attribute(txt, ['GUID', 'guid', 'Guid'])
        component_display += f"* Qualified Name: `{q_name}`\n\t* GUID: {guid}\n\n"
        if not component_exists:
            msg = f"Component can't be updated; `{component_name}` not found"
            print_msg("ERROR", msg, debug_level)
            valid = False
        else:
            msg = f"Component can be updated; `{component_name}` found"
            print_msg(ALWAYS, msg, debug_level)

    elif object_action == "Create":
        if component_exists:
            msg = f"Component `{component_name}` can't be created because it already exists.\n"
            print_msg("ERROR", msg, debug_level)
            valid = False
        elif valid:
            msg = f"It is valid to create Component `{component_name}` with:\n"
            print_msg("ALWAYS", msg, debug_level)

    if directive == "display":
        print(Markdown(component_display))
        return None

    elif directive == "validate":
        if valid:
            print(Markdown(component_display))
        else:
            msg = f"Validation failed for Component `{component_name}`\n"
            print_msg(ERROR, msg, debug_level)
            print(Markdown(component_display))

        return valid

    elif directive == "process":
        if valid:
            print(Markdown(component_display))
        else:
            if component_exists and object_action == "Create":
                msg = f"Create failed because component `{component_name}` exists - changing `Create` to `Update` in processed output \n"
                print_msg(ERROR, msg, debug_level)
                print(Markdown(component_display))
                return update_a_command(txt, command, object_type, known_q_name, known_guid)
            else:
                return None

        if object_action == "Update":
            if not component_exists:
                print(f"\n{ERROR}Component `{component_name}` does not exist! Updating result document with Create "
                      f"command\n")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)

            body = {
                "class": "ReferenceableRequestBody", "elementProperties": {
                    "class": "SolutionComponentProperties", "qualifiedName": known_q_name, "description": description
                    }
                }
            egeria_client.update_solution_component(known_guid, body)
            print_msg(ALWAYS, f"Updated Component `{component_name}` with GUID {known_guid}", debug_level)
            update_element_dictionary(known_q_name, {
                'guid': known_guid, 'display_name': component_name
                })

            # Update parent components if specified
            if parent_components and parents_exist and parents_valid:
                # Get the current parent components
                component_details = egeria_client.get_solution_component_by_guid(known_guid)
                current_parents = []
                if 'parentComponents' in component_details:
                    for parent in component_details['parentComponents']:
                        current_parents.append(parent.get('guid', None))
                
                # Add new parent components
                for parent in parent_q_name_list:
                    if parent not in current_parents:
                        egeria_client.add_parent_component(parent, known_guid)
                        print_msg(INFO, f"Added parent component to {component_name}", debug_level)
                
                # Remove parent components that are not in the new list
                for parent in current_parents:
                    if parent not in parent_q_name_list:
                        egeria_client.remove_parent_component(parent, known_guid)
                        print_msg(INFO, f"Removed parent component from {component_name}", debug_level)

            return egeria_client.get_solution_component_by_guid(known_guid, output_format='MD')

        elif object_action == "Create":
            if component_exists:
                print(f"\nComponent `{component_name}` already exists and result document updated\n")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)
            else:
                component_guid = egeria_client.create_solution_component(component_name, description, known_blueprint_guid)
                if component_guid:
                    print_msg(ALWAYS, f"Created Component `{component_name}` with GUID {component_guid}", debug_level)
                    
                    # Add parent components if specified
                    if parent_components and parents_exist and parents_valid:
                        for parent in parent_q_name_list:
                            egeria_client.add_parent_component(parent, component_guid)
                            print_msg(INFO, f"Added parent component to {component_name}", debug_level)
                    
                    return egeria_client.get_solution_component_by_guid(component_guid, output_format='MD')
                else:
                    print_msg(ERROR, f"Failed to create Component `{component_name}`", debug_level)
                    return None