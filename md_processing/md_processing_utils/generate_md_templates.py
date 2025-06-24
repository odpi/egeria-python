"""
This file contains general utility functions for processing Egeria Markdown
"""
import os
import sys
from typing import List

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

    """
    glossary_name = "Egeria-Markdown"
    commands = COMMAND_DEFINITIONS["Command Specifications"]
    for command, values in commands.items():
        if command == "exported":
            continue
        if commands[command].get("level","") not in ["Basic"]:
            continue
        command_description = commands[command].get("description","")
        command_verb = commands[command].get("verb","")
        print(f"\n# {command_verb} {command}\n>\t{command_description}")

        attributes = commands[command]['Attributes']
        for attribute in attributes:
            for key, value in attribute.items():
                if value.get('level',"") not in ["Basic"]:
                    continue
                user_specified =  value.get('user_specified', 'true') in ["true", "True"]

                print(f"\n## {key}")

                print(f">\tInput Required: {value.get('input_required', "false")}")

                print(f">\tDescription: {value.get("description","")}")
                labels = value.get("attr_labels", None)
                if labels:
                    print(f">\tAlternative Labels: {labels}")

                valid_values = value.get("valid_values", None)
                if valid_values:
                    print(f">\tValid Values: {valid_values}")
                default_value = value.get("default_value", None)
                if default_value:
                    print(f">\tDefault Value: {default_value}")
        print("\n___\n")




    #

if __name__ == "__main__":
    main()