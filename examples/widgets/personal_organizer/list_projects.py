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
from pyegeria import ProjectManager


def display_list(project_name: str, server: str, url: str,
                   username: str,  save_output: bool):

    p_client = ProjectManager(server, url, user_id=username)
    token = p_client.create_egeria_bearer_token(username, "secret")

    def generate_table(project_name: str) -> Table:
        """Make a new table."""
        table = Table(
            title=f"Project List: {project_name}  @ {time.asctime()}",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Project list for Server '{server}' @ Platform - {url}",
            expand=True
        )


        table.add_column("Display Name")
        table.add_column("Project GUID", no_wrap=True,)
        table.add_column("Classifications")
        table.add_column("Qualified Name")
        table.add_column("Identifier")
        table.add_column("Phase")
        table.add_column("Health")
        table.add_column("Status")
        table.add_column("Start Date")
        table.add_column("End Date")
        table.add_column("Description")

        projects = p_client.find_projects(project_name)

        if projects is None:
            name = " "
            guid = " "
            classification = " "
            qualified_name = " "
            identifier = " "
            phase= " "
            health = " "
            status = " "
            start = " "
            end = " "
            description = " "
        elif type(projects) == str:
            raise ValueError("-->This is not a known project")
        else:
            for project in projects:
                classification = ""
                guid = project['elementHeader']['guid']
                props = project["properties"]
                name = props.get("name","None")
                p_class = project['elementHeader'].get("classifications")
                if p_class:
                    for classif in p_class:
                        classification = f"{classif.get('classificationName')}, {classification}"
                qualified_name = props.get("qualifiedName"," ")
                identifier = props.get("identifier", " ")
                phase = props.get("projectPhase", " ")
                health = props.get("projectHealth", " ")
                status = props.get("projectStatus", " ")
                description = props.get("description", " ")
                start = props.get("startDate"," ")
                end = props.get("plannedEndDate", " ")
                additional_properties = project.get('additionalProperties')
                if additional_properties is not None:
                    props = json.dumps(additional_properties)
                table.add_row(
                    name, guid, classification, qualified_name, identifier, phase, health, status, start,
                    end,description)

        p_client.close_session()
        return table

    try:
        # with Live(generate_table(), refresh_per_second=4, screen=True) as live:
        #     while True:
        #         time.sleep(2)
        #         live.update(generate_table())
        console = Console(record=True)
        with console.pager():
            console.print(generate_table(project_name))
        if save_output:
            console.save_html("projects.html")

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException, ValueError) as e:
        if type(e) is str:
            print(e)
        else:
            print_exception_response(e)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--save-output", help="Save output to file?")
    # parser.add_argument("--sponsor", help="Name of sponsor to search")
    args = parser.parse_args()

    server = args.server if args.server is not None else "view-server"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'erinoverview'
    save_output = args.save_output if args.save_output is not None else False
    project_name = Prompt.ask("Enter the Project to retrieve:", default="*")

    display_list(project_name, server, url, userid, save_output)