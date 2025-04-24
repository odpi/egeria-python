"""
This file contains glossary-related command functions for processing Egeria Markdown
"""
from typing import Optional

from rich.markdown import Markdown

from pyegeria.egeria_tech_client import EgeriaTech
from md_processing.utils.common_utils import (
    debug_level, print_msg, ALWAYS, ERROR, INFO, WARNING, pre_command, EXISTS_REQUIRED
)
from md_processing.utils.extraction_utils import (
    extract_command_plus, extract_command, process_simple_attribute
)
from md_processing.utils.validation_utils import (
    process_element_identifiers, update_a_command
)
from md_processing.utils.display_utils import (
    GLOSSARY_NAME_LABELS
)
from pyegeria.dr_egeria_state import update_element_dictionary

def process_glossary_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a glossary create or update command by extracting key attributes such as
    glossary name, language, description, and usage from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """

    command, object_type, object_action = extract_command_plus(txt)
    from md_processing.utils.common_utils import set_debug_level
    set_debug_level(directive)

    glossary_name = process_simple_attribute(txt, GLOSSARY_NAME_LABELS, ERROR)
    print(Markdown(
        f"{pre_command} `{object_action}` `{object_type}`  for glossary: `\'{glossary_name}\'` with directive: `"
        f"{directive}` "))
    language = process_simple_attribute(txt, ['Language'], INFO)
    description = process_simple_attribute(txt, ['Description'], INFO)
    usage = process_simple_attribute(txt, ['Usage'], INFO)
    q_name = process_simple_attribute(txt, ['Qualified Name'], INFO)
    valid = True

    if glossary_name is None:
        valid = False
        known_q_name = None
        known_guid = None
        glossary_exists = False
    else:
        element_labels = GLOSSARY_NAME_LABELS
        element_labels.append('Display Name')
        known_q_name, known_guid, valid, glossary_exists = process_element_identifiers(egeria_client, object_type,
                                                                                       element_labels, txt,
                                                                                       object_action, None)
    glossary_display = (f"\n* Command: `{command}`\n\t* Glossary Name: {glossary_name}\n\t"
                        f"* Language: {language}\n\t* Description:\n{description}\n"
                        f"* Usage: {usage}\n")

    if object_action == 'Update':
        guid = process_simple_attribute(txt, ['GUID', 'guid', 'Guid'])
        glossary_display += f"* Qualified Name: `{q_name}`\n\t* GUID: {guid}\n\n"
        if not glossary_exists:
            msg = f"Glossary can't be updated; `{glossary_name}` not found"
            print_msg("ERROR", msg, debug_level)
            valid = False
        else:
            msg = f"Glossary can be updated; `{glossary_name}` found"
            print_msg(ALWAYS, msg, debug_level)


    elif object_action == "Create":
        if glossary_exists:
            msg = f"Glossary `{glossary_name}` can't be created because it already exists.\n"
            print_msg("ERROR", msg, debug_level)
            valid = False
        elif valid:
            msg = f"It is valid to create Glossary `{glossary_name}` with:\n"
            print_msg("ALWAYS", msg, debug_level)

    if directive == "display":
        print(Markdown(glossary_display))
        return None

    elif directive == "validate":
        if valid:
            print(Markdown(glossary_display))
        else:
            msg = f"Validation failed for Glossary `{glossary_name}`\n"
            print_msg(ERROR, msg, debug_level)
            print(Markdown(glossary_display))

        return valid

    elif directive == "process":
        if valid:
            print(Markdown(glossary_display))
        else:
            if glossary_exists and object_action == "Create":
                msg = f"Create failed because glossary `{glossary_name}` exists - changing `Create` to `Update` in processed output \n"
                print_msg(ERROR, msg, debug_level)
                print(Markdown(glossary_display))
                return update_a_command(txt, command, object_type, known_q_name, known_guid)
            else:
                return None
        if object_action == "Update":
            if not glossary_exists:
                print(f"\n{ERROR}Glossary `{glossary_name}` does not exist! Updating result document with Create "
                      f"command\n")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)

            body = {
                "class": "ReferenceableRequestBody", "elementProperties": {
                    "class": "GlossaryProperties", "qualifiedName": known_q_name, "description": description,
                    "language": language, "usage": usage
                    }
                }
            egeria_client.update_glossary(known_guid, body)
            print_msg(ALWAYS, f"Updated Glossary `{glossary_name}` with GUID {known_guid}", debug_level)
            update_element_dictionary(known_q_name, {
                'guid': known_guid, 'display_name': glossary_name
                })
            return egeria_client.get_glossary_by_guid(known_guid, output_format='MD')
        elif object_action == "Create":
            glossary_guid = None

            if glossary_exists:
                print(f"\nGlossary `{glossary_name}` already exists and result document updated\n")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)
            else:
                glossary_guid = egeria_client.create_glossary(glossary_name, description, language, usage)
                if glossary_guid:
                    print_msg(ALWAYS, f"Created Glossary `{glossary_name}` with GUID {glossary_guid}", debug_level)
                    return egeria_client.get_glossary_by_guid(glossary_guid, output_format='MD')
                else:
                    print_msg(ERROR, f"Failed to create Glossary `{glossary_name}`", debug_level)
                    return None
        else:
            return None
    else:
        return None

def process_glossary_list_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a glossary list command by extracting key attributes such as
    output format and search string from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.utils.common_utils import set_debug_level
    from md_processing.utils.display_utils import OUTPUT_LABELS, SEARCH_LABELS, ELEMENT_OUTPUT_FORMATS

    command = extract_command(txt)
    set_debug_level(directive)
    print(Markdown(f"{pre_command} `{command}` with directive: `{directive}`"))

    output_format = process_simple_attribute(txt, OUTPUT_LABELS)
    output_format = output_format.upper() if output_format else "MD"
    if output_format not in ELEMENT_OUTPUT_FORMATS:
        print_msg(WARNING, f"Output format {output_format} not recognized, using MD", debug_level)
        output_format = "MD"

    search_string = process_simple_attribute(txt, SEARCH_LABELS)

    if directive == "display":
        print(Markdown(f"\n* Command: {command}\n\t* Output Format: {output_format}\n\t* Search String: {search_string}"))
        return None
    elif directive == "validate":
        print(Markdown(f"\n* Command: {command}\n\t* Output Format: {output_format}\n\t* Search String: {search_string}"))
        return True
    elif directive == "process":
        print(Markdown(f"\n* Command: {command}\n\t* Output Format: {output_format}\n\t* Search String: {search_string}"))
        return egeria_client.list_glossaries(output_format=output_format, search_string=search_string)


def process_glossary_structure_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a glossary structure command by extracting key attributes such as
    glossary name and output format from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.utils.common_utils import set_debug_level
    from md_processing.utils.display_utils import OUTPUT_LABELS, ELEMENT_OUTPUT_FORMATS

    command = extract_command(txt)
    set_debug_level(directive)
    print(Markdown(f"{pre_command} `{command}` with directive: `{directive}`"))

    glossary_name = process_simple_attribute(txt, GLOSSARY_NAME_LABELS, ERROR)
    output_format = process_simple_attribute(txt, OUTPUT_LABELS)
    output_format = output_format.upper() if output_format else "MD"
    if output_format not in ELEMENT_OUTPUT_FORMATS:
        print_msg(WARNING, f"Output format {output_format} not recognized, using MD", debug_level)
        output_format = "MD"

    if glossary_name is None:
        print_msg(ERROR, "No glossary name found", debug_level)
        return None

    known_q_name, known_guid, valid, glossary_exists = process_element_identifiers(egeria_client, "Glossary",
                                                                                  GLOSSARY_NAME_LABELS, txt,
                                                                                  EXISTS_REQUIRED, None)
    if not glossary_exists:
        print_msg(ERROR, f"Glossary {glossary_name} not found", debug_level)
        return None

    if directive == "display":
        print(Markdown(f"\n* Command: {command}\n\t* Glossary Name: {glossary_name}\n\t* Output Format: {output_format}"))
        return None
    elif directive == "validate":
        print(Markdown(f"\n* Command: {command}\n\t* Glossary Name: {glossary_name}\n\t* Output Format: {output_format}"))
        return True
    elif directive == "process":
        print(Markdown(f"\n* Command: {command}\n\t* Glossary Name: {glossary_name}\n\t* Output Format: {output_format}"))
        return egeria_client.get_glossary_structure(known_guid, output_format=output_format)