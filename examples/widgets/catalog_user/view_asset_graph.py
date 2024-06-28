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
    AssetCatalog
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

def asset_viewer(asset_name: str, server_name:str, platform_url:str, user:str):

    def build_classifications(classification: dict) -> Markdown:

        class_md = "-"
        for c in classification:
            c_type = c["classificationName"]
            if c_type == "Anchors":
                continue
            class_md += f"* Classification: {c_type}\n"
            class_props = c["classificationProperties"]
            for prop in class_props.keys():
                class_md += f"* {prop}: {class_props[prop]}\n"
        if class_md == "-":
            output = None
        else:
            output = class_md
        return output

    def build_nested_elements(nested_element: dict) -> Markdown:
        ne_md = " "

        ne_created_by = nested_element["versions"]["createdBy"]
        ne_created_at = nested_element["versions"]["createTime"]
        ne_guid = nested_element["guid"]
        guid_list.append(ne_guid)

        ne_type = nested_element["type"]["typeName"]
        ne_classifications = nested_element["classifications"]
        ne_class_md = build_classifications(ne_classifications)
        # ne_class_md = " " if ne_class_md is None else ne_class_md
        ne_props = nested_element["properties"]

        ne_prop_md = ""
        for prop in ne_props.keys():
            ne_prop_md += f"* {prop}: {ne_props[prop]}\n"
        ne_md = (f"Nested Element of Type: {ne_type} with GUID:  {ne_guid} \n "
                 f"* created by {ne_created_by} at time {ne_created_at}\n"
                 f"{ne_prop_md}\n")
        if ne_class_md is not None:
            ne_md += f"* {ne_class_md}"

        output = Markdown(ne_md)
        return output

    try:

        console = Console(width=200)

        a_client = AssetCatalog(view_server, platform,
                                     user_id=user)

        token = a_client.create_egeria_bearer_token(user, "secret")
        asset_info = a_client.find_assets_in_domain(asset_name)
        asset_guid = asset_info[0]['guid']
        guid_list.append(asset_guid)

        asset_graph = a_client.get_asset_graph(asset_guid)
        if type(asset_graph) is not dict:
            print(f"\n No Asset found for {asset_name}")
            sys.exit(1)

        # print(f"\n{json.dumps(asset_graph, indent =2)}\n")
        tree = Tree(f"{asset_name} ({asset_guid})", style = "bold bright_white",guide_style="bold bright_blue")
        style = ""

        asset_name = asset_graph["displayName"]
        qualified_name = asset_graph["qualifiedName"]
        resource_name = asset_graph["resourceName"]

        asset_type = asset_graph["type"]["typeName"]
        asset_origin = asset_graph["origin"]["homeMetadataCollectionName"]
        asset_creation = asset_graph["versions"]["createTime"]
        asset_created_by = asset_graph["versions"]["createdBy"]
        asset_classifications = asset_graph["classifications"]
        asset_nested_elements = asset_graph["anchoredElements"]
        asset_relationships = asset_graph["relationships"]
        asset_class_md = build_classifications(asset_classifications)


        asset_properties = asset_graph["extendedProperties"]
        prop_md = ""
        for prop in asset_properties:
            prop_md = f"{prop_md}* {prop}: {asset_properties[prop]}\n"

        core_md = (f"**Type: {asset_type} Created by: {asset_created_by} on {asset_creation}**\n"
               f"* Qualified Name: {qualified_name}\n "
               f"* Resource Name: {resource_name}\n"
               f"* Display Name: {asset_name}\n"
               f"* Asset Origin: {asset_origin}\n{prop_md}"
               )
        core_md = Markdown(core_md)
        p1 = Panel.fit(core_md, style = "bold bright_white")
        l2 = tree.add(p1)
        if asset_class_md is not None:
            p2 = Panel.fit(Markdown(asset_class_md), style = "bold bright_white")
            l2 = tree.add(p2)

        #
        # Nested Assets
        #
        l2 = tree.add("Nested Elements", style = "bold white")
        for el in asset_nested_elements:
            asset_ne_md = build_nested_elements(el)
            p3 = Panel.fit(asset_ne_md, style = "bold bright_white", title="Nested Elements")
            l2.add(p3)

        #
        # Now work on the Relationships
        #
        for relationship in asset_relationships:
            # Find the end guids - if one isn't in our list then display
            rel_end1 = relationship["end1"]
            rel_end1_type = rel_end1["type"]["typeName"]
            rel_end1_guid = rel_end1["guid"]
            rel_end1_unique_name = rel_end1["uniqueName"]

            rel_end2 = relationship["end2"]
            rel_end2_type = rel_end2["type"]["typeName"]
            rel_end2_guid = rel_end2["guid"]
            rel_end2_unique_name = rel_end2["uniqueName"]

            if (rel_end1_guid not in guid_list) or (rel_end2_guid not in guid_list):
                rel_end1_class_md = build_classifications(rel_end1["classifications"])
                rel_end2_class_md = build_classifications(rel_end2["classifications"])

                relationship_guid = relationship["guid"]
                relationship_type = relationship["type"]["typeName"]
                relationship_created_by = relationship["versions"]["createdBy"]
                relationship_creation_time = relationship["versions"]["createTime"]
                relationship_properties = relationship.get("properties"," ")
                relationship_md = (f"Relationship Type {relationship_type}\n"
                                   f"* GUID: {relationship_guid}\n* Created by: {relationship_created_by} \n"
                                   f"* Creation Time: {relationship_creation_time}\n"
                                   f"* Properties: {relationship_properties}\n")


                rel_md = (
                    f"* Relationship Type: {relationship_type}\n"
                    f"* Relationship GUID: {relationship_guid}\n"
                    f"* Created by: {relationship_created_by} at time {relationship_creation_time}\n"
                )
                rel_end1_md = (
                    f"* End1:\n"
                    f"\t* Type: {rel_end1_type}\n"
                    f"\t* GUID: {rel_end1_guid}\n"
                    f"\t* Unique Name: {rel_end1_unique_name}\n"
                    )

                if rel_end1_class_md is not None:
                    rel_end1_md = rel_end1_md + rel_end1_class_md

                rel_end2_md = (
                    f"* End1:\n"
                    f"\t* Type: {rel_end2_type}\n"
                    f"\t* GUID: {rel_end2_guid}\n"
                    f"\t* Unique Name: {rel_end2_unique_name}\n"
                )

                if rel_end2_class_md is not None:
                    rel_end1_md = rel_end2_md + rel_end2_class_md
                #
                # for prop in relationship_properties.keys():
                #     relationship_md += f"* {prop}: {relationship_properties[prop]}\n"

                relationship_md += rel_end1_md + rel_end2_md

                relationship_panel = Panel.fit(Markdown(relationship_md), style="bold bright_white")
                tree.add(relationship_panel)


        print("\n\n")
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

    asset_name = Prompt.ask("Enter the Asset Name to view:", default="TransMorg-Clinical-Trials-Weeklies")
    asset_viewer(asset_name,server, url, userid)
