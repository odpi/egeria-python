#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A command that takes an output format set name, looks up the format set using select_report_spec,
and invokes the specified function with parameters filled from command line arguments.

This command works with any format set defined in output_formatter.py that has an "action" property.
It dynamically determines the appropriate client class and method to call based on the format set,
and prompts for any required parameters that aren't provided on the command line.

Features:
- Works with any format set that has an "action" property
- Dynamically adds command-line arguments based on the format set's required/optional parameters
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
from pydantic import ValidationError
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
import pydevd_pycharm

from pyegeria import (
    EgeriaTech,
    CollectionManager,
    NO_ELEMENTS_FOUND, GovernanceOfficer, GlossaryManager, print_validation_error,
)
from pyegeria.config import settings
from pyegeria.external_links import ExternalReferences
from pyegeria.logging_configuration import config_logging
from pyegeria._output_format_models import load_format_sets_from_json
from pyegeria.base_report_formats import (select_report_format, get_report_format_heading,
                                          load_user_report_specs, load_report_specs,
                                          get_report_format_description)
from pyegeria._exceptions import PyegeriaException, print_exception_response

# pydevd_pycharm.settrace('host.docker.internal',  # Use 'host.docker.internal' to connect to the host machine
#                              port=5678,               # Port to communicate with PyCharm
#                              stdoutToServer=True,     # Forward stdout to PyCharm
#                              stderrToServer=True,     # Forward stderr to PyCharm
#                              suspend=True)            # Suspend execution until the debugger is connected
#


EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")


