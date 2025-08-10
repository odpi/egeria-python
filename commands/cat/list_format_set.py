#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A command that takes an output format set name, looks up the format set using select_output_format_set,
and invokes the specified function with parameters filled from command line arguments.

This command works with any format set defined in output_formatter.py that has an "action" property.
It dynamically determines the appropriate client class and method to call based on the format set,
and prompts for any required parameters that aren't provided on the command line.

Features:
- Works with any format set that has an "action" property
- Dynamically adds command-line arguments based on the format set's user_params
- Prompts for required parameters if not provided
- Supports multiple output formats (TABLE, DICT, FORM, REPORT, HTML, LIST)
- Handles both instance methods and standalone functions
- Provides informative error messages

Examples:
    # List all collections using the Collections format set
    format_set_action --format-set Collections --search-string "*" --output-format TABLE

    # Output collections in DICT format
    format_set_action --format-set Collections --search-string "*" --output-format DICT

    # Use a specific search string
    format_set_action --format-set Collections --search-string "Data*" --output-format TABLE
    
    # Use a different format set (Data Dictionary)
    format_set_action --format-set "Data Dictionary" --search-string "*" --output-format TABLE
    
    # Use a format set with multiple parameters (will prompt for missing parameters)
    format_set_action --format-set DigitalProducts --output-format REPORT
