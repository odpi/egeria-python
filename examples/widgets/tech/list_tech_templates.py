"""This creates a templates guid file from the core metadata archive"""
from rich.markdown import Markdown
from rich.prompt import Prompt
import os
from pyegeria import AutomatedCuration
from datetime import datetime
import argparse
import time
import sys
from rich import box
from rich.console import Console
from rich.table import Table

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    RegisteredInfo
)


console = Console()
EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get('KAFKA_ENDPOINT', 'localhost:9092')
EGERIA_PLATFORM_URL = os.environ.get('EGERIA_PLATFORM_URL', 'https://localhost:9443')
EGERIA_VIEW_SERVER = os.environ.get('VIEW_SERVER', 'view-server')
EGERIA_VIEW_SERVER_URL = os.environ.get('EGERIA_VIEW_SERVER_URL', 'https://localhost:9443')
EGERIA_INTEGRATION_DAEMON = os.environ.get('INTEGRATION_DAEMON', 'integration-daemon')
EGERIA_ADMIN_USER = os.environ.get('ADMIN_USER', 'garygeeke')
EGERIA_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'secret')
EGERIA_USER = os.environ.get('EGERIA_USER', 'erinoverview')
EGERIA_USER_PASSWORD = os.environ.get('EGERIA_USER_PASSWORD', 'secret')


def display_tech_types(search_string:str, server: str,
                       url: str, username: str, password: str):

    a_client = AutomatedCuration(server, url, username)
    token = a_client.create_egeria_bearer_token(username, password)
    tech_list = a_client.find_technology_types(search_string, page_size=0)

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Technology Templates for: {url} @ {time.asctime()}",
            style="bold white on black",
            row_styles=["bold white on black"],
            header_style="white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Templates from Server '{server}' @ Platform - {url}",
            expand=True,
            # width=500
        )

        table.add_column("Name", width=20)
        table.add_column("Template Name", width=20)
        table.add_column("Template GUID", width = 38,no_wrap=True)
        table.add_column("Placeholders")


        if type(tech_list) is list:
            for item in tech_list:
                if 'deployedImplementationType' not in item['qualifiedName']:
                    continue
                placeholder_table = Table(expand=False, show_lines=True)
                placeholder_table.add_column("Name", width = 20,no_wrap=True)
                placeholder_table.add_column("Type", width = 10)
                placeholder_table.add_column("Required", width = 10)
                placeholder_table.add_column("Example", width = 20)
                placeholder_table.add_column("Description", width = 40)


                name = item.get("name", "none")

                details = a_client.get_technology_type_detail(name)
                if type(details) is str:
                    console.log(f"Missing details for - {name}: {details}")
                    continue

                templates = details.get("catalogTemplates", "Not Found")
                if type(templates) is not str:
                    for template in templates:
                        template_name = template.get("name", None)

                        template_name = f"{name}_Template" if template_name is None else template_name

                        specification = template["specification"]["placeholderProperty"]
                        template_guid = template["relatedElement"]["guid"]

                        for placeholder in specification:
                            placeholder_data_type = placeholder["dataType"]
                            placeholder_description = placeholder["description"]
                            placeholder_name = placeholder["placeholderPropertyName"]
                            placeholder_required = placeholder["required"]
                            placeholder_example = placeholder.get("example", None)
                            placeholder_table.add_row(placeholder_name, placeholder_data_type,  placeholder_required,
                                                      placeholder_example, placeholder_description,)

                        table.add_row(name, template_name, template_guid, placeholder_table)

            return table
        else:
            print("Unknown technology type")
            sys.exit(1)

    try:
        console = Console()
        with console.pager(styles=True):
            console.print(generate_table())

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)
        assert e.related_http_code != "200", "Invalid parameters"
    finally:
        a_client.close_session()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="Password")

    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    password = args.password if args.password is not None else EGERIA_USER_PASSWORD
    guid = None

    try:
        search_string = Prompt.ask("Enter the technology you are searching for:", default="*")
        display_tech_types(search_string, server, url, userid, password)
    except(KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()



