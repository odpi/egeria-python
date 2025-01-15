"""This displays deployed databases"""
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
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "300"))


def check_if_template(header: dict) -> bool:
    """Check if the the template classification is set"""
    classifications = header.get("classifications", None)
    if classifications is None:
        return False
    for c in classifications:
        if c["type"]["typeName"] == "Template":
            return True
    return False


def list_deployed_databases(
    view_server: str = EGERIA_VIEW_SERVER,
    view_url: str = EGERIA_VIEW_SERVER_URL,
    user: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    """
    Parameters
    ----------
    view_server : str
        The view server name to which the Egeria client will connect. By default, this is set to EGERIA_VIEW_SERVER.
    view_url : str
        The URL of the Egeria view server. By default, this is set to EGERIA_VIEW_SERVER_URL.
    user : str
        The username used for authentication with the Egeria server. By default, it is set to EGERIA_USER.
    user_pass : str
        The password used for authentication with the Egeria server. By default, it is set to EGERIA_USER_PASSWORD.
    jupyter : bool
        A flag indicating whether the output is displayed within a Jupyter notebook. Default is set to EGERIA_JUPYTER.
    width : int
        The width of the output console. By default, it is set to EGERIA_WIDTH.
    """
    c_client = EgeriaTech(view_server, view_url, user_id=user, user_pwd=user_pass)
    token = c_client.create_egeria_bearer_token()

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Database List @ {time.asctime()}",
            caption=f"Databases found: {view_url} - {view_server} @ {time.asctime()}",
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

        table.add_column("Qualified Name")
        table.add_column("Type")
        table.add_column("Created", width=23)
        table.add_column("GUID", width=38, no_wrap=True)
        table.add_column("Properties")
        table.add_column("Schemas")

        om_type = "Database"
        dbs = c_client.get_elements(om_type)
        if type(dbs) is list:
            for element in dbs:
                header = element["elementHeader"]

                if check_if_template(header):
                    continue

                el_q_name = element["properties"].get("qualifiedName", "---")
                el_type = header["type"]["typeName"]
                el_home = header["origin"]["homeMetadataCollectionName"]
                el_create_time = header["versions"]["createTime"][:-10]
                el_created_by = header["versions"]["createdBy"]
                el_created_md = (
                    f"* **Created By**: {el_created_by}\n"
                    f"* **Created Time**: {el_create_time}\n"
                    f"* **Home Store**: {el_home}"
                )
                el_created_out = Markdown(el_created_md)

                el_guid = header["guid"]

                el_props_md = ""
                for prop in element["properties"].keys():
                    el_props_md += f"* **{prop}**: {element['properties'][prop]}\n"
                el_props_out = Markdown(el_props_md)

                rel_elements = c_client.get_related_elements(el_guid)
                schema_md = ""
                count = 0
                rel_cnt = len(rel_elements)
                if type(rel_elements) is list:
                    for rel_element in rel_elements:
                        count += 1
                        rel_type = rel_element["relatedElement"]["elementHeader"][
                            "type"
                        ]["typeName"]
                        rel_guid = rel_element["relatedElement"]["elementHeader"][
                            "guid"
                        ]
                        rel_props = rel_element["relatedElement"]["properties"]
                        props_md = ""
                        for key in rel_props.keys():
                            props_md += f"* **{key}**: {rel_props[key]}\n"
                        rel_el_md = f"* **{rel_type}**: {rel_guid}\n{props_md}\n---\n"
                        if count == rel_cnt:
                            rel_el_md = rel_el_md[:-4]
                    rel_el_out = Markdown(rel_el_md)

                table.add_row(
                    el_q_name,
                    el_type,
                    el_created_out,
                    el_guid,
                    el_props_out,
                    rel_el_out,
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
        list_deployed_databases(server, url, userid, password)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
