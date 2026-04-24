"""
This file contains general utility functions for processing Egeria Markdown
"""
import os
import sys
from datetime import datetime
from typing import Optional

from loguru import logger
from rich import print
from rich.console import Console

from md_processing.md_processing_utils import md_processing_constants
from md_processing.md_processing_utils.md_processing_constants import (get_command_spec, load_commands,
                                                                       add_default_upsert_attributes,
                                                                       add_default_link_attributes)

from pyegeria import ServerClient, EgeriaTech
from pyegeria.core.config import get_app_config
from pyegeria.view.output_formatter import generate_entity_md_table, populate_columns_from_properties

# Load application configuration
config = get_app_config()
env = config.Environment
user_profile = config.User_Profile

EGERIA_WIDTH = env.console_width
EGERIA_ROOT_PATH = env.pyegeria_root
EGERIA_INBOX_PATH = env.egeria_inbox

console = Console(width=EGERIA_WIDTH)

debug_level = config.Debug.debug_mode
load_commands('commands.json')


log_format = "D {time} | {level} | {function} | {line} | {message} | {extra}"
logger.remove()
logger.add(sys.stderr, level="INFO", format=log_format, colorize=True)
full_file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_INBOX_PATH, "data_designer_debug.log")
# logger.add(full_file_path, rotation="1 day", retention="1 week", compression="zip", level="TRACE", format=log_format,
#            colorize=True)
logger.add("debug_log", rotation="1 day", retention="1 week", compression="zip", level="TRACE", format=log_format,
           colorize=True)
def get_iso8601_datetime():
    """Returns the current date and time in ISO 8601 format."""
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

def yes_no(input: str)->str:
    if type(input) is bool:
        if input:
            return "True"
        else:
            return "False"

    input = input.title()
    if input in ["Yes","No"]:
        return input

    if input in ["True", "T"]:
        return "Yes"
    else:
        return "No"

@logger.catch
def _extract_help_fields(command: dict, client: Optional[ServerClient] = None, advanced: bool = False):
    """
    Build a list of attribute dictionaries for a given command spec.
    This prepares the data rows used to render the help table.
    """

    command_spec = get_command_spec(command)
    verb = command_spec.get('verb', None)
    from md_processing.md_processing_utils.md_processing_constants import LINK_VERBS
    if verb in ["Create", "Update"]:
        distinguished_attributes = command_spec.get('Attributes', [])
        attributes = add_default_upsert_attributes(distinguished_attributes)
    elif verb in LINK_VERBS:
        distinguished_attributes = command_spec.get('Attributes', [])
        attributes = add_default_link_attributes(distinguished_attributes)
    else:
        attributes = command_spec.get('Attributes', [])


    term_entry: list = []
    for attribute in attributes:
        if "name" in attribute:
            key = attribute["name"]
            value = attribute
        else:
            # Fallback for old single-key dict structure
            if not attribute:
                continue
            key, value = list(attribute.items())[0]

        if not advanced and value.get('level', 'Basic') != "Basic":
            continue
            
        attribute_name = key
        input_required = yes_no(value.get('input_required', "No"))

        read_only = yes_no(value.get('user_specified', "No"))
        generated = yes_no(value.get('generated', "No"))
        default = value.get('default', None) or value.get('default_value', None)
        
        unique = yes_no(value.get('unique', "No"))
        notes = value.get('description', "")
        valid_values = value.get('valid_values', [])
        prop_name = value.get('property_name')
        
        dynamic_default = None
        if prop_name and client:
            try:
                valid_elements = client.get_valid_metadata_values(prop_name)
                if valid_elements:
                    if not valid_values:
                        valid_values = "; ".join([el.get("preferredValue") for el in valid_elements if el.get("preferredValue")])
                    
                    # Look for dynamic default
                    for el in valid_elements:
                        if el.get("additionalProperties", {}).get("isDefaultValue") == "true":
                            dynamic_default = el.get("preferredValue")
                            break
            except Exception:
                pass
        
        if not default:
            default = dynamic_default

        term_entry.append({
            'Attribute Name': attribute_name,
            'Input Required': input_required,
            'Read Only': read_only,
            'Generated': generated,
            'Default Value': default,
            'Notes': notes,
            'Unique Values': unique,
            'Valid Values': valid_values,
        })

    return term_entry