app_config = settings.Environment
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
    user: str = settings.User_Profile.user_name,
    user_pass: str = settings.User_Profile.user_pwd,
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
    format_set = select_report_format(format_set_name, output_format)
    if not format_set:
        print(f"Error: Output format set '{format_set_name}' does not have a format compatible with output format '{output_format}'.")
        return

    # Check if the format set has an action property
    if "action" not in format_set:
        print(f"Error: Output format set '{format_set_name}' does not have an action property.")
        return

    # Extract the function and parameters from the action property (now a dict)
    action = format_set["action"]
    func = action.get("function")
    required_params = action.get("required_params", action.get("user_params", []))
    optional_params = action.get("optional_params", [])
    spec_params = action.get("spec_params", {})
    
    # Create a params dictionary from required/optional and spec_params
    params = {}
    for param in required_params:
        if param in kwargs and kwargs[param]:
            params[param] = kwargs[param]
        elif param not in kwargs and param not in spec_params:
            print(f"Warning: Required parameter '{param}' not provided for format set '{format_set_name}'.")
    for param in optional_params:
        if param in kwargs and kwargs[param]:
            params[param] = kwargs[param]
    
    # Add spec_params to params
    params.update(spec_params)

    # Delegate execution to exec_report_spec for canonical behavior
    from pyegeria.format_set_executor import exec_report_spec
    ofmt = (output_format or "TABLE").upper()
    mapped = "DICT" if ofmt == "TABLE" else ofmt
    res = exec_report_spec(
        format_set_name,
        output_format=mapped,
        params=params,
        view_server=view_server,
        view_url=view_url,
        user=user,
        user_pass=user_pass,
    )

    # Handle TABLE rendering locally
    if ofmt == "TABLE":
        if res.get("kind") != "json":
            print("No results or unexpected response:", res)
            return
        data = res.get("data")
        # Render basic table
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
        rows = data if isinstance(data, list) else [data]
        if rows and isinstance(rows[0], dict):
            cols = list(rows[0].keys())
            for c in cols:
                table.add_column(str(c), justify="left", style="cyan")
            for r in rows:
                table.add_row(*[str(r.get(c, "")) for c in cols])
        else:
            table.add_column("Value")
            for r in rows:
                table.add_row(str(r))
        # Optional header
        from pyegeria.base_report_formats import get_report_format_heading, get_report_format_description
        heading = get_report_format_heading(format_set_name)
        desc = get_report_format_description(format_set_name)
        if heading and desc:
            console.print(Markdown(f"# {heading}\n{desc}\n"))
        console.print(table)
        return

    # For non-table formats, write to file based on MIME/kind
    kind = res.get("kind")
    mime = res.get("mime")
    out_dir = os.path.join(app_config.pyegeria_root, app_config.dr_egeria_outbox)
    ts = time.strftime('%Y-%m-%d-%H-%M-%S')
    safe_name = "".join(c for c in format_set_name if c.isalnum() or c in ("-","_","+","."," ")).strip().replace(" ", "_")

    if kind == "text":
        content = res.get("content", "")
        ext = ".html" if mime == "text/html" else ".md"
    elif kind == "json":
        content = json.dumps(res.get("data"), indent=2)
        ext = ".json"
    else:
        content = json.dumps(res, indent=2, default=str)
        ext = ".txt"

    file_name = f"{safe_name}-{ts}{ext}"
    full_file_path = os.path.join(out_dir, file_name)
    os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
    with open(full_file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n==> Output written to {full_file_path}")
    if ext == ".html":
        print(f"\n==> Web link: [{file_name}]({app_config.pyegeria_publishing_root}/{file_name})")
    return

    # Determine the appropriate client class based on the format set name or function
    client_class = None
    method_name = None
    
    # If function name is provided as a string, parse it to get class and method
    if isinstance(func, str) and "." in func:
        class_name, method_name = func.split(".")
        if class_name == "CollectionManager":
            client_class = CollectionManager
        elif class_name == "GovernanceOfficer":
            client_class = GovernanceOfficer
        elif class_name == "GlossaryManager":
            client_class = GlossaryManager
        elif class_name == "ExternalReference":
            client_class = ExternalReferences
        else:
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
    heading = get_report_format_heading(format_set_name)
    desc = get_report_format_description(format_set_name)
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
            print(f"\n==> Calling function: {func} with parameters:{params}")
            try:
                if callable(func):
                    # Call the function as an instance method of the client
                    output = func(**params)
                else:
                    # For standalone functions, call with client as first argument
                    output = func(client, **params)
            except ValidationError as e:
                print_validation_error(e)
                return

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
        else:
            # For TABLE output, add output_format to params
            params['output_format'] = "TABLE"
            print(f"\n==> Calling function: {func} with parameters:{params}")
            # Call the function and create a table
            try:
                if hasattr(client, method_name):  # It's a method of the client
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
                if result[0].get("display_name", None):
                    sorted_results = sorted(result, key=lambda k: k.get("display_name", ""))
                elif result[0].get("Display Name", None):
                    sorted_results = sorted(result, key=lambda k: k.get("Display Name", ""))
                else:
                    sorted_results = result

                # Add columns dynamically based on the first result
                column_headings = list(sorted_results[0].keys())
                for heading in column_headings:
                    if heading == "Usage":
                        table.add_column(heading, justify="left", style="cyan")
                    else:
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
    initial_parser.add_argument("--report", help="Name of the report spec", required=True)
    initial_args, _ = initial_parser.parse_known_args()

    # Get the format set to determine parameters
    format_set_name = initial_args.report
    format_set = select_report_format(format_set_name, "ANY")

    # Check if the format set exists
    if not format_set:
        print(f"Error: Report Spec for '{format_set_name}' not found.")
        print("Available Report Specs:")
        from pyegeria.base_report_formats import report_spec_list
        for name in report_spec_list():
            print(f"  - {name}")
        return
    
    # Create the full parser with all arguments
    parser = argparse.ArgumentParser(description="Execute an action from Report Spec")
    parser.add_argument("--report", help="Name of the report spec", required=True)
    parser.add_argument("--server", help="Name of the server to connect to")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    parser.add_argument("--output-format", help="Output format (TABLE, DICT, FORM, REPORT, HTML, LIST)", 
                        choices=["TABLE", "DICT", "FORM", "REPORT", "HTML", "LIST", "MERMAID"], default="TABLE")



    # Add arguments based on the format set's required/optional params
    required_params = []
    optional_params = []
    if "action" in format_set:
        action = format_set["action"]
        required_params = action.get("required_params", action.get("user_params", []))
        optional_params = action.get("optional_params", [])
        
        for param in sorted(set(required_params + optional_params)):
            parser.add_argument(f"--{param.replace('_', '-')}", help=f"{param.replace('_', ' ')} parameter")
    else:
        print(f"Error: Report Spec '{format_set_name}' does not have an action property.")
        return
    
    args = parser.parse_args()
    app_settings = settings
    app_config = app_settings.Environment

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_view_server_url
    print(f"root path: {app_config.pyegeria_root}, config_file: {app_config.pyegeria_config_file}")
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    format_set_name = args.report
    output_format = args.output_format

    logger.info(f"view server @ {url}")
    # Collect all parameters from args
    kwargs = {}
    for param in sorted(set(required_params + optional_params)):
        arg_name = param.replace('_', '-')
        if hasattr(args, arg_name) and getattr(args, arg_name) is not None:
            kwargs[param] = getattr(args, arg_name)
        elif hasattr(args, param) and getattr(args, param) is not None:
            kwargs[param] = getattr(args, param)
    
    try:
        # If a required parameter is not provided, prompt for it
        for param in required_params:
            if param not in kwargs:
                default_value = "*" if param == "search_string" else ""
                prompt_text = f"Enter {param.replace('_', ' ')}:"
                if default_value:
                    prompt_text += f" (default: {default_value})"
                value = Prompt.ask(prompt_text, default=default_value).strip()
                kwargs[param] = value
        print(f"Using Report Spec {format_set_name} and output format {output_format} with parameters: {kwargs} ")
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