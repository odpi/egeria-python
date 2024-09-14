#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for glossary terms
"""
import argparse
import json
import os
import time

from rich import box
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria import ProjectManager, ClassificationManager

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get(
    "EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443"
)
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))


def display_project_list(
    project_name: str,
    server: str,
    url: str,
    username: str,
    user_pass: str,
    save_output: bool,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    p_client = ProjectManager(server, url, user_id=username)
    token = p_client.create_egeria_bearer_token(username, user_pass)
    c_client = ClassificationManager(server, url, token=token)

    def generate_table(project_name: str) -> Table:
        """Make a new table."""
        table = Table(
            title=f"Project List: {project_name}  @ {time.asctime()}",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Project list for Server '{server}' @ Platform - {url}",
            expand=True,
        )

        table.add_column("Project Name")
        table.add_column("Description")

        table.add_column("Classifications")
        table.add_column("Qualified Name")
        table.add_column("Identifier")
        table.add_column("Phase")
        table.add_column("Health")
        table.add_column("Status")
        table.add_column("Start Date")
        table.add_column("End Date")
        table.add_column("Contracts")

        projects = p_client.find_projects(project_name)

        if projects is None:
            name = " "
            guid = " "
            classification = " "
            qualified_name = " "
            identifier = " "
            phase = " "
            health = " "
            status = " "
            start = " "
            end = " "
            description = " "
        elif type(projects) == str:
            raise ValueError("-->This is not a known project")
        else:
            sorted_projects = sorted(
                projects, key=lambda k: k["properties"].get("name", "---")
            )

            for project in sorted_projects:
                classification = ""
                guid = project["elementHeader"]["guid"]
                props = project["properties"]
                name = props.get("name", "None")
                p_class = project["elementHeader"].get("classifications")
                if p_class:
                    for classif in p_class:
                        classification += f"* {classif.get('classificationName')}\n"
                qualified_name = props.get("qualifiedName", " ")
                identifier = props.get("identifier", " ")
                phase = props.get("projectPhase", " ")
                health = props.get("projectHealth", " ")
                status = props.get("projectStatus", " ")
                description = props.get("description", " ")
                start = props.get("startDate", " ")[0:10]
                end = props.get("plannedEndDate", " ")
                additional_properties = project.get("additionalProperties")
                if additional_properties is not None:
                    props = json.dumps(additional_properties)

                governed_by = c_client.get_related_elements(guid, "GovernedBy")
                if type(governed_by) is list:
                    for gov in governed_by:
                        rel_guid = gov["relatedElement"]["elementHeader"]["guid"]
                        rel_title = gov["relatedElement"]["properties"].get(
                            "title", "---"
                        )
                        certified_partner = f"{rel_title}: \n"
                        certified = c_client.get_related_elements(
                            rel_guid, "Certification"
                        )
                        if type(certified) is list:
                            for rel_elem in certified:
                                p_name = rel_elem["relatedElement"]["properties"][
                                    "name"
                                ]
                                certified_partner += f"* {p_name}\n"
                else:
                    certified_partner = "---"

                table.add_row(
                    name,
                    description,
                    classification,
                    qualified_name,
                    identifier,
                    phase,
                    health,
                    status,
                    start,
                    end,
                    certified_partner,
                )

        p_client.close_session()
        return table

    try:
        # with Live(generate_table(), refresh_per_second=4, screen=True) as live:
        #     while True:
        #         time.sleep(2)
        #         live.update(generate_table())
        console = Console(
            record=True, width=width, force_terminal=not jupyter, soft_wrap=True
        )
        with console.pager():
            console.print(generate_table(project_name), soft_wrap=True)
        if save_output:
            console.save_html("projects.html")

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
        ValueError,
    ) as e:
        if type(e) is str:
            print(e)
        else:
            print_exception_response(e)
    except KeyboardInterrupt:
        pass
    finally:
        p_client.close_session()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--save-output", help="Save output to file?")
    parser.add_argument("--password", help="User Password")
    # parser.add_argument("--sponsor", help="Name of sponsor to search")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    try:
        save_output = args.save_output if args.save_output is not None else False
        project_name = Prompt.ask("Enter the Project to retrieve:", default="*")
        display_project_list(project_name, server, url, userid, user_pass, save_output)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