"""
import argparse
import json
import os
import time

from loguru import logger
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
import pydevd_pycharm

from pyegeria import (
    EgeriaTech,
    NO_ELEMENTS_FOUND,
    # config_logging,
    # get_app_config
)
from pyegeria.load_config import get_app_config
from pyegeria.logging_configuration import config_logging
from pyegeria._output_formats import select_output_format_set, get_output_format_set_heading, \
    get_output_format_set_description
from pyegeria._exceptions_new import PyegeriaException, print_exception_response
from pyegeria.egeria_tech_client import EgeriaTech

# pydevd_pycharm.settrace('host.docker.internal',  # Use 'host.docker.internal' to connect to the host machine
#                              port=5678,               # Port to communicate with PyCharm
#                              stdoutToServer=True,     # Forward stdout to PyCharm
#                              stderrToServer=True,     # Forward stderr to PyCharm
#                              suspend=True)            # Suspend execution until the debugger is connected
#


EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

app_settings = get_app_config()
app_config = app_settings.Environment
config_logging()

print(f"Console width is {app_config.console_width}")
console = Console(
    style="bold bright_white on black",
    width=app_config.console_width,
    force_terminal=not app_config.egeria_jupyter,
    )

def execute_format_set_action(
    format_set_name: str,
    view_server: str = app_config.egeria_view_server,
    view_url: str = app_config.egeria_view_server_url,
    user: str = app_settings.User_Profile.user_name,
    user_pass: str = app_settings.User_Profile.user_pwd,
    output_format: str = "TABLE",
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
    # logger.info(f"Entering execute_format_set_action, format set name: {format_set_name}, search_string: {kwargs.get('search_string',"meow")}")
    # logger.info(json.dumps(kwargs, indent=2))
    format_set = select_output_format_set(format_set_name, output_format)
    if not format_set:
        print(f"Error: Output format set '{format_set_name}' does not have a format compatible with output format '{output_format}'.")
        return

    # Check if the format set has an action property
    if "action" not in format_set:
        print(f"Error: Output format set '{format_set_name}' does not have an action property.")
        return

    # Extract the function and parameters from the action property
    action = format_set["action"][0]  # Assuming there's only one action
    func = action.get("function")
    user_params = action.get("user_params", [])
    spec_params = action.get("spec_params", {})
    
    # Create a params dictionary from user_params and spec_params
    params = {}
    for param in user_params:
        if param in kwargs and kwargs[param]:
            params[param] = kwargs[param]
        elif param not in kwargs and param not in spec_params:
            print(f"Warning: Required parameter '{param}' not provided for format set '{format_set_name}'.")
    
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
        # elif class_name == "EgeriaTech":
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
    client = client_class(view_server, view_url, user_id=user, user_pwd=user_pass)
    
    # If method_name is set, get the method from the client
    # Note: We need to convert func from string to method reference even if func is already set
    if method_name:
        if hasattr(client, method_name):
            func = getattr(client, method_name)
        else:
            print(f"Error: Method '{method_name}' not found in client class '{client_class.__name__}'.")
            return
    
    # Check if we have a valid function to call
    if not func and not method_name:
        print(f"Error: No valid function found for format set '{format_set_name}'.")
        return
    
    client.create_egeria_bearer_token()

    # Get heading and description information
    heading = get_output_format_set_heading(format_set_name)
    desc = get_output_format_set_description(format_set_name)
    preamble = f"# {heading}\n{desc}\n\n" if heading and desc else ""

    try:
        # Invoke the function with the parameters
        if output_format != "TABLE":
            file_path = os.path.join(app_config.pyegeria_root, app_config.dr_egeria_outbox)
            if output_format == "HTML":
                file_name = f"{format_set_name}-{time.strftime('%Y-%m-%d-%H-%M-%S')}.html"
            elif output_format == "JSON":
                file_name = f"{format_set_name}-{time.strftime('%Y-%m-%d-%H-%M-%S')}.json"
            elif output_format == "DICT":
                file_name = f"{format_set_name}-{time.strftime('%Y-%m-%d-%H-%M-%S')}.py"
            elif output_format == "MERMAID":
                file_name = f"{format_set_name}-{time.strftime('%Y-%m-%d-%H-%M-%S')}.md"
            else:
                file_name = f"{format_set_name}-{time.strftime('%Y-%m-%d-%H-%M-%S')}.md"
            full_file_path = os.path.join(file_path, file_name)
            os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
            
            # Add output_format to params
            params['output_format'] = output_format
            
            # Call the function with the parameters
            try:
                if isinstance(func, type(client.find_collections)):  # It's a method of the client
                    # Call the function as an instance method of the client
                    output = func(**params)
                else:
                    # For standalone functions, call with client as first argument
                    output = func(client, **params)
            except TypeError as e:
                # Handle parameter mismatch errors
                print(f"Error calling function: {e}")
                print(f"Parameters provided: {params}")
                return
            
            if output == NO_ELEMENTS_FOUND:
                print(f"\n==> No elements found for format set '{format_set_name}'")
                return
            elif isinstance(output, (str, list)) and output_format == "DICT":
                output = json.dumps(output, indent=4)
            elif isinstance(output, (str, list)) and output_format in[ "REPORT" ]:
                output = preamble + output
            elif isinstance(output, (str, list)) and output_format == "HTML":
                pass

            with open(full_file_path, 'w') as f:
                f.write(output)
            print(f"\n==> Output written to {full_file_path}")
            if output_format == "HTML":
                print(f"\n==> Web link: [{file_name}]({app_config.pyegeria_publishing_root}/{file_name}")
            return

        # For TABLE output, add output_format to params
        params['output_format'] = "DICT"
        
        # Call the function and create a table
        try:
            if isinstance(func, type(client.find_collections)):  # It's a method of the client
                # Call the function as an instance method of the client
                result = func(**params)
            else:
                # For standalone functions, call with client as first argument
                result = func(client, **params)
        except TypeError as e:
            # Handle parameter mismatch errors
            print(f"Error calling function: {e}")
            print(f"Parameters provided: {params}")
            return
        
        if not result or result == NO_ELEMENTS_FOUND:
            print(f"\n==> No elements found for format set '{format_set_name}'")
            return
        

        if heading and desc:
            console.print(Markdown(preamble))

        # Create a table for the results
        table = Table(
            title=f"{format_set_name} @ {time.asctime()}",
            style="bright_white on black",
            header_style="bright_white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"View Server '{view_server}' @ Platform - {view_url}",
            expand=True,
        )
        
        # Handle both list and dictionary results
        if isinstance(result, list):
            if not result:
                print(f"\n==> No elements found for format set '{format_set_name}'")
                return
                
            # Sort the results by display_name if available
            if "display_name" in result[0]:
                sorted_results = sorted(result, key=lambda k: k.get("display_name", ""))
            elif "Display Name" in result[0]:
                sorted_results = sorted(result, key=lambda k: k.get("Display Name", ""))
            else:
                sorted_results = result
                
            # Add columns dynamically based on the first result
            column_headings = list(sorted_results[0].keys())
            for heading in column_headings:
                table.add_column(heading, justify="left", style="cyan")
                
            # Add rows
            for item in sorted_results:
                row_values = []
                for key in column_headings:
                    value = item.get(key, "")
                    row_values.append(str(value))
                    
                table.add_row(*row_values)
        else:
            # Handle single dictionary result
            column_headings = list(result.keys())
            for heading in column_headings:
                table.add_column(heading, justify="left", style="cyan")
                
            row_values = []
            for key in column_headings:
                value = result.get(key, "")
                row_values.append(str(value))
                
            table.add_row(*row_values)
            
        # Print the table

        console.print(table)

    except PyegeriaException as e:
        print_exception_response(e)
    finally:
        client.close_session()


def main():
    # First, parse just the format-set argument to determine which other arguments to add
    logger.enable("pyegeria")
    initial_parser = argparse.ArgumentParser(add_help=False)
    initial_parser.add_argument("--format-set", help="Name of the output format set", required=True)
    initial_args, _ = initial_parser.parse_known_args()

    # Get the format set to determine user_params
    format_set_name = initial_args.format_set
    format_set = select_output_format_set(format_set_name, "ANY")

    # Check if the format set exists
    if not format_set:
        print(f"Error: Format set for '{format_set_name}' not found.")
        print("Available format sets:")
        from pyegeria._output_formats import output_format_set_list
        for name in output_format_set_list():
            print(f"  - {name}")
        return
    
    # Create the full parser with all arguments
    parser = argparse.ArgumentParser(description="Execute an action from an output format set")
    parser.add_argument("--format-set", help="Name of the output format set", required=True)
    parser.add_argument("--server", help="Name of the server to connect to")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    parser.add_argument("--output-format", help="Output format (TABLE, DICT, FORM, REPORT, HTML, LIST)", 
                        choices=["TABLE", "DICT", "FORM", "REPORT", "HTML", "LIST", "MERMAID"], default="TABLE")



    # Add arguments based on the format set's user_params
    user_params = []
    if "action" in format_set:
        action = format_set["action"][0]  # Assuming there's only one action
        user_params = action.get("user_params", [])
        
        for param in user_params:
            parser.add_argument(f"--{param.replace('_', '-')}", help=f"{param.replace('_', ' ')} parameter")
    else:
        print(f"Error: Format set '{format_set_name}' does not have an action property.")
        return
    
    args = parser.parse_args()
    app_settings = get_app_config()
    app_config = app_settings.Environment

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_view_server_url
    print(f"root path: {app_config.pyegeria_root}, config_file: {app_config.pyegeria_config_file}")
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    format_set_name = args.format_set
    output_format = args.output_format

    logger.info(f"view server @ {url}")
    # Collect all user parameters from args
    kwargs = {}
    for param in user_params:
        arg_name = param.replace('_', '-')
        if hasattr(args, arg_name) and getattr(args, arg_name) is not None:
            kwargs[param] = getattr(args, arg_name)
        elif hasattr(args, param) and getattr(args, param) is not None:
            kwargs[param] = getattr(args, param)
    
    try:
        # If a required parameter is not provided, prompt for it
        for param in user_params:
            if param not in kwargs:
                default_value = "*" if param == "search_string" else ""
                prompt_text = f"Enter {param.replace('_', ' ')}:"
                if default_value:
                    prompt_text += f" (default: {default_value})"
                value = Prompt.ask(prompt_text, default=default_value).strip()
                kwargs[param] = value
        print(f"Using format set {format_set_name} and output format {output_format} with parameters: {kwargs} ")
        execute_format_set_action(
            format_set_name=format_set_name,
            view_server=server,
            view_url=url,
            user=userid,
            user_pass=user_pass,
            output_format=output_format,
            **kwargs
        )

    except KeyboardInterrupt:
        pass

    except PyegeriaException as e:
        print_exception_response(e)


if __name__ == "__main__":
    main()