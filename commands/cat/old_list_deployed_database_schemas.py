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


def list_deployed_database_schemas(
    db_name: str,
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

        table.add_column("Schema in Catalog")
        table.add_column("Schema Properties")

        # table.add_column("Home Store")
        # table.add_column("GUID", width=38, no_wrap=True)
        # table.add_column("Properties")
        table.add_column("Cataloged Resource")

        om_type = "DeployedDatabaseSchema"

        # get the guid for the database or catalog

        if db_name in (None, "*"):
            dbs = c_client.get_elements(om_type)
        else:
            db_guid = c_client.get_guid_for_name(db_name)
            dbs = c_client.get_elements_by_classification_with_property_value(
                "Anchors", db_guid, ["anchorGUID"], om_type
            )

        if type(dbs) is not list:
            print("No instances found")
            sys.exit(1)

        for element in dbs:
            header = element["elementHeader"]

            if check_if_template(header):
                continue

            el_name = element["properties"].get("name", "---")
            el_type = header["type"]["typeName"]
            el_home = header["origin"]["homeMetadataCollectionName"]
            el_create_time = header["versions"]["createTime"][:-10]
            el_created_by = header["versions"]["createdBy"]
            el_created_md = (
                f"* **Created By**: {el_created_by}\n"
                f"* **Created Time**: {el_create_time}"
            )
            el_created_out = Markdown(el_created_md)

            el_guid = header["guid"]

            el_classification = header["classifications"]
            for c in el_classification:
                if c["type"]["typeName"] == "Anchors":
                    el_anchor_guid = c["classificationProperties"]["anchorGUID"]
                    el_anchor_type_name = c["classificationProperties"][
                        "anchorTypeName"
                    ]
                    if el_anchor_type_name == "Catalog":
                        el_cat = c_client.get_element_by_guid(el_anchor_guid)
                        el_cat_name = el_cat["properties"].get("name", None)
                        if el_cat_name is None:
                            el_cat_name = el_cat["properties"].get(
                                "qualifiedName", "---"
                            )
                        el_cat_guid = el_cat["elementHeader"]["guid"]
            el_schema_id = (
                f"{el_name}\n{el_guid}\n\n\t\tin\n\n{el_cat_name}\n{el_cat_guid}"
            )
            el_props_md = ""
            for prop in element["properties"].keys():
                el_props_md += f"* **{prop}**: {element['properties'][prop]}\n"
            el_props_out = Markdown(el_props_md)

            rel_elements = c_client.get_elements_by_property_value(
                el_guid, ["anchorGUID"]
            )
            schema_md = ""
            count = 0
            rel_el_out = ""
            if type(rel_elements) is list:
                len_els = len(rel_elements)
                rel_el_md = ""
                spacer = "---\n"
                for rel_element in rel_elements:
                    count += 1
                    rel_type = rel_element["elementHeader"]["type"]["typeName"]
                    rel_guid = rel_element["elementHeader"]["guid"]
                    rel_props = rel_element["properties"]
                    props_md = ""
                    for key in rel_props.keys():
                        props_md += f"\t* **{key}**: {rel_props[key]}\n"
                    rel_el_md = f"{rel_el_md}\n* **{rel_type}**:\n\t{rel_guid}\n{props_md}{spacer}"
                    # if count > 1 and count < len_els:
                    #     spacer = "---\n"
                    # elif count > len_els:
                    #     spacer = ""
                    rel_el_md = f"{rel_el_md}\n* **{rel_type}**:\n\t{rel_guid}\n{props_md}{spacer}"
                    if count == len_els:
                        rel_el_md = rel_el_md[:-4]
                rel_el_out = Markdown(rel_el_md)

            table.add_row(
                el_schema_id,
                # el_type,
                # el_created_out,
                # el_home,
                # el_guid,
                el_props_out,
                rel_el_out,
            )

        return table

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
        db_name = Prompt.ask(
            "Enter the name of a database/catalog to retrieve schemas for", default="*"
        )
        list_deployed_database_schemas(db_name, server, url, userid, password)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
