"""This creates a templates guid file from the core metadata archive"""

import argparse
import os
import sys
import time
from typing import Union

import nest_asyncio
from rich import box
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from textual.widgets import DataTable

from pyegeria import (
    PyegeriaException,
    print_basic_exception,
    settings, load_app_config, pretty_print_config,
    config_logging,
    AutomatedCuration,
)


app_config = settings.Environment
config_path = os.path.join(app_config.pyegeria_config_directory, app_config.pyegeria_config_file)

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

conf = load_app_config(config_path)
# print(f"Loading config from {config_path} and mermaid folder is {EGERIA_MERMAID_FOLDER}")
console = Console(width = app_config.console_width)
config_logging()



def list_templates(
    search_string: str, server: str, url: str, username: str, password: str
) -> []:
    """Return a list of templates for one or more technology type"""
    a_client = AutomatedCuration(server, url, username)
    token = a_client.create_egeria_bearer_token(username, password)
    tech_list = a_client.find_technology_types(search_string, page_size=0)
    tech_info_list: dict = []

    if type(tech_list) is list:
        for item in tech_list:
            if "deployedImplementationType" not in item["qualifiedName"]:
                continue

            details = a_client.get_tech_type_detail(item["displayName"])
            entry = {details["displayName"]: {}}
            if type(details) is str:
                tech_info_list.append(entry)
                continue
            templates = details.get("catalogTemplates", "Not Found")
            if type(templates) is list:
                t_list = []
                entry = {details["displayName"]: {}}
                for template in templates:
                    t_list.append({"template": template["displayName"]})
                entry[details["displayName"]] = t_list
                tech_info_list.append(entry)
    return tech_info_list


def add_row(
    table: Union[Table, DataTable],
    displayName: str,
    template_name: str,
    template_guid: str,
    placeholder_table: Table,
) -> Table | DataTable:
    if isinstance(table, Table):
        table.add_row(displayName, template_name, template_guid, placeholder_table)
    elif isinstance(table, DataTable):
        table.add_row(displayName, template_name, template_guid, placeholder_table)

    return table


def display_templates_spec(
    search_string: str,
    server: str,
    url: str,
    username: str,
    password: str,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
    data_table: bool = False,
) -> Table | DataTable:
    a_client = AutomatedCuration(server, url, username)
    nest_asyncio.apply()
    token = a_client.create_egeria_bearer_token(username, password)
    tech_list = a_client.find_technology_types(search_string, page_size=0)

    def generate_table(data_table: bool) -> Table | DataTable:
        """Make a new table."""
        if data_table:
            table = DataTable()
            table.add_columns("Name", "Template Name", "Template GUID", "Placeholders")
        else:
            table = Table(
                title=f"Technology Templates for: {url} @ {time.asctime()}",
                style="bold bright_white on black",
                row_styles=["bold bright_white on black"],
                header_style="white on dark_blue",
                title_style="bold bright_white on black",
                caption_style="white on black",
                show_lines=True,
                box=box.ROUNDED,
                caption=f"Templates from Server '{server}' @ Platform - {url}",
                expand=True,
                # width=500
            )

            table.add_column("Name", width=20)
            table.add_column("Template Name", width=20)
            table.add_column("Template GUID", width=38, no_wrap=True)
            table.add_column("Placeholders")

        if type(tech_list) is list:
            for item in tech_list:
                if "deployedImplementationType" not in item["qualifiedName"]:
                    continue
                placeholder_table = Table(expand=False, show_lines=True)
                placeholder_table.add_column("Name", width=20, no_wrap=True)
                placeholder_table.add_column("Type", width=10)
                placeholder_table.add_column("Required", width=10)
                placeholder_table.add_column("Example", width=20)
                placeholder_table.add_column("Description", width=40)

                displayName = item.get("displayName", "none")

                details = a_client.get_tech_type_detail(displayName)
                if type(details) is str:
                    console.log(f"Missing details for - {displayName}: {details}")
                    continue

                templates = details.get("catalogTemplates", "Not Found")
                if type(templates) is not str:
                    for template in templates:
                        template_name = template.get("displayName", None)

                        template_name = (
                            f"{displayName}_Template"
                            if template_name is None
                            else template_name
                        )

                        specification = template["specification"]["placeholderProperty"]
                        template_guid = template["relatedElement"]['elementHeader']["guid"]

                        for placeholder in specification:
                            placeholder_data_type = placeholder["dataType"]
                            placeholder_description = placeholder["description"]
                            placeholder_name = placeholder["name"]
                            placeholder_required = str(placeholder["required"])
                            placeholder_example = placeholder.get("example", None)
                            placeholder_table.add_row(
                                placeholder_name,
                                placeholder_data_type,
                                placeholder_required,
                                placeholder_example,
                                placeholder_description,
                            )

                        # table.add_row(displayName, template_name, template_guid, placeholder_table)
                        table = add_row(
                            table, displayName, template_name, template_guid, placeholder_table
                        )

            return table
        else:
            print("Unknown technology type")
            sys.exit(1)

    try:
        if data_table:
            return generate_table(data_table)
        else:
            console = Console(width=width, force_terminal=not jupyter)

            with console.pager(styles=True):
                console.print(generate_table(data_table))

    except (
        PyegeriaException
    ) as e:
        print_basic_exception(e)
        assert e.related_http_code != "200", "Invalid parameters"
    except Exception as e:
        console.print_exception(show_locals=True)
    finally:
        a_client.close_session()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="Password")

    args = parser.parse_args()

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_view_server_url
    userid = args.userid if args.userid is not None else EGERIA_USER
    password = args.password if args.password is not None else EGERIA_USER_PASSWORD
    guid = None

    try:
        search_string = Prompt.ask(
            "Enter the technology you are searching for:", default="*"
        )
        display_templates_spec(
            search_string, server, url, userid, password, data_table=False
        )
    except KeyboardInterrupt:
        pass


# def display_templates_spec(
#     search_string: str,
#     server: str,
#     url: str,
#     username: str,
#     password: str,
#     jupyter: bool = EGERIA_JUPYTER,
#     width: int = EGERIA_WIDTH,
# ):
#     a_client = AutomatedCuration(server, url, username)
#     token = a_client.create_egeria_bearer_token(username, password)
#     tech_list = a_client.find_technology_types(search_string, page_size=0)
#
#     def generate_table() -> Table:
#         """Make a new table."""
#         table = Table(
#             title=f"Technology Templates for: {url} @ {time.asctime()}",
#             style="bold bright_white on black",
#             row_styles=["bold bright_white on black"],
#             header_style="white on dark_blue",
#             title_style="bold bright_white on black",
#             caption_style="white on black",
#             show_lines=True,
#             box=box.ROUNDED,
#             caption=f"Templates from Server '{server}' @ Platform - {url}",
#             expand=True,
#             # width=500
#         )
#
#         table.add_column("Name", width=20)
#         table.add_column("Template Name", width=20)
#         table.add_column("Template GUID", width=38, no_wrap=True)
#         table.add_column("Placeholders")
#
#         if type(tech_list) is list:
#             for item in tech_list:
#                 if "deployedImplementationType" not in item["qualifiedName"]:
#                     continue
#                 placeholder_table = Table(expand=False, show_lines=True)
#                 placeholder_table.add_column("Name", width=20, no_wrap=True)
#                 placeholder_table.add_column("Type", width=10)
#                 placeholder_table.add_column("Required", width=10)
#                 placeholder_table.add_column("Example", width=20)
#                 placeholder_table.add_column("Description", width=40)
#
#                 displayName = item.get("displayName", "none")
#
#                 details = a_client.get_tech_type_detail(displayName)
#                 if type(details) is str:
#                     console.log(f"Missing details for - {displayName}: {details}")
#                     continue
#
#                 templates = details.get("catalogTemplates", "Not Found")
#                 if type(templates) is not str:
#                     for template in templates:
#                         template_name = template.get("displayName", None)
#
#                         template_name = (
#                             f"{displayName}_Template"
#                             if template_name is None
#                             else template_name
#                         )
#
#                         specification = template["specification"]["placeholderProperty"]
#                         template_guid = template["relatedElement"]["guid"]
#
#                         for placeholder in specification:
#                             placeholder_data_type = placeholder["dataType"]
#                             placeholder_description = placeholder["description"]
#                             placeholder_name = placeholder["placeholderPropertyName"]
#                             placeholder_required = placeholder["required"]
#                             placeholder_example = placeholder.get("example", None)
#                             placeholder_table.add_row(
#                                 placeholder_name,
#                                 placeholder_data_type,
#                                 placeholder_required,
#                                 placeholder_example,
#                                 placeholder_description,
#                             )
#
#                         table.add_row(
#                             displayName, template_name, template_guid, placeholder_table
#                         )
#
#             return table
#         else:
#             print("Unknown technology type")
#             sys.exit(1)
#
#     try:
#         console = Console(width=width, force_terminal=not jupyter)
#
#         with console.pager(styles=True):
#             console.print(generate_table())
#
#     except (
#         PyegeriaInvalidParameterException,
#         PyegeriaAPIException,
#         PyegeriaUnauthorizedException,
#     ) as e:
#         print_exception_response(e)
#         assert e.related_http_code != "200", "Invalid parameters"
#     finally:
#         a_client.close_session()
#
#
# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--server", help="Name of the server to display status for")
#     parser.add_argument("--url", help="URL Platform to connect to")
#     parser.add_argument("--userid", help="User Id")
#     parser.add_argument("--password", help="Password")
#
#     args = parser.parse_args()
#
#     server = args.server if args.server is not None else EGERIA_VIEW_SERVER
#     url = args.url if args.url is not None else EGERIA_PLATFORM_URL
#     userid = args.userid if args.userid is not None else EGERIA_USER
#     password = args.password if args.password is not None else EGERIA_USER_PASSWORD
#     guid = None
#
#     try:
#         search_string = Prompt.ask(
#             "Enter the technology you are searching for:", default="*"
#         )
#         # display_templates_spec(search_string, server, url, userid, password)
#         list_templates(search_string, server, url, userid, password)
#     except KeyboardInterrupt:
#         pass
#
#
if __name__ == "__main__":
    main()
