#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Display the status of cataloged platforms and servers.
"""
import sys
import time
import argparse

from rich import json
from rich.panel import Panel

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    AutomatedCuration
)
from rich.table import Table
from rich.live import Live
from rich.console import Console
from rich.markdown import Markdown
from rich.tree import Tree
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich import print

disable_ssl_warnings = True
console = Console(width=200)

platform = "https://127.0.0.1:9443"
user = "erinoverview"
view_server = "view-server"

guid_list = []

def tech_viewer(tech_name: str, server_name:str, platform_url:str, user:str):

    def build_classifications(classification: dict) -> Markdown:

        class_md = ("\n")
        for c in classification:
            c_type = c["classificationName"]
            if c_type == "Anchors":
                continue
            class_md += f"* Classification: {c_type}\n"
            class_props = c.get("classificationProperties", None)
            if class_props is None:
                continue
            for prop in class_props.keys():
                class_md += f"\t* {prop}: {class_props[prop]}\n"
        if class_md == "-":
            output = None
        else:
            output = class_md
        return output

    try:

        console = Console()

        a_client = AutomatedCuration(view_server, platform,
                                     user_id=user)

        token = a_client.create_egeria_bearer_token(user, "secret")
        tech_elements = a_client.get_technology_type_elements(tech_name, get_templates=True)
        if len(tech_elements) <= 1:
            console.print(f"No elements found for {tech_name}")
            sys.exit(1)
        tree = Tree(f"Deployed Technology Type: {tech_name}", style="bold bright_white", guide_style="bold bright_blue")
        note: str =" "
        for element in tech_elements:
            header = element['elementHeader']
            tech_type = header["type"]["typeName"]
            tech_collection = header["origin"]['homeMetadataCollectionName']
            tech_created_by = header['versions']['createdBy']
            tech_created_at = header['versions']['createTime']
            tech_guid = header['guid']
            tech_classifications = header['classifications']
            class_md = build_classifications(tech_classifications)

            referenceables = element['referenceableProperties']
            tech_qualified_name = referenceables['qualifiedName']
            extended = referenceables['extendedProperties']
            ex_md:str = ""
            for key, value in extended.items():
                ex_md += f"* {key}: {value}\n"

            note = (f"* Qualified Name: {tech_qualified_name}\n"
                          f"* GUID: {tech_guid}\n"
                          f"* Createdy by: {tech_created_by}\n"
                          f"* Created at: {tech_created_at}\n"
                          f"* Home Collection: {tech_collection}\n"
                          f"{class_md}\n"
                          f"{ex_md}\n"
                          )

            interfaces = extended.get('connectorInterfaces', None)
            if interfaces is not None:
                interface_type_name = interfaces['typeName']
                interface_array_cnt = interfaces['arrayCount']
                note += f"* Interface Type: {interface_type_name}\n"
                for i in range(0, int(interface_array_cnt)):
                    note += (f"\t* Type: {interfaces['arrayValues']['propertyValueMap'][str(i)]['typeName']}"
                            f"\tName: {interfaces['arrayValues']['propertiesAsStrings'][str(i)]}\n"
                            )
            note_md = Panel.fit(Markdown(note), style = 'bold bright_white')
            t = tree.add(note_md)

        print(tree)

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException
    ) as e:
        print_exception_response(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    args = parser.parse_args()

    server = args.server if args.server is not None else "view-server"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'erinoverview'

    tech_name = Prompt.ask("Enter the Asset Name to view:", default="Apache Kafka Server")
    tech_viewer(tech_name,server, url, userid)
