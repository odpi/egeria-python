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
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))


def list_classified_elements(
    om_type: str,
    classification: str,
    server: str,
    url: str,
    username: str,
    password: str,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    c_client = EgeriaTech(server, url, user_id=username, user_pwd=password)
    token = c_client.create_egeria_bearer_token()

    om_typedef = c_client.get_typedef_by_name(om_type)
    if type(om_typedef) is str:
        print(
            f"The type name '{om_type}' is not known to the Egeria platform at {url} - {server}"
        )
        sys.exit(1)

    elements = c_client.get_elements_by_classification(classification, om_type)

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
            title=f"Elements for Open Metadata Type: '{om_type}' ",
            expand=True,
            # width=500
        )

        table.add_column("Qualified Name")
        table.add_column("Type")
        table.add_column("Created")
        table.add_column("Home Store")
        table.add_column("GUID", width=38, no_wrap=True)
        table.add_column("Properties")
        table.add_column("Classifications")

        if type(elements) is list:
            for element in elements:
                header = element["elementHeader"]
                el_q_name = element["properties"].get("qualifiedName", "---")
                el_type = header["type"]["typeName"]
                el_home = header["origin"]["homeMetadataCollectionName"]
                el_create_time = header["versions"]["createTime"][:-10]
                el_guid = header["guid"]
                el_class = header.get("classifications", "---")

                el_props_md = ""
                for prop in element["properties"].keys():
                    el_props_md += f"* **{prop}**: {element['properties'][prop]}\n"
                el_props_out = Markdown(el_props_md)

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

                table.add_row(
                    el_q_name,
                    el_type,
                    el_create_time,
                    el_home,
                    el_guid,
                    el_props_out,
                    c_md_out,
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
        om_type = Prompt.ask(
            "Enter the Open Metadata Type to find elements of:", default="Project"
        )
        classification = Prompt.ask("Enter the classification to filter by: ")
        list_classified_elements(om_type, classification, server, url, userid, password)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
