"""This creates a templates guid file from the core metadata archive"""
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


def check_if_template(header: dict) -> bool:
    """Check if the the template classification is set"""
    classifications = header.get("classifications", None)
    if classifications is None:
        return False
    for c in classifications:
        if c["type"]["typeName"] == "Template":
            return True
    return False


def list_deployed_catalogs(
    uc_server_name: str,
    server: str,
    url: str,
    username: str,
    password: str,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    c_client = EgeriaTech(server, url, user_id=username, user_pwd=password)
    token = c_client.create_egeria_bearer_token()

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            caption=f"Databases found: {url} - {server} @ {time.asctime()}",
            style="bold bright_white on black",
            row_styles=["bold bright_white on black"],
            header_style="white on dark_blue",
            title_style="bold bright_white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            # title=f"Elements for Open Metadata Type: '{om_type}' ",
            expand=True,
            # width=500
        )

        table.add_column("Catalog Name/GUID", width=38, no_wrap=True)
        table.add_column("Catalog Server")
        table.add_column("Properties")
        table.add_column("Catalog Schemas")

        om_type = "DeployedDatabaseSchema"

        cats = c_client.get_elements_by_classification("Anchors", "Catalog")
        if type(cats) is list:
            for cat in cats:
                header = cat["elementHeader"]

                if check_if_template(header):
                    continue
                el_guid = header["guid"]
                el_name = cat["properties"].get("name", "---")
                el_id = f"{el_name}\n{el_guid}"
                el_home = header["origin"]["homeMetadataCollectionName"]

                el_anchors_md = ""
                class_info = header["classifications"]
                for class_i in class_info:
                    class_prop = class_i.get("classificationProperties", None)
                    if class_prop:
                        for anchor in class_prop.keys():
                            if anchor == "anchorGUID":
                                server_guid = class_prop[anchor]
                            el_anchors_md += f"* **{anchor}**: {class_prop[anchor]}\n"
                el_anchors_out = Markdown(el_anchors_md)

                el_props_md = ""
                for prop in cat["properties"].keys():
                    el_props_md += f"* **{prop}**: {cat['properties'][prop]}\n"
                el_props_out = Markdown(el_props_md)

                schemas = c_client.get_elements_by_classification_with_property_value(
                    "Anchors", el_guid, ["anchorGUID"], "DeployedDatabaseSchema"
                )
                schemas_md = ""
                if type(schemas) is list:
                    cnt = 0
                    for schema in schemas:
                        schema_md = ""
                        schema_props = schema["properties"]
                        for key in schema_props.keys():
                            schema_md += f"* **{key}**: {schema_props[key]}\n"

                        spacer = "---\n" if cnt > 0 else ""
                        cnt += 1
                        schemas_md += f"{spacer}{schema_md}"
                schemas_md_out = Markdown(schemas_md)

                element_info = c_client.get_element_by_guid(server_guid)
                element_info_md = ""
                for key in element_info["properties"].keys():
                    element_info_md += (
                        f"* **{key}**: {element_info['properties'][key]}\n"
                    )
                element_info_out = Markdown(element_info_md)

                table.add_row(
                    el_id,
                    element_info_out,
                    el_props_out,
                    schemas_md_out,
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
        # uc_server_name = Prompt.ask(
        #     "Enter the name of a server to retrieve schemas for", default="*"
        # )
        uc_server_name = None
        list_deployed_catalogs(uc_server_name, server, url, userid, password)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
