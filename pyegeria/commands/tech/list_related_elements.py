"""This creates a templates guid file from the core metadata archive"""
from jedi import Project
from rich.markdown import Markdown
from rich.prompt import Prompt
import os
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
    EgeriaTech,
)

console = Console()
EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "220"))


def list_related_elements(
    element_guid: str,
    om_type: str,
    relationship_type: str,
    server: str,
    url: str,
    username: str,
    password: str,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    c_client = EgeriaTech(server, url, user_id=username, user_pwd=password)
    token = c_client.create_egeria_bearer_token()

    if om_type is not None:
        om_typedef = c_client.get_typedef_by_name(om_type)
        if type(om_typedef) is str:
            print(
                f"The type name '{om_type}' is not known to the Egeria platform at {url} - {server}"
            )
            sys.exit(1)

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            caption=f"Metadata Elements for: {url} - {server} @ {time.asctime()}",
            style="bold bright_white on black",
            row_styles=["bold bright_white on black"],
            header_style="white on dark_blue",
            title_style="bold bright_white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            title=f"Elements related to: '{element_guid}' ",
            expand=True,
            # width=500
        )
        table.add_column("Relationship GUID", width=38, no_wrap=True)
        table.add_column("Rel Header", width=38, no_wrap=True)
        table.add_column("Relationship Props")
        table.add_column("Related GUID", width=38, no_wrap=True)
        table.add_column("Properties")
        table.add_column("Element Header")

        elements = c_client.get_related_elements(
            element_guid, relationship_type, om_type
        )

        if type(elements) is list:
            for element in elements:
                header = element["relationshipHeader"]
                el_type = header["type"]["typeName"]
                el_home = header["origin"]["homeMetadataCollectionName"]
                el_create_time = header["versions"]["createTime"][:-10]
                el_guid = header["guid"]
                el_class = header.get("classifications", "---")
                rel_header_md = (
                    f"* Type: {el_type}\n"
                    f"* Home: {el_home}\n"
                    f"* Created: {el_create_time}\n"
                )
                rel_header_out = Markdown(rel_header_md)
                rel_props = element.get("relationshipProperties", "---")

                rel_props_md = ""
                if type(rel_props) is list:
                    for prop in rel_props.keys():
                        rel_props_md += (
                            f"* **{prop}**: {element['relationshipProperties'][prop]}\n"
                        )
                rel_props_out = Markdown(rel_props_md)

                c_md = ""
                if type(el_class) is list:
                    for classification in el_class:
                        classification_name = classification.get(
                            "classificationName", "---"
                        )
                        c_md = f"* **{classification_name}**\n"
                        class_props = classification.get(
                            "classificationProperties", "---"
                        )
                        if type(class_props) is dict:
                            for prop in class_props.keys():
                                c_md += f"  * **{prop}**: {class_props[prop]}\n"
                c_md_out = Markdown(c_md)

                rel_element = element["relatedElement"]
                rel_el_header = rel_element["elementHeader"]
                rel_type = rel_el_header["type"]["typeName"]
                rel_home = rel_el_header["origin"]["homeMetadataCollectionName"]
                rel_guid = rel_el_header["guid"]

                rel_el_header_md = f"* Type: {rel_type}\n" f"* Home: {rel_home}\n"
                rel_el_header_out = Markdown(rel_el_header_md)

                rel_el_props_md = ""
                for prop in rel_element["properties"].keys():
                    rel_el_props_md += (
                        f"* **{prop}**: {rel_element['properties'][prop]}\n"
                    )
                rel_el_props_out = Markdown(rel_el_props_md)

                table.add_row(
                    el_guid,
                    rel_header_out,
                    rel_props_out,
                    # el_q_name,
                    rel_guid,
                    rel_el_props_out,
                    rel_el_header_out,
                )

            return table
        else:
            print("No instances found")
            sys.exit(1)

    try:
        console = Console(width=width, force_terminal=not jupyter)

        with console.pager(styles=True):
            console.print(generate_table())

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)
        print("\n\nPerhaps the type name isn't known")
    finally:
        c_client.close_session()


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

    try:
        element_guid = Prompt.ask("Guid of base element").strip()
        om_type = Prompt.ask(
            "Enter the Open Metadata Type to find elements of", default=None
        )
        relationship_type = Prompt.ask("Enter the relationship type to follow")

        om_type = om_type.strip() if type(om_type) is str else None
        relationship_type = (
            None if len(relationship_type) == 0 else relationship_type.strip()
        )

        list_related_elements(
            element_guid, om_type, relationship_type, server, url, userid, password
        )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
