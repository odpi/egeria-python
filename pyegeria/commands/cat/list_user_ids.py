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
    ClassificationManager,
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


def list_user_ids(
    server: str,
    url: str,
    username: str,
    password: str,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    c_client = ClassificationManager(server, url, user_id=username, user_pwd=password)
    token = c_client.create_egeria_bearer_token()
    elements = c_client.get_elements("UserIdentity")

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
            title=f"Elements for Open Metadata Type: 'User Identities' ",
            expand=True,
            # width=500
        )
        table.add_column("Name")
        table.add_column("Job Title")
        table.add_column("UserId")
        table.add_column("Created")
        table.add_column("GUID", width=38, no_wrap=True)
        table.add_column("Qualified Name")

        if type(elements) is list:
            sorted_elements = sorted(
                elements, key=lambda i: i["properties"].get("userId", "---")
            )
            for element in sorted_elements:
                header = element["elementHeader"]
                el_q_name = element["properties"].get("qualifiedName", "---")
                el_create_time = header["versions"]["createTime"][:-10]
                el_guid = header["guid"]
                el_user_id = element["properties"].get("userId", "---")
                full_name = ""
                job = ""

                profile = c_client.get_related_elements(el_guid, "ProfileIdentity")
                if type(profile) is list:
                    for rel in profile:
                        full_name = rel["relatedElement"]["properties"].get(
                            "fullName", "---"
                        )
                        job = rel["relatedElement"]["properties"].get("jobTitle", "---")

                table.add_row(
                    full_name,
                    job,
                    el_user_id,
                    el_create_time,
                    el_guid,
                    el_q_name,
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
        print("Perhaps the type name isn't known")
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
        list_user_ids(server, url, userid, password)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
