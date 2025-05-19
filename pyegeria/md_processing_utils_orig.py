"""

This file contains functions to parse and process Egeria Markdown (Freddie)


"""

import json
from jupyter_notebook_parser import JupyterNotebookParser
import nbformat
from typing import List, Optional

import os
import re

from rich import box, print
from rich.console import Console
from rich.markdown import Markdown

from pyegeria import body_slimmer
from pyegeria._globals import NO_TERMS_FOUND, NO_GLOSSARIES_FOUND, NO_TERMS_FOUND, NO_ELEMENTS_FOUND, NO_PROJECTS_FOUND, NO_CATEGORIES_FOUND
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.project_manager_omvs import ProjectManager
from pyegeria.glossary_manager_omvs import GlossaryManager

from datetime import datetime
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))
console = Console(width=EGERIA_WIDTH)

command_list = ["Provenance",
                "Create Glossary", "Update Glossary",
                "Create Term", "Update Term",
                "Create Personal Project", "Update Personal Project",
                "Create Category", "Update Category",
                "Create Solution Blueprint", "Update Solution Blueprint"]

ERROR = "ERROR-> "
INFO = "INFO- "
WARNING = "WARNING-> "
pre_command = "\n---\n==> Processing object_action:"

element_dictionary = {}

def render_markdown(markdown_text: str) -> None:
    """Renders the given markdown text in the console."""
    console.print(Markdown(markdown_text))


