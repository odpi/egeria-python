"""
This file contains term-related object_action functions for processing Egeria Markdown
"""
import json
import os
import sys
import time
from typing import Optional

from loguru import logger
from pydantic import ValidationError
from rich import print
from rich.console import Console
from rich.markdown import Markdown

from md_processing.md_processing_utils.common_md_proc_utils import (parse_upsert_command, parse_view_command)
from md_processing.md_processing_utils.common_md_utils import update_element_dictionary
from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, update_a_command)
from md_processing.md_processing_utils.md_processing_constants import (load_commands, ERROR)
from pyegeria import DEBUG_LEVEL, body_slimmer, print_basic_exception, print_validation_error
from pyegeria.egeria_tech_client import EgeriaTech, NO_ELEMENTS_FOUND
from pyegeria.config import settings
from pyegeria.logging_configuration import config_logging
from pyegeria._output_formats import (select_output_format_set, get_output_format_set_heading, get_output_format_set_description)
from pyegeria._exceptions_new import PyegeriaException, print_exception_response

GERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get("EGERIA_VIEW_SERVER_URL", "https://localhost:9443")
EGERIA_INTEGRATION_DAEMON = os.environ.get("EGERIA_INTEGRATION_DAEMON", "integration-daemon")
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get("EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443")
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_WIDTH = os.environ.get("EGERIA_WIDTH", 220)
EGERIA_JUPYTER = os.environ.get("EGERIA_JUPYTER", False)
EGERIA_HOME_GLOSSARY_GUID = os.environ.get("EGERIA_HOME_GLOSSARY_GUID", None)
EGERIA_GLOSSARY_PATH = os.environ.get("EGERIA_GLOSSARY_PATH", None)
EGERIA_ROOT_PATH = os.environ.get("EGERIA_ROOT_PATH", "../../")
EGERIA_INBOX_PATH = os.environ.get("EGERIA_INBOX_PATH", "md_processing/dr_egeria_inbox")
EGERIA_OUTBOX_PATH = os.environ.get("EGERIA_OUTBOX_PATH", "md_processing/dr_egeria_outbox")

load_commands('commands.json')
debug_level = DEBUG_LEVEL

console = Console(width=int(200))

app_config = settings.Environment
config_logging()


