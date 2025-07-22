"""
This file contains general utility functions for processing Egeria Markdown
"""
import os
import sys
from typing import List, Dict
import io

from loguru import logger
from rich import print
from rich.console import Console

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
@logger.catch
def main():
    """
    Generate markdown command templates organized by family
    """
    glossary_name = "Egeria-Markdown"
    commands = COMMAND_DEFINITIONS["Command Specifications"]

    # Create base output directory if it doesn't exist
    base_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "family_docs")
    os.makedirs(base_output_dir, exist_ok=True)

    # Group commands by family
    families = {}
    for command, values in commands.items():
        if command == "exported":
            continue
        if values.get("level", "") not in ["Basic"]:
            continue

        family = values.get("family", "Other")
        if family not in families:
            families[family] = []

        families[family].append(command)

    # Process each family
    for family, command_list in sorted(families.items()):
        # Create a folder for each family
        family_dir = os.path.join(base_output_dir, family)
        os.makedirs(family_dir, exist_ok=True)

        print(f"\n# Family: {family}\n")

        # Process each command in the family
        for command in sorted(command_list):
            values = commands[command]
            command_description = values.get("description", "")
            command_verb = values.get("verb", "")

            # Create a string buffer for the command's output
            command_output = io.StringIO()

            # Write command header
            command_output.write(f"# **{command}**\n>\t{command_description}\n")
            print(f"\n## {command_verb} **{command}**\n>\t{command_description}")

            # Process command attributes
            attributes = values['Attributes']
            for attribute in attributes:
                for key, value in attribute.items():
                    if value.get('level', "") not in ["Basic"]:
                        continue
                    user_specified = value.get('user_specified', 'true') in ["true", "True"]

                    command_output.write(f"\n## **{key}**\n")
                    print(f"\n### **{key}**")

                    command_output.write(f">\t**Input Required**: {value.get('input_required', 'false')}\n\n")
                    print(f">\tInput Required: {value.get('input_required', 'false')}")

                    command_output.write(f">\t**Description**: {value.get('description', '')}\n\n")
                    print(f">\tDescription: {value.get('description', '')}")

                    labels = value.get("attr_labels", None)
                    if labels:
                        command_output.write(f">\t**Alternative Labels**: {labels}\n\n")
                        print(f">\tAlternative Labels: {labels}")

                    valid_values = value.get("valid_values", None)
                    if valid_values:
                        command_output.write(f">\t**Valid Values**: {valid_values}\n\n")
                        print(f">\tValid Values: {valid_values}")

                    default_value = value.get("default_value", None)
                    if default_value:
                        command_output.write(f">\t**Default Value**: {default_value}\n\n")
                        print(f">\tDefault Value: {default_value}")

            # Save the command to its own file in the family directory
            # Use a sanitized version of the command name for the filename
            command_filename = command.replace(" ", "_").replace(":", "").replace("/", "_")
            command_file_path = os.path.join(family_dir, f"{command_filename}.md")

            with open(command_file_path, 'w') as f:
                f.write(command_output.getvalue())

            logger.info(f"Saved command documentation to {command_file_path}")
            print("\n___\n")




    #

if __name__ == "__main__":
    main()
