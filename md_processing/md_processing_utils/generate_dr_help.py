"""
This file contains general utility functions for processing Egeria Markdown
"""
import json
import os
import sys
from datetime import datetime
from typing import List

from loguru import logger
from rich import print
from rich.console import Console
from rich.markdown import Markdown

from commands.cat.dr_egeria_command_help import EGERIA_INBOX_PATH
from md_processing.md_processing_utils.common_md_utils import (get_current_datetime_string, get_element_dictionary,
                                                               update_element_dictionary,
                                                               split_tb_string, str_to_bool, )
from md_processing.md_processing_utils.extraction_utils import (process_simple_attribute, extract_attribute,
                                                                get_element_by_name)
from md_processing.md_processing_utils.md_processing_constants import (get_command_spec, load_commands, load_commands, COMMAND_DEFINITIONS)

from md_processing.md_processing_utils.message_constants import (ERROR, INFO, WARNING, ALWAYS, EXISTS_REQUIRED)
from pyegeria import EgeriaTech
from pyegeria._globals import DEBUG_LEVEL
from pyegeria.output_formatter import generate_entity_md_table

# Constants
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))
EGERIA_ROOT_PATH = os.environ.get("EGERIA_ROOT_PATH", ".")
EGERIA_INBOX_PATH = os.environ.get("EGERIA_INBOX_PATH", ".")

console = Console(width=EGERIA_WIDTH)

debug_level = DEBUG_LEVEL
global COMMAND_DEFINITIONS

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
def _extract_help_fields(command: dict):
    """

    """

    command_spec = get_command_spec(command)
    attributes = command_spec.get('Attributes', [])
    command_display_name = command_spec.get('display_name', None)
    command_qn_prefix = command_spec.get('qn_prefix', None)

    term_entry: list = []
    for attr in attributes:
        for key in attr:
            if attr[key].get('level','Basic') != "Basic":
                continue
            attribute_name = key
            input_required = yes_no(attr[key].get('input_required', "No"))

            read_only = yes_no(attr[key].get('user_specified', "No"))
            generated = yes_no(attr[key].get('generated', "No"))
            default = attr[key].get('default', None)
            if default:
                generated = default
            unique = yes_no(attr[key].get('unique', "No"))
            notes = attr[key].get('description', "")
            valid_values = attr[key].get('valid_values', [])
            term_entry.append ({
                'Attribute Name' : attribute_name,
                'Input Required' : input_required,
                'Read Only' : read_only,
                'Generated' : generated,
                'Default Value' : default,
                'Notes' : notes,
                'Unique Values' : unique,
                'Valid Values' : valid_values,
                })

    return term_entry

def create_help_terms():
    term_entry:str = ""
    glossary_name = "Egeria-Markdown"
    commands = COMMAND_DEFINITIONS["Command Specifications"]
    columns = [{'name': "Attribute Name", 'key': 'Attribute Name'},
               {'name': 'Input Required', 'key': 'Input Required'},
               {'name': 'Read Only', 'key': 'Read Only'},
               {'name': 'Generated', 'key': 'Generated'},
               {'name': 'Default Value', 'key': 'Default Value'},
               {'name': 'Notes', 'key': 'Notes'},
               {'name': 'Unique Values', 'key': 'Unique Values'},
               {'name': 'Valid Values', 'key': 'Valid Values'}]

    term_entry = """# Generating glossary entries for the documented commands\n\n
            This file contains generated Dr.Egeria commands to generate glossary term entries describing
            each Dr.Egeria command. 

> Usage: Before executing this file, make sure you have a glossary named `Egeria-Markdown`
> already created. If you Need to create one, you can use the \n"""

    for command, values in commands.items():
        if command == "exported":
            continue
        if commands[command].get("level","") not in ["Basic"]:
            continue
        command_description = commands[command].get("description","")
        command_verb = commands[command].get("verb","")

        term_entry+= "# Create Term\n"
        term_entry+= f"## Term Name\n\n{command}\n\n"
        term_entry+= f"## Description\n\n{command_description}\n\n"
        term_entry+= f"## Owning Glossary\n\n{glossary_name}\n\n"
        term_entry+= f"## Categories\n\nWriting Dr.Egeria Markdown\n\n"


        du = _extract_help_fields(command)
        output = generate_entity_md_table(du, "", "", _extract_help_fields, columns, None, "help" )

        term_entry+= f"## Usage\n\n{output}\n\n___\n\n"
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
    create_help_terms()


if __name__ == "__main__":
    main()
