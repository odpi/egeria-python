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
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
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


def make_prop_md(props: dict) -> str:
    """Given a properties dict, make a markdown string"""
    props_md = ""
    for key in props.keys():
        props_md += f"* {key}: {props[key]}\n"
    return props_md


def list_deployed_database_schemas(
    db_name: str = "*",
    view_server: str = EGERIA_VIEW_SERVER,
    view_url: str = EGERIA_VIEW_SERVER_URL,
    user: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    """List schemas that have been deployed in database catalogs or databases.
    Parameters
    ----------
    db_name : str
        Name of the database or catalog to get schemas for, or '*' for all databases.
    view_server : str
        The view server to connect to.
    view_url : str
        URL of the view server.
    user : str
        Username for authentication.
    user_pass : str
        Password for authentication.
    jupyter : bool
        Whether to force the terminal output to behave as if in a Jupyter notebook.
    width : int
        Width of the console output.
    """
    c_client = EgeriaTech(view_server, view_url, user_id=user, user_pwd=user_pass)
    token = c_client.create_egeria_bearer_token()

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Catalog Schema List @ {time.asctime()}",
            caption=f"Databases found: {view_url} - {view_server} @ {time.asctime()}",
            style="bold bright_white on black",
            row_styles=["bold bright_white on black"],
            header_style="white on dark_blue",
            title_style="bold bright_white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            expand=True,
            # width=500
        )

        table.add_column("Schema in Catalog")
        table.add_column("Schema Properties")
        table.add_column("Cataloged Resource")

        om_type = "DeployedDatabaseSchema"

        # First get the deployed schemas - either all of them or for a specific server
        if db_name in (None, "*"):
            dbs = c_client.get_elements(om_type)
        else:
            # get the guid for the database or catalog and then all schemas anchored on that catalog
            db_guid = c_client.get_guid_for_name(db_name)
            dbs = c_client.get_elements_by_classification_with_property_value(
                "Anchors", db_guid, ["anchorGUID"], om_type
            )
        # Now we should have a list of Database/Catalog Schemas

        if type(dbs) is not list:
            print("No instances found")
            sys.exit(1)

        for element in dbs:
            header = element["elementHeader"]

            if check_if_template(header):
                continue

            el_name = element["properties"].get("name", "---")

            el_guid = header["guid"]

            # get the information about the catalog we are part of
            el_classification = header["classifications"]
            for c in el_classification:
                el_cat_guid = "---"
                if c["type"]["typeName"] == "Anchors":
                    el_anchor_guid = c["classificationProperties"]["anchorGUID"]
                    el_anchor_type_name = c["classificationProperties"][
                        "anchorTypeName"
                    ]
                    el_anchor_domain_name = c["classificationProperties"][
                        "anchorDomainName"
                    ]
                    el_cat_name = "---"
                    if el_anchor_domain_name == "SoftwareCapability":
                        el_cat = c_client.get_element_by_guid(el_anchor_guid)
                        el_cat_name = el_cat["properties"].get("name", None)
                        if el_cat_name is None:
                            el_cat_name = el_cat["properties"].get("qualifiedName", "")
                        el_cat_guid = el_cat["elementHeader"]["guid"]
            el_schema_id = (
                f"{el_name}\n{el_guid}\n\n\t\tin\n\n{el_cat_name}\n{el_cat_guid}"
            )

            # get the schema properties
            el_props_md = make_prop_md(element["properties"])

            # Now get property facets related to us
            el_facets = c_client.get_related_elements(
                el_guid, "ReferenceableFacet", None
            )
            el_facets_md = "---\n**Property Facets:**\n"
            if type(el_facets) is list:
                for facet in el_facets:
                    el_facets_md += make_prop_md(facet["relatedElement"]["properties"])
            else:
                el_facets_md += "--- \n"
            # Add the facet properties under the normal properties
            el_props_out = Markdown(f"{el_props_md}{el_facets_md}")
            # get the Content within our schema
            rel_elements = c_client.get_related_elements(
                el_guid, "DataContentForDataSet", None
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
                    rel_type = rel_element["relationshipHeader"]["type"]["typeName"]
                    rel_guid = rel_element["relationshipHeader"]["guid"]
                    rel_props = rel_element["relatedElement"]["properties"]
                    props_md = ""
                    for key in rel_props.keys():
                        props_md += f"\t* **{key}**: {rel_props[key]}\n"
                    rel_el_md = f"{rel_el_md}\n* **{rel_type}**:\n\t{rel_guid}\n{props_md}{spacer}"
                    # if count > 1 and count < len_els:
                    #     spacer = "---\n"
                    # elif count > len_els:
                    #     spacer = ""
                    # rel_el_md = f"{rel_el_md}\n* **{rel_type}**:\n\t{rel_guid}\n{props_md}{spacer}"
                    if count == len_els:
                        rel_el_md = rel_el_md[:-4]
                rel_el_out = Markdown(rel_el_md)

            table.add_row(
                el_schema_id,
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