def is_valid_iso_date(date_text) -> bool:
    """Checks if the given string is a valid ISO date."""
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def get_current_datetime_string():
    """Returns the current date and time as a human-readable string."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    return now


def add_term_to_categories(egeria_client: GlossaryManager, term_guid: str, categories_exist: bool,
                           categories_list: List[str], element_dictionary: dict) -> None:
    if categories_exist is True and categories_list is not None:
        for category in categories_list:
            cat_guid = None
            cat_el = category.strip()
            if cat_el in element_dictionary:
                cat= element_dictionary.get(cat_el, None)
                cat_guid = cat.get('guid', None) if cat else None
            if cat_guid is None:
                cat_guid = egeria_client.__get_guid__(qualified_name=cat_el)
            egeria_client.add_term_to_category(term_guid, cat_guid)


def extract_command_plus(block: str) -> tuple[str, str] | None:
    match = re.search(r"#(.*?)(?:##|\n|$)", block)  # Using a non capturing group
    if match:
        clean_match = match.group(1).strip()
        parts = clean_match.split(' ')
        object_action = parts[0].strip()
        # Join the rest of the parts to allow object_type to be one or two words
        object_type = ' '.join(parts[1:]).strip()
        return object_type, object_action
    return None

def extract_command(block: str) -> str | None:
    match = re.search(r"#(.*?)(?:##|\n|$)", block)  # Using a non capturing group
    if match:
        return match.group(1).strip()
    return None

def extract_attribute(text: str, labels: List[str]) -> Optional[str]:
    """
        Extracts the glossary name from a string.

        Args:
            text: The input string.
            labels: List of equivalent labels to search for

        Returns:
            The glossary name, or None if not found.
        """
    # Iterate over the list of labels
    for label in labels:
        # Construct pattern for the current label
        pattern = rf"## {re.escape(label)}\n(.*?)(?:#|---|$)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # Extract matched text and replace consecutive \n with a single \n
            extracted_text = re.sub(r'\n+', '\n', match.group(1).strip())
            if not extracted_text.isspace() and extracted_text:
                return extracted_text  # Return the cleaned text



def update_a_command(txt: str, command: str, obj_type: str, q_name: str, u_guid: str) -> str:
    u_guid = u_guid if u_guid else " "
    verb = command.split(' ')[0].strip()
    action = "Update" if (verb == "Create" and u_guid is not None) else "Create"
    txt = txt.replace(f"{command}", f'{action} {obj_type}\n')  # update the object_action
    txt = txt.replace('<GUID>', f'GUID\n{u_guid}')  # update with GUID
    txt = txt.replace('<Qualified Name>', f"Qualified Name\n{q_name}")
    if "Qualified Name" not in txt:
        txt += f"\n## Qualified Name\n{q_name}\n"
    if "GUID" not in txt:
        txt += f"\n## GUID\n{u_guid}\n"

    # if (object_action in {"Update Term", "Update Category", 'Update Glossary'}) and ("Update Description" not in txt):
    #     txt += '\n** Update Description\n\n\n'
    # elif "Update Description" in txt:
    #     pattern = r"(## Update Description\n).*?(#)"
    #     replacement = r"\1\n\n\2"
    #     txt += re.sub(pattern, replacement, txt)

    status = extract_attribute(txt, ["Status"])
    if command in ["Create Term", "Update Term"] and status is None:
        pattern = r"(## Status\s*\n)(.*?)(#)"
        replacement = r"\1\n DRAFT\n\n\3"
        txt = re.sub(pattern, replacement, txt)
    return txt

def process_provenance_command(file_path: str, txt: [str]) -> str:
    """This md_commands processes a provenence object_action by pre-pending the current file name and time to the provenance
    output"""
    output = (f"* Derived from processing file {file_path} on "
              f"{get_current_datetime_string()}\n")
    pattern = rf"# {re.escape('Provenance')}\n(.*?)(?:#|---|$)"
    match = re.search(pattern, txt, re.DOTALL)
    if match:
        # Extract matched text and replace consecutive \n with a single \n
        extracted_text = re.sub(r'\n+', '\n', match.group(1).strip())
        if not extracted_text.isspace() and extracted_text:
            existing_prov =  extracted_text  # Return the cleaned text
        else:
            existing_prov = None
    print(f"txt is: {txt}, existing_prov: {existing_prov}")
    existing_prov = existing_prov if existing_prov else " "
    return f"\n# Provenance:\n{existing_prov}\n{output}\n"

def process_element_identifiers(egeria_client: EgeriaTech, txt: str) -> tuple[str, str, str, bool, bool]:
    """
    Processes element identifiers by extracting display name and qualified name from the input text,
    checking if the element exists in Egeria, and validating the information.

    Parameters:
    egeria_client: EgeriaTech
        Client object for interacting with Egeria.
    txt: str
        A string representing the input text to be processed for extracting element identifiers.

    Returns: tuple[str, str, str, bool, bool]
        A tuple containing:
        - qualified_name: Empty string or element identifier
        - guid: Empty string or additional element information
        - msg: Information or error messages about the processing
        - Valid: Boolean indicating if the element information is valid
        - Exists: Boolean indicating if the element exists in Egeria
    """

    msg = ""
    known_guid = None
    valid = True
    exists = False
    display_name = extract_attribute(txt, ["Display Name"])
    if display_name is None:
        msg = f"* {ERROR}Display name is missing\n"
        valid = False
        return "","", msg, valid, exists
    qualified_name = extract_attribute(txt, ["Qualified Name"])
    if qualified_name:
        element_details = egeria_client.get_terms_by_name(qualified_name)
    else:
        element_details = egeria_client.get_terms_by_name(display_name)

    if element_details == NO_TERMS_FOUND:
        exists = False
    else:
        exists = True

    if len(element_details) > 1 and exists:
        msg += (f"* {ERROR}More than one element with name {display_name} found, please specify a "
                f"**Qualified Name**\n")
        valid = False
    elif len(element_details) == 1:
        known_guid = element_details[0]['elementHeader'].get('guid', None)
        known_q_name = element_details[0]['glossaryTermProperties'].get('qualifiedName', None)
        if qualified_name != known_q_name:
            msg += (f"* {ERROR}Element {display_name} qualifiedName mismatch between {qualified_name} and {known_q_name}\n")
            valid = False
        else:
            msg += f"\n--> * Element {display_name} exists and can be updated\n"
            # msg += term_display
            # element_dictionary[known_q_name] = {'display_name': display_name, 'guid': known_guid}
    return qualified_name, known_guid, msg, valid, exists

def process_blueprint_upsert_command(egeria_client: EgeriaTech, element_dictionary: dict, txt: str,
                                directive: str = "display") -> Optional[str]:
    """
    Processes a blueprint create or update object_action by extracting key attributes such as
    blueprint name, description, and version from the given cell.

    Parameters:
    egeria_client: SolutionArchitect
        Client object for interacting with Egeria.
    txt: str
        A string representing the input cell to be processed for
        extracting glossary-related attributes.
    directive: str, optional, default "display"
        An optional string indicating the directive to be used - display, validate or execute

    Returns: str
        A string summarizing the outcome of the processing.
    """

    object_type, object_action = extract_command_plus(txt)
    element_display = ""
    display_name = extract_attribute(txt, ['Display Name','Blueprint Name'])
    description = extract_attribute(txt, ['Description'])
    version = extract_attribute(txt, ['Version', "Version Identifier", "Published Version"])

    print(Markdown(f"{pre_command} `{object_type}{object_action}` for Blueprint: `\'{display_name}\'` with directive: `{directive}`"))

    def validate_blueprint(obj_action: str) -> tuple[bool, bool, Optional[str], Optional[str]]:
        nonlocal display_name, description, version, element_dictionary, element_display

        known_q_name, known_guid, msg, valid, exists = process_element_identifiers(egeria_client, txt)

        if description is None:
            msg += f"* {INFO}Description is missing\n"

        if version is None:
            msg += f"* {INFO}Term version is missing\n"

        update_description = extract_attribute(txt, ['Update Description'])
        if update_description is None:
            msg += f"* {INFO}Update Description is missing\n"
            update_description = "---"
        element_display = (f"\n* Command: {object_type}{object_action}\n\t* Blueprint: {display_name}\n\t"
                           f"* Term Name: {display_name}\n\t* Description: {description}\n\t"
                           f"* Version: {version}\n\t* Qualified Name:{known_q_name}\n\t* GUID: {known_guid} "
                           f"\n\t* Update Description: {update_description}\n")

        if obj_action == "Update":  # check to see if provided information exists and is consistent with existing info
            if not exists:
                msg += f"* {ERROR}Element {display_name} does not exist\n"
                valid = False
                element_dictionary[known_q_name] = {'display_name': display_name, 'guid': known_guid}

        elif obj_action == 'Create':  # if the object_action is create, check that it doesn't already exist
            if exists:
                msg += f"\n{WARNING}Element \'{display_name}\' already exists.\n"
            elif not valid:
                msg += f"\n-->Validation checks failed in creating element \'{display_name}\' with: {element_display}\n"
            else: # valid to create - update element_dictionary
                msg += f"\n-->It is valid to create element \'{display_name}\' with: {element_display}\n"
                if known_q_name is None:
                    known_q_name = egeria_client.__create_qualified_name__(object_type, display_name)
                element_dictionary[known_q_name] = {'display_name': display_name}
        print(Markdown(msg))
        return valid, exists, known_guid, known_q_name


    if directive == "display":
        print(Markdown(element_display))
        return None
    elif directive == "validate":
        is_valid, exists, known_guid, known_q_name = validate_blueprint(object_action)
        valid = is_valid if is_valid else None
        return valid
    elif directive == "process":
        try:
            is_valid, exists, known_guid, known_q_name = validate_blueprint(object_action)
            if not is_valid:  # First validate the term before we process it
                return None

            if object_action == "Update" and directive == "process":
                if not exists:
                    print(f"\n-->Blueprint {display_name} does not exist")
                    return None

                # call update blueprint here

                print(f"\n-->Updated Blueprint {display_name} with GUID {known_guid}")
                # update with get blueprint by guid
                return 'Would return get blueprint by guid and return md' #egeria_client.get_terms_by_guid(known_guid, 'md')

            elif object_action == "Update" and directive == "validate":
                return 'Would call get_blueprint_by_guid and return md' #egeria_client.get_terms_by_guid(known_guid, 'md')

            elif object_action == "Create":
                if exists:
                    print(f"\n{WARNING}Blueprint {display_name} exists and result document updated")
                    return update_a_command(txt, f"{object_type}{object_action}",
                    object_type, known_q_name, known_guid)
                else:
                   # create the blueprint
                    #term_guid = egeria_client.create_controlled_glossary_term(glossary_guid, term_body)
                    # if term_guid == NO_ELEMENTS_FOUND:
                    #     print(f"{ERROR}Term {term_name} not created")
                    #     return None

                    print(f"\n-->Created Blueprint {display_name} with GUID {known_guid}")
                    element_dictionary[known_q_name] = {'guid': known_guid, 'display_name': display_name}
                    return 'Would return get blueprint by guid results as md' #egeria_client.get_terms_by_guid(term_guid, 'MD')

        except Exception as e:
            print(f"{ERROR}Error creating term {display_name}: {e}")
            console.print_exception(show_locals=True)
            return None





def process_glossary_upsert_command(egeria_client: GlossaryManager, element_dictionary: dict, txt: str,
                                    directive: str = "display") -> Optional[str]:
    """
    Processes a glossary create or update object_action by extracting key attributes such as
    glossary name, language, description, and usage from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command = extract_command(txt)
    object_type = command.split(' ')[1].strip()
    object_action = command.split(' ')[0].strip()

    glossary_name = extract_attribute(txt, ['Glossary Name'])
    print(Markdown(f"{pre_command} `{command}` for glossary: `\'{glossary_name}\'` with directive: `{directive}` "))
    language = extract_attribute(txt, ['Language'])
    description = extract_attribute(txt, ['Description'])
    usage = extract_attribute(txt, ['Usage'])

    glossary_display = (f"\n* Command: {command}\n\t* Glossary Name: {glossary_name}\n\t"
                        f"* Language: {language}\n\t* Description:\n{description}\n"
                        f"* Usage: {usage}\n")

    if object_action == 'Update':
        q_name = extract_attribute(txt, ['Qualified Name'])
        guid = extract_attribute(txt, ['GUID', 'guid', 'Guid'])
        glossary_display += f"* Qualified Name: {q_name}\n\t* GUID: {guid}\n\n"

    def validate_glossary(obj_action: str) -> tuple[bool, bool, Optional[str], Optional[str]]:
        valid = True
        msg = ""
        known_glossary_guid = None
        known_q_name = None

        glossary_details = egeria_client.get_glossaries_by_name(glossary_name)
        if glossary_details == NO_GLOSSARIES_FOUND:
            glossary_exists = False
        else:
            glossary_exists = True

        if glossary_name is None:
            msg = f"* {ERROR}Glossary name is missing\n"
            valid = False
        if language is None:
            msg += f"* {ERROR}Language is missing\n"
            valid = False
        if description is None:
            msg += f"* {INFO}Description is missing\n"

        if len(glossary_details) > 1 and glossary_exists:
            msg += f"* {ERROR}More than one glossary with name {glossary_name} found\n"
            valid = False
        if len(glossary_details) == 1:
            known_glossary_guid = glossary_details[0]['elementHeader'].get('guid', None)
            known_q_name = glossary_details[0]['glossaryProperties'].get('qualifiedName', None).strip()

        if obj_action == "Update":

            if not glossary_exists:
                msg += f"* {ERROR}Glossary {glossary_name} does not exist\n"
                valid = False

            if q_name is None:
                msg += f"* {INFO}Qualified Name is missing => can use known qualified name of {known_q_name}\n"
                valid = True
            elif q_name != known_q_name:
                msg += (
                    f"* {ERROR}Glossary `{glossary_name}` qualifiedName mismatch between {q_name} and {known_q_name}\n")
                valid = False
            if valid:
                msg += glossary_display
                msg += f"* -->Glossary `{glossary_name}` exists and can be updated\n"
                element_dictionary[known_q_name] = {'display_name': glossary_name, 'guid': known_glossary_guid}
            else:
                msg += f"* --> validation failed\n"

            print(Markdown(msg))
            return valid, glossary_exists, known_glossary_guid, known_q_name

        elif obj_action == "Create":
            if glossary_exists:
                msg += f"{ERROR}Glossary {glossary_name} already exists\n"

            elif valid:
                msg += f"-->It is valid to create Glossary \'{glossary_name}\' with:\n"
                msg += glossary_display
                expected_q_name = egeria_client.__create_qualified_name__('Glossary', glossary_name)
                element_dictionary[expected_q_name] = {'display_name': glossary_name}

            print(Markdown(msg))
            return valid, glossary_exists, known_glossary_guid, known_q_name

    if directive == "display":
        print(Markdown(glossary_display))
        return None

    elif directive == "validate":
        is_valid, exists, known_guid, known_q_name = validate_glossary(object_action)
        valid = is_valid if is_valid else None
        return valid

    elif directive == "process":
        is_valid, exists, known_guid, known_q_name = validate_glossary(object_action)
        if not is_valid:
            return None
        if object_action == "Update":
            if not exists:
                print(
                    f"\n{ERROR}Glossary {glossary_name} does not exist! Updating result document with Create object_action\n")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)

            body = {
                "class": "ReferenceableRequestBody", "elementProperties": {
                    "class": "GlossaryProperties", "qualifiedName": known_q_name, "description": description,
                    "language": language, "usage": usage
                    }
                }
            egeria_client.update_glossary(known_guid, body)
            print(f"\n-->Updated Glossary {glossary_name} with GUID {known_guid}")
            element_dictionary[known_q_name] = {
                'guid': known_guid, 'display_name': glossary_name
                }
            # return update_a_command(txt, object_action, object_type, known_q_name, known_guid)
            return egeria_client.get_glossary_by_guid(known_guid, output_format='MD')
        elif object_action == "Create":
            glossary_guid = None

            if exists:
                print(f"\nGlossary {glossary_name} already exists and result document updated\n")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)
            else:
                glossary_guid = egeria_client.create_glossary(glossary_name, description, language, usage)
                glossary = egeria_client.get_glossary_by_guid(glossary_guid)
                if glossary == NO_GLOSSARIES_FOUND:
                    print(f"{ERROR}Just created with GUID {glossary_guid} but Glossary not found\n")
                    return None
                qualified_name = glossary['glossaryProperties']["qualifiedName"]
                element_dictionary[qualified_name] = {
                    'guid': glossary_guid, 'display_name': glossary_name
                    }
                # return update_a_command(txt, object_action, object_type, qualified_name, glossary_guid)
                return egeria_client.get_glossary_by_guid(glossary_guid, output_format = 'MD')


def process_categories_upsert_command(egeria_client: GlossaryManager, element_dictionary: dict, txt: str,
                                      directive: str = "display") -> Optional[str]:
    """
    Processes a glossary category create or update object_action by extracting key attributes such as
    category name, qualified, description, and anchor glossary from the given txt..

    :param txt: A string representing the input cell to be processed for
        extracting category-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command = extract_command(txt)
    object_type = command.split(' ')[1].strip()
    object_action = command.split(' ')[0].strip()

    category_name = extract_attribute(txt, ['Category Name', 'category_name', 'Cat'])
    print(Markdown(f"{pre_command} `{command}` for category: `\'{category_name}\'` with directive: `{directive}` "))
    owning_glossary_qn = extract_attribute(txt, ['Owning Glossary', '[In Glossary'])
    description = extract_attribute(txt, ['Description'])
    q_name = extract_attribute(txt, ['Qualified Name'])

    category_display = (f"\n* Command: {command}\n\t* Category: {category_name}\n\t* In Glossary: {owning_glossary_qn}\n\t"
                        f"* Description:\n{description}\n\t* Qualified Name: {q_name}\n\t")
    update_description = None

    if object_action == 'Update':
        guid = extract_attribute(txt, ['GUID','guid','Guid'])
        update_description = extract_attribute(txt, 'Update Description')
        category_display += (f"* GUID: {guid}\n\n"
                             f"* Update Description: \n {update_description}\n\t")

    def validate_category(obj_action: str) -> tuple[bool, bool, Optional[str], Optional[str], Optional[str]]:
        valid = True
        msg = ""
        known_category_guid = None
        known_q_name = None
        glossary_guid = None

        category_details = egeria_client.get_categories_by_name(category_name)
        if category_details == NO_CATEGORIES_FOUND:
            category_exists = False
        else:
            category_exists = True

        if owning_glossary_qn is None:
            msg += f"* {ERROR}Owning Glossary Qualified Name is missing\n"
            valid = False

        elif owning_glossary_qn in element_dictionary:  # Check to see if we already know about this glossary
            glossary_name = element_dictionary[owning_glossary_qn].get('display_name', None)
            glossary_guid = element_dictionary[owning_glossary_qn].get('guid', None)

        else:
            # need to ask Egeria if it knows the Glossary Name
            glossary = egeria_client.get_glossaries_by_name(owning_glossary_qn)
            if glossary == NO_GLOSSARIES_FOUND:
                msg += f"* {ERROR}Glossary `{owning_glossary_qn}` does not exist\n\n"
                valid = False
            else:
                msg += f"* {INFO}Glossary `{owning_glossary_qn}` exists\n\n"
                glossary_guid = glossary[0]['elementHeader'].get('guid', None)
                glossary_name = glossary[0]['glossaryProperties'].get('displayName', None)
                glossary_qn = glossary[0]['glossaryProperties'].get('qualifiedName', None)
                if glossary_qn != owning_glossary_qn: # we were given the right qualified name - maybe a display_name
                    msg += f"* {ERROR}Glossary `{owning_glossary_qn}` is known by qualifiedName `{glossary_qn}`\n\n"
                    valid = False
                else:
                    element_dictionary[owning_glossary_qn] = {
                        'guid': glossary_guid, 'display_name': glossary_name
                        }

        if category_name is None:
            msg = f"* {ERROR}Category name is missing\n"
            valid = False

        if description is None:
            msg += f"* {INFO}Description is missing\n"

        if len(category_details) > 1 and category_exists:
            msg += f"* {ERROR}More than one category with name `{category_name}` found\n"
            valid = False
        if len(category_details) == 1:
            known_category_guid = category_details[0]['elementHeader'].get('guid', None)
            known_q_name = category_details[0]['glossaryCategoryProperties'].get('qualifiedName', None)

        if obj_action == "Update":
            if not category_exists:
                msg += f"* {ERROR}category `{category_name}` does not exist\n"
                valid = False
            if q_name is None:
                msg += f"* {INFO}Qualified Name is missing => can use known qualified name of {known_q_name}\n"
                valid = True
            elif q_name != known_q_name:
                msg += (
                    f"* {ERROR}category `{category_name}` qualifiedName mismatch between {q_name} and {known_q_name}\n")
                valid = False
            if valid:
                msg += category_display
                msg += f"* -->category `{category_name}` exists and can be updated\n"
                element_dictionary[known_q_name] = {'display_name': glossary_name, 'guid': known_category_guid}
            else:
                msg += f"* --> validation failed\n"

            print(Markdown(msg))
            return valid, category_exists, known_category_guid, known_q_name, glossary_guid

        elif obj_action == "Create":
            if category_exists:
                msg += f"{ERROR}category `{category_name}` already exists\n"

            elif valid:
                msg += f"-->It is valid to create category `{category_name}` with:\n"
                msg += category_display
                expected_q_name = egeria_client.__create_qualified_name__('Category', category_name)
                element_dictionary[expected_q_name] = {'display_name': category_name}

            print(Markdown(msg))
            return valid, category_exists, known_category_guid, known_q_name, glossary_guid

    if directive == "display":
        print(Markdown(category_display))
        return None

    elif directive == "validate":
        is_valid, exists, known_guid, known_q_name, glossary_guid = validate_category(object_action)
        valid = is_valid if is_valid else None
        return valid

    elif directive == "process":
        is_valid, exists, known_guid, known_q_name, glossary_guid = validate_category(object_action)
        if not is_valid:
            print(f"{ERROR}Validation checks failed in creating category `{category_name}`")
            return None

        if object_action == "Update":
            if not exists:
                print(
                    f"\n{ERROR}category `{category_name}` does not exist! Updating result document with Create "
                    f"object_action\n")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)

            egeria_client.update_category(glossary_guid, category_name, description, known_q_name, None,
                                          update_description)
            print(f"\n-->Updated category `{category_name}`with GUID {known_guid}")
            element_dictionary[known_q_name] = {
                'guid': known_guid, 'display_name': category_name
                }
            # return update_a_command(txt, object_action, object_type, known_q_name, known_guid)
            return egeria_client.get_category_by_guid(known_guid, output_format='FORM')

        elif object_action == "Create":
            is_root = False

            if exists:
                print(f"\ncategory `{category_name}` already exists and result document updated\n")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)
            else:
                category_guid = egeria_client.create_category(glossary_guid, category_name, description, is_root)
                category = egeria_client.get_category_by_guid(category_guid)

                if category == NO_CATEGORIES_FOUND:
                    print(f"{ERROR}Just created with GUID {category_guid} but category not found\n")
                    return None
                qualified_name = category['glossaryCategoryProperties']["qualifiedName"]
                element_dictionary[qualified_name] = {
                    'guid': category_guid, 'display_name': category_name
                    }
                # return update_a_command(txt, object_action, object_type, qualified_name, category_guid)
                return egeria_client.get_category_by_guid(category_guid, output_format='MD')


def process_term_upsert_command(egeria_client: GlossaryManager, element_dictionary: dict, txt: str,
                                directive: str = "display") -> Optional[str]:
    """
    Processes a term create or update object_action by extracting key attributes such as
    term name, summary, description, abbreviation, examples, usage, version, and status from the given cell.

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """

    command = extract_command(txt)
    object_type = command.split(' ')[1].strip()
    object_action = command.split(' ')[0].strip()

    term_name = extract_attribute(txt, ['Term Name'])
    summary = extract_attribute(txt, ['Summary'])
    description = extract_attribute(txt, ['Description'])
    abbreviation = extract_attribute(txt, ['Abbreviation'])
    examples = extract_attribute(txt, ['Examples'])
    usage = extract_attribute(txt, ['Usage'])
    status = extract_attribute(txt, ['Status'])
    version = extract_attribute(txt, ['Version', "Version Identifier", "Published Version"])
    categories = extract_attribute(txt, ['Categories'])
    q_name = extract_attribute(txt, ['Qualified Name'])
    # q_name = q_name if q_name else " "

    categories_list = None
    cats_exist = True

    glossary_qn = extract_attribute(txt, ['In Glossary','Owning Glossary'])

    print(Markdown(f"{pre_command} `{command}` for term: `\'{term_name}\'` with directive: `{directive}`"))

    def validate_term(obj_action: str) -> tuple[bool, bool, Optional[str], Optional[str]]:
        nonlocal version, status, categories, categories_list, cats_exist, q_name, glossary_qn
        valid = True
        msg = ""
        known_term_guid = None
        known_q_name = None

        # If the user has specified a qualified_name then use it to look for matching terms.
        # If not, use the display_name.
        if q_name:
            term_details = egeria_client.get_terms_by_name(q_name)
        else:
            term_details = egeria_client.get_terms_by_name(term_name)

        if term_details == NO_TERMS_FOUND:
            term_exists = False
        else:
            term_exists = True

        if status is None:
            msg += f"* {INFO}Term status is missing - will default to DRAFT\n"
            status = 'DRAFT'


        if term_name is None:
            msg = f"* {ERROR}Term name is missing\n"
            valid = False
        if glossary_qn is None:
            msg += f"* {ERROR}Glossary qualified name is missing\n"
            valid = False
        else:
            print(f"* {INFO}Glossary qualified name is `{glossary_qn}`")
            if glossary_qn not in element_dictionary:
                glossary = egeria_client.get_glossaries_by_name(glossary_qn) #assuming q_name?
                if isinstance(glossary,str):
                    msg += f"* {ERROR}Glossary `{glossary_qn}` is unknown\n "
                    valid = False
                elif len(glossary) != 1:
                    msg += f"* {ERROR}Glossary `{glossary_qn}` is ambiguous or not found\n "
                    valid = False
                else:
                    glossary_qn = glossary[0]['glossaryProperties'].get('qualifiedName', None)
                    if glossary_qn is None:
                        msg += f"* {ERROR}Glossary `{glossary_qn}` has no qualifiedName\n "
                        valid = False
                    else:
                        element_dictionary[glossary_qn] = {
                        'guid': glossary[0]['elementHeader'].get('guid', None),
                        'display_name': glossary[0]['glossaryProperties'].get('displayName', None)
                        }


        if categories is None:
            msg += f"* {INFO} No categories found\n"
        else:
            categories_list = re.split(r'[,\n]+', categories)
            categories = ""
            new_cat_list = []
            for category in categories_list:
                category_el = category.strip()
                if category_el not in element_dictionary:
                    cat = egeria_client.get_categories_by_name(category_el) # assuming qualified name?
                    if isinstance(cat,str):
                        msg += (f"* {WARNING}Category `{category_el}` not found -> "
                                f"categories for this term won't be processed!\n")
                        cats_exist = False
                        break
                    cat_qname = cat[0]['glossaryCategoryProperties'].get('qualifiedName', None)
                    category = cat_qname # use the qualified name if found
                    if cat_qname not in element_dictionary:
                        cat_guid = cat[0]['elementHeader']['guid']
                        cat_display_name = cat[0]['glossaryCategoryProperties'].get('displayName', None)
                        element_dictionary[cat_qname] = {
                            'guid' : cat_guid,
                            'displayName': cat_display_name
                            }
                categories = f"{category}, {categories}"
                new_cat_list.append(category)
            if cats_exist:
                categories +='\n'
                categories_list = new_cat_list
            else:
                categories = None


        if summary is None:
            msg += f"* {INFO}Term summary is missing\n"

        if description is None:
            msg += f"* {INFO}Term description is missing\n"

        if abbreviation is None:
            msg += f"* {INFO}Term abbreviation is missing\n"
        if examples is None:
            msg += f"* {INFO}Term examples is missing\n"
        if usage is None:
            msg += f"* {INFO}Term usage is missing\n"
        if version is None:
            msg += f"* {INFO}Term version is missing\n"
            # version = "0.0.1"


        if obj_action == "Update":  # check to see if provided information exists and is consistent with existing info
            if not term_exists:
                msg += f"* {ERROR}Term {term_name} does not exist\n"
                valid = False

            if len(term_details) > 1 and term_exists:
                msg += (f"* {ERROR}More than one term with name {term_name} found, please specify a "
                        f"**Qualified Name**\n")
                valid = False
            elif len(term_details) == 1:
                known_term_guid = term_details[0]['elementHeader'].get('guid', None)
                known_q_name = term_details[0]['glossaryTermProperties'].get('qualifiedName', None)
            if q_name != known_q_name:
                msg += (f"* {ERROR}Term {term_name} qualifiedName mismatch between {q_name} and {known_q_name}\n")
                valid = False
            else:
                msg += f"\n--> * Term {term_name} exists and can be updated\n"
                msg += term_display
                element_dictionary[known_q_name] = {'display_name': term_name, 'guid': known_term_guid}

            print(Markdown(msg))
            return valid, term_exists, known_term_guid, known_q_name

        elif obj_action == 'Create':  # if the object_action is create, check that it doesn't already exist
            if term_exists:
                msg += f"\n{WARNING}Term \'{term_name}\' already exists.\n"
            elif not valid:
                msg += f"\n-->Validation checks failed in creating Term \'{term_name}\' with: {term_display}\n"
            else:
                msg += f"\n-->It is valid to create Term \'{term_name}\' with: {term_display}\n"
                if q_name is None:
                    expected_q_name = egeria_client.__create_qualified_name__('Term', term_name)
                    element_dictionary[expected_q_name] = {'display_name': term_name}
                else:
                    element_dictionary[q_name] = {'display_name': term_name}
            print(Markdown(msg))
            return valid, term_exists, known_term_guid, known_q_name

    # Continue processing the upsert
    if object_action == "Update":
        term_guid = extract_attribute(txt, 'GUID')
        term_guid = term_guid if term_guid else None


        update_description = extract_attribute(txt, 'Update Description')
        update_description = update_description if update_description else " "
        term_display = (f"\n* Command: {command}\n\t* Glossary: {glossary_qn}\n\t"
                        f"* Term Name: {term_name}\n\t* Qualified Name: {q_name}\n\t* Categories: {categories}\n\t"
                        f"* Summary: {summary}\n\t* Description: {description}\n\t"
                        f"* Abbreviation: {abbreviation}\n\t* Examples: {examples}\n\t* Usage: {usage}\n\t"
                        f"* Version: {version}\n\t* Status: {status}\n\t* GUID: {term_guid}\n\t* Qualified Name: "
                        f"{q_name}"
                        f"\n\t* Update Description: {update_description}\n")
    else:
        term_display = (f"\n* Command: {command}\n\t* Glossary: {glossary_qn}\n\t"
                        f"* Term Name: {term_name}\n\t* Categories: {categories}\n\t* Summary: {summary}\n\t"
                        f"* Qualified Name: {q_name}\n\t* Description: {description}\n\t"
                        f"* Abbreviation: {abbreviation}\n\t* Examples: {examples}\n\t* Usage: {usage}\n\t"
                        f"* Version: {version}\n\t* Status: {status}\n")

    if directive == "display":
        print(Markdown(term_display))
        return None
    elif directive == "validate":
        is_valid, exists, known_guid, known_q_name = validate_term(object_action)
        valid = is_valid if is_valid else None
        return valid
    elif directive == "process":
        try:
            is_valid, exists, known_guid, known_q_name = validate_term(object_action)
            if not is_valid:  # First validate the term before we process it
                return None

            if object_action == "Update" and directive == "process":
                if not exists:
                    print(f"\n-->Term {term_name} does not exist")
                    return None
                body = {
                    "class": "ReferenceableRequestBody",
                    "elementProperties": {
                        "class": "GlossaryTermProperties",
                        "qualifiedName": known_q_name,
                        "summary": summary,
                        "description": description,
                        "abbreviation": abbreviation,
                        "examples": examples,
                        "usage": usage,
                        "publishVersionIdentifier": version,
                        "status": status
                        },
                    "updateDescription": update_description
                    }
                egeria_client.update_term(known_guid, body_slimmer(body))
                # if cats_exist is True and categories_list is not None:
                #     for category in categories_list:
                #         cat_guid = element_dictionary.get(f"category.{category}", None)
                #         if cat_guid is None:
                #             cat_guid = egeria_client.__get_guid__(display_name=category)
                #         egeria_client.add_term_to_category(known_guid, cat_guid)
                add_term_to_categories(
                    egeria_client, known_guid, cats_exist , categories_list,
                    element_dictionary)
                print(f"\n-->Updated Term {term_name} with GUID {known_guid} and categories {categories_list}")
                return egeria_client.get_terms_by_guid(known_guid, 'md')
                # return update_a_command(txt, object_action, object_type, known_q_name, known_guid)
            elif object_action == "Update" and directive == "validate":
                return egeria_client.get_terms_by_guid(known_guid, 'md')

            elif object_action == "Create":
                guid = None
                if q_name is None:
                    q_name = egeria_client.__create_qualified_name__("Term",term_name)
                if exists:
                    print(f"\n{WARNING}Term {term_name} exists and result document updated")
                    return update_a_command(txt, command, object_type, q_name, known_guid)
                else:
                    ## get the guid for the glossary from the name - first look locally
                    glossary = element_dictionary.get(glossary_qn, None)

                    if glossary is not None:
                        glossary_guid = glossary.get('guid', None)
                        if glossary_guid is None:
                            print(f"{ERROR}Glossary reference {glossary_qn} not found")
                            return None
                    else:
                        glossary_guid = egeria_client.__get_guid__(qualified_name=glossary_qn)
                        if glossary_guid == NO_ELEMENTS_FOUND:
                            print(f"{ERROR}Glossary {glossary_qn} not found")
                            return None
                    term_body = {
                        "class": "ReferenceableRequestBody", "elementProperties": {
                            "class": "GlossaryTermProperties",
                            "qualifiedName": q_name,
                            "displayName": term_name,
                            "summary": summary,
                            "description": description,
                            "abbreviation": abbreviation,
                            "examples": examples,
                            "usage": usage,
                            "publishVersionIdentifier": version
                            # "additionalProperties":
                            #     {
                            #         "propertyName1": "xxxx",
                            #         "propertyName2": "xxxx"
                            #         }
                            }, "initialStatus": status
                        }
                    term_guid = egeria_client.create_controlled_glossary_term(glossary_guid, term_body)
                    if term_guid == NO_ELEMENTS_FOUND:
                        print(f"{ERROR}Term {term_name} not created")
                        return None
                    if cats_exist and categories is not None:
                        add_term_to_categories(
                        egeria_client, term_guid, cats_exist, categories_list,
                        element_dictionary)
                    print(f"\n-->Created Term {term_name} with GUID {term_guid}")
                    element_dictionary[q_name] = {'guid': term_guid, 'display_name': term_name}
                    return egeria_client.get_terms_by_guid(term_guid, 'MD')
                    # return update_a_command(txt, object_action, object_type, q_name, term_guid)
        except Exception as e:
            print(f"{ERROR}Error creating term {term_name}: {e}")
            console.print_exception(show_locals=True)
            return None

def process_per_proj_upsert_command(egeria_client: ProjectManager, element_dictionary: dict, txt: str,
                                    directive: str = "display") -> str | None:
    """
    Processes a personal project create or update object_action by extracting key attributes such as
    glossary name, language, description, and usage from the given cell.

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command = extract_command(txt)
    object = command.split()
    object_type = f"{object[1]} {object[2]}"
    object_action = object[0]

    project_name = extract_attribute(txt, ['Project Name'])
    description = extract_attribute(txt, ['Description'])
    project_identifier = extract_attribute(txt, ['Project Identifier'])
    project_status = extract_attribute(txt, ['Project Status'])
    project_phase = extract_attribute(txt, ['Project Phase'])
    project_health = extract_attribute(txt, ['Project Health'])
    start_date = extract_attribute(txt, ['Start Date'])
    planned_end_date = extract_attribute(txt, ['Planned End Date'])
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
            q_name = extract_attribute(txt, 'Qualified Name')

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
        is_valid, exists, known_guid, known_q_name = validate_project(object_action)
        valid = is_valid if is_valid else None
        return valid

    elif directive == "process":
        is_valid, exists, known_guid, known_q_name = validate_project(object_action)
        if not is_valid:
            return None
        if object_action == "Update":
            if not exists:
                print(f"\n\n-->Project {project_name} does not exist")
                return None

            egeria_client.update_project(known_guid, known_q_name, project_identifier, project_name, description,
                                         project_status, project_phase, project_health, start_date, planned_end_date,
                                         False)
            print(f"\n-->Updated Project {project_name} with GUID {known_guid}")
            return update_a_command(txt, command, object_type, known_q_name, known_guid)
        elif object_action == "Create":
            guid = None
            if exists:
                print(f"Project {project_name} already exists and update document created")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)
            else:
                guid = egeria_client.create_project(None, None, None, False, project_name, description,
                                                    "PersonalProject", project_identifier, True, project_status,
                                                    project_phase, project_health, start_date, planned_end_date)
                project_g = egeria_client.get_project_by_guid(guid)
                if project_g == NO_GLOSSARIES_FOUND:
                    print(f"Just created with GUID {guid} but Project not found")
                    return None

                q_name = project_g['projectProperties']["qualifiedName"]
                element_dictionary[q_name] = {'guid': guid, 'display_name': project_name}
                return update_a_command(txt, command, object_type, q_name, guid)