def process_format_set_action(
        egeria_client: EgeriaTech,
        format_set_name: str,
        output_format: str = "REPORT",
        search_string: str = "*",
        **kwargs
):
    """
    Looks up the specified output format set, extracts the function and parameters,
    and invokes the function with the parameters.

    Parameters
    ----------
    format_set_name : str
        The name of the output format set to use.
    view_server : str
        The view server name or address where the Egeria services are hosted.
    view_url : str
        The URL of the platform the view server is on.
    user : str
        The user ID for authentication with the Egeria server.
    user_pass : str
        The password for authentication with the Egeria server.
    jupyter : bool, optional
        A boolean indicating whether the output is intended for a Jupyter notebook.
    width : int, optional
        The width of the console output.
    output_format : str, optional
        Format of the output. Default is TABLE.
    **kwargs : dict
        Additional parameters to override the default parameters in the format set.
    """
    # Get the output format set
    format_set = select_output_format_set(format_set_name, output_format)
    if not format_set:
        print(
            f"Error: Output format set '{format_set_name}' does not have a format compatible with output format '{output_format}'.")
        return

    # Check if the format set has an action property
    if "action" not in format_set:
        print(f"Error: Output format set '{format_set_name}' does not have an action property.")
        return

    # put the search string in kwargs
    kwargs['search_string'] = search_string

    # Extract the function and parameters from the action property (now a dict)
    action = format_set["action"]
    func = action.get("function")
    required_params = action.get("required_params", action.get("user_params", []))
    optional_params = action.get("optional_params", [])
    spec_params = action.get("spec_params", {})

    # Create a params dictionary from required/optional and spec_params
    params = {}
    # First handle required params
    if required_params:
        for param in required_params:
            if param in kwargs and kwargs[param] is not None and kwargs[param] != "":
                params[param] = kwargs[param]
            elif param not in kwargs and param not in spec_params:
                print(f"Warning: Required parameter '{param}' not provided for format set '{format_set_name}'.")
    # Then include any provided optional params
    if optional_params:
        for param in optional_params:
            if param in kwargs and kwargs[param] is not None and kwargs[param] != "":
                params[param] = kwargs[param]

    # Add spec_params to params
    params.update(spec_params)

    params['output_format'] = output_format
    params['output_format_set'] = format_set_name

    # Determine the appropriate client class based on the format set name or function
    client_class = None
    method_name = None

    # If function name is provided as a string, parse it to get class and method
    if isinstance(func, str) and "." in func:
        class_name, method_name = func.split(".")
        # if class_name == "CollectionManager":
        #     client_class = CollectionManager
        # elif class_name == "GovernanceOfficer":
        #     client_class = GovernanceOfficer
        # elif class_name == "GlossaryManager":
        #     client_class = GlossaryManager
        # else:
        client_class = EgeriaTech

        # Add more client classes as needed

    # # If client_class is still None, determine based on format set name
    # if client_class is None:
    #     if format_set_name in ["Collections", "Data Dictionary", "Data Specification", "DigitalProducts"]:
    #         client_class = CollectionManager
    #         method_name = "find_collections"
    #     else:
    #         # Default to CollectionManager for now
    #         client_class = CollectionManager

    # Create the client instance


    # If method_name is set, get the method from the egeria_client
    # Note: We need to convert func from string to method reference even if func is already set
    if method_name:
        if hasattr(egeria_client, method_name):
            func = getattr(egeria_client, method_name)
        else:
            print(f"Error: Method '{method_name}' not found in client class '{client_class.__name__}'.")
            return

    # Check if we have a valid function to call
    if not func and not method_name:
        print(f"Error: No valid function found for format set '{format_set_name}'.")
        return

    # egeria_client.create_egeria_bearer_token()

    # # Get heading and description information
    # heading = get_output_format_set_heading(format_set_name)
    # desc = get_output_format_set_description(format_set_name)
    # preamble = f"# {heading}\n{desc}\n\n" if heading and desc else ""

    try:

            # Add output_format to params
            params['output_format'] = output_format

            try:
                if callable(func):
                    # Call the function as an instance method of the client
                    output = func(**params)
                else:
                    # For standalone functions, call with egeria_client as first argument
                    output = func(egeria_client, **params)
            except TypeError as e:
                # Handle parameter mismatch errors
                print(f"Error calling function: {e}")
                print(f"Parameters provided: {params}")
                return

            if output == NO_ELEMENTS_FOUND:
                return f"\n==> No elements found for format set '{format_set_name}'"

            elif isinstance(output, (str, list)) and output_format == "DICT":
                return json.dumps(output, indent=4)
            elif isinstance(output, (str, list)) and output_format in ["REPORT", "LIST", "FORM"]:
                return output ## used to include pre-amble
            elif isinstance(output, (str, list)) and output_format in ["HTML", "MERMAID"]:
                return '\n\n'.join(output)


            elif isinstance(output, (str, list)) and output_format == "TABLE":
                return "Table is not a legal output format for this command."


    except PyegeriaException as e:
        print_basic_exception(e)
    except ValidationError as e:
        print_validation_error(e)


def process_output_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a output requests - view and list commands.

    :param txt: A string representing the input cell to be processed for
        extracting term-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_view_command(egeria_client, object_type, object_action, txt, directive)
    if parsed_output is None:
        logger.error(f"No valid output found for command '{command}'.")
        return None

    attributes = parsed_output['attributes']

    valid = parsed_output['valid']
    print(Markdown(f"Performing {command}"))
    print(Markdown(parsed_output['display']))

    if directive == "display":
        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
            logger.error(msg)
        return valid

    elif directive == "process":
        attributes = parsed_output['attributes']
        search_string = attributes.get('Search String', {}).get('value', '*')
        output_format = attributes.get('Output Format', {}).get('value', 'LIST')
        output_format_set = attributes.get('Output Format Set', {}).get('value', object_type)
        kwargs = parsed_output.get("kwargs", {})
        for key, value in attributes.items():
            kwargs[key] = value.get('value', None) if key not in ["Search String", "Output Format", "Output Format Set"] else None
        kwargs = body_slimmer(kwargs)
        try:
            if not valid:  # First validate the command before we process it
                msg = f"Validation failed for {object_action} `{object_type}`\n"
                logger.error(msg)
                return None

            list_md = process_format_set_action(
                egeria_client,
                output_format_set,
                output_format,
                search_string,
                ** kwargs
            )
            # if output_format == "DICT":
            #     list_md += f"```\n{json.dumps(struct, indent=4)}\n```\n"
            # else:
            #     list_md += struct
            # logger.info(f"Wrote `{object_type}` for search string: `{search_string}`")

            return list_md

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:
        return None