@logger.catch
def _extract_help_function(element: dict, columns_struct: dict) -> dict:
    """
    Return a populated columns data structure matching the signature and structure
    of _extract_glossary_properties in glossary_manager.

    Args:
        element: One row (dict) describing a help attribute with keys matching columns_struct
        columns_struct: Dict containing formats->columns definitions

    Returns:
        dict: A structure with key 'formats' and a 'columns' list whose entries have
              their 'value' fields populated from the element dict.
    """
    # Normalize to a shape compatible with populate_columns_from_properties
    normalized = {
        'properties': element or {},
        'elementHeader': {},
    }
    col_data = populate_columns_from_properties(normalized, columns_struct)
    return col_data

def create_help_terms(client: Optional[ServerClient] = None, advanced: bool = False):
    term_entry:str = ""
    glossary_name = "dr-egeria"
    glossary_qn = "Glossary::dr-egeria"
    commands = md_processing_constants.COMMAND_DEFINITIONS.get("Command Specifications", {})
    columns = [{'name': "Attribute Name", 'key': 'Attribute Name'},
               {'name': 'Input Required', 'key': 'Input Required'},
               {'name': 'Read Only', 'key': 'Read Only'},
               {'name': 'Generated', 'key': 'Generated'},
               {'name': 'Default Value', 'key': 'Default Value'},
               {'name': 'Notes', 'key': 'Notes'},
               {'name': 'Unique Values', 'key': 'Unique Values'},
               {'name': 'Valid Values', 'key': 'Valid Values'}]
    columns_struct = {"target_type": "Term", "formats": {
                                          "types": "ALL",
                                        "attributes": columns}
                      }

    term_entry = f"""## Create Glossary\n
### Display Name\n\n{glossary_name}\n
### Qualified Name\n\n{glossary_qn}\n
### Description\n\nDr.Egeria command help glossary.\n\n___\n\n"""

    families = set()
    for command, values in commands.items():
        if command == "exported":
            continue
        family = values.get("family", "General")
        families.add(family)

    for family in families:
        family_qn = f"CollectionFolder::dr-egeria:{family.lower().replace(' ', '-')}"
        term_entry += f"## Create Collection Folder\n### Display Name\n\n{family}\n\n### Qualified Name\n\n{family_qn}\n\n### Purpose\n\nDr-Egeria Definitions\n\n### Parent ID\n\n{glossary_qn}\n\n### Parent Relationship Type Name\n\nCollectionMembership\n\n___\n\n"

    for command, values in commands.items():
        if command == "exported":
            continue
        if not advanced and commands[command].get("level","Basic") not in ["Basic"]:
            continue
        command_description = commands[command].get("description","")
        command_verb = commands[command].get("verb","")
        family = commands[command].get("family", "General")
        family_qn = f"CollectionFolder::dr-egeria:{family.lower().replace(' ', '-')}"

        term_entry+= "## Create Term\n"
        term_entry+= f"### Display Name\n\n{command}\n\n"
        term_entry+= f"### Description\n\n{command_description}\n\n"
        term_entry+= f"### Glossary Name\n\n{glossary_qn}\n\n"
        term_entry+= f"### Folders\n\n{family_qn}\n\n"


        du = _extract_help_fields(command, client=client, advanced=advanced)
        output = generate_entity_md_table(du, "", "", _extract_help_function, columns_struct, None, "help" )

        term_entry+= f"### Usage\n\n{output}\n\n___\n\n"

    print(term_entry)
    # Generate filename with current date and time in ISO 8601 format
    current_datetime = get_iso8601_datetime()
    filename = f"dr-egeria-help-{current_datetime}.md"
    file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_INBOX_PATH, filename)

    # Write the content to the file
    with open(file_path, 'w', encoding="utf-8") as f:
        f.write(term_entry)

    logger.info(f"Help documentation saved to {file_path}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate Dr. Egeria help documentation.")
    parser.add_argument("--server", default=env.egeria_view_server, help="Egeria view server name")
    parser.add_argument("--url", default=env.egeria_view_server_url, help="Egeria platform URL")
    parser.add_argument("--userid", default=user_profile.user_name, help="Egeria user ID")
    parser.add_argument("--pass", dest="user_pass", default=user_profile.user_pwd, help="Egeria user password")
    parser.add_argument("--advanced", action="store_true", help="Include advanced attributes and commands")

    args = parser.parse_args()
    
    client = None
    if args.url:
        try:
            client = ServerClient(args.server, args.url, user_id=args.userid)
            client.create_egeria_bearer_token(args.userid, args.user_pass)
            logger.info(f"Connected to Egeria at {args.url} for dynamic valid values")
        except Exception as e:
            logger.warning(f"Could not connect to Egeria: {e}. Falling back to static values.")

    create_help_terms(client=client, advanced=args.advanced)


if __name__ == "__main__":
    main()
