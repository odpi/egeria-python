#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Display the status of cataloged platforms and servers.
"""
import argparse
import os
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.tree import Tree
from rich import print

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    AssetCatalog,
)

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

disable_ssl_warnings = True

guid_list = []

console = Console(width=EGERIA_WIDTH, force_terminal=(not EGERIA_JUPYTER))


def asset_viewer(
    asset_guid: str,
    server_name: str,
    platform_url: str,
    user: str,
    user_pass: str,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    def build_classifications(classification: dict) -> Markdown:
        class_md = ""
        for c in classification:
            c_type = c["classificationName"]
            if c_type == "Anchors":
                continue
            class_md += f"\n* Classification: {c_type}\n"
            class_props = c.get("classificationProperties", "---")
            if type(class_props) is dict:
                for prop in class_props.keys():
                    class_md += f"\t* {prop}: {class_props[prop]}\n"
        if class_md == "":
            output = None
        else:
            output = class_md
        return output

    def build_nested_elements(nested_element: dict) -> Markdown:
        ne_md = " "
        ne_header = nested_element["elementHeader"]
        ne_created_by = ne_header["versions"]["createdBy"]
        ne_created_at = ne_header["versions"]["createTime"]
        ne_guid = ne_header["guid"]
        guid_list.append(ne_guid)

        ne_type = ne_header["type"]["typeName"]
        ne_classifications = ne_header["classifications"]
        ne_class_md = build_classifications(ne_classifications)
        # ne_class_md = " " if ne_class_md is None else ne_class_md
        ne_props = nested_element.get("properties", "---")
        ne_prop_md = "\n"
        if type(ne_props) is dict:
            for prop in ne_props.keys():
                ne_prop_md += f"\t* {prop}: {ne_props[prop]}\n"
        ne_md = (
            f"Nested Element of Type: {ne_type} with GUID:  {ne_guid} \n "
            f"* created by {ne_created_by} at time {ne_created_at}\n"
            f"\n* Properties:\n{ne_prop_md}\n"
        )

        if ne_class_md is not None:
            ne_md += f"* {ne_class_md}"

        output = Markdown(ne_md)
        return output

    try:
        a_client = AssetCatalog(server_name, platform_url, user_id=user)

        token = a_client.create_egeria_bearer_token(user, user_pass)
        # asset_info = a_client.find_assets_in_domain(asset_name)
        # if type(asset_info) is str:
        #     print("\n No Assets Found - Exiting\n")
        #     sys.exit(1)
        #
        # asset_guid = asset_info[0]['guid']

        guid_list.append(asset_guid)

        asset_graph = a_client.get_asset_graph(asset_guid)
        if type(asset_graph) is not dict:
            print(f"\n No Asset found for {asset_guid}")
            sys.exit(1)

        # print(f"\n{json.dumps(asset_graph, indent =2)}\n")

        asset_display_name = asset_graph["properties"].get("displayName", "---")
        asset_display_description = asset_graph["properties"].get(
            "displayDescription", "---"
        )
        asset_name = asset_graph["properties"].get("name", "---")
        asset_resource_name = asset_graph["properties"].get("resourceName", "---")
        asset_resource_description = asset_graph["properties"].get(
            "resourceDescription", "---"
        )
        qualified_name = asset_graph["properties"].get("qualifiedName", "---")

        tree = Tree(
            f"{asset_name} ({asset_guid})",
            style="bold bright_white on black",
            guide_style="bold bright_blue",
        )
        style = ""
        asset_elements = asset_graph["elementHeader"]
        asset_type = asset_elements["type"]["typeName"]
        asset_deployed_imp_type = asset_graph["properties"].get(
            "deployedImplementationType", "---"
        )

        asset_origin = asset_elements["origin"]["homeMetadataCollectionName"]
        asset_creation = asset_elements["versions"]["createTime"]
        asset_created_by = asset_elements["versions"]["createdBy"]
        asset_classifications = asset_elements["classifications"]
        asset_nested_elements = asset_graph.get("anchoredElements", "----")
        asset_relationships = asset_graph["relationships"]
        asset_class_md = build_classifications(asset_classifications)

        additional_properties = asset_graph["properties"].get(
            "additionalProperties", None
        )
        if additional_properties is not None:
            add_prop_md = "\n* Additional Properties:\n"
            for prop in additional_properties:
                add_prop_md = (
                    f"{add_prop_md}\n\t* {prop}: {additional_properties[prop]}\n"
                )
        else:
            add_prop_md = ""

        extended_properties = asset_graph["properties"].get("extendedProperties", None)
        if extended_properties is not None:
            prop_md = "\n* Extended Properties:\n"
            for prop in extended_properties:
                prop_md = f"{prop_md}\n\t* {prop}: {extended_properties[prop]}\n"
        else:
            prop_md = ""
        core_md = (
            f"**Type: {asset_type}  Created by: {asset_created_by} on {asset_creation}**\n"
            f"* Deployed Implementation Type: {asset_deployed_imp_type}\n"
            f"* Name: {asset_name}\n "
            f"* Asset Resource Name: {asset_resource_name}\n"
            f"* Asset Resource Description: {asset_resource_description}\n "
            f"* Asset Display Name: {asset_display_name}\n"
            f"* Asset Display Description: {asset_display_description}\n "
            f"* Qualified Name: {qualified_name}\n "
            f"* Asset Origin: {asset_origin}\n"
            f" {prop_md}\n"
            f" {add_prop_md}\n"
        )
        core_md = Markdown(core_md)

        p1 = Panel.fit(core_md, style="bold bright_white")
        l2 = tree.add(p1)
        if asset_class_md is not None:
            p2 = Panel.fit(
                Markdown(asset_class_md),
                style="bold bright_white",
                title="Classifications",
            )
            l2 = tree.add(p2)

        #
        # Nested Assets
        #
        if type(asset_nested_elements) is list:
            l2 = tree.add("Nested Elements", style="bold white")
            for el in asset_nested_elements:
                asset_ne_md = build_nested_elements(el)
                p3 = Panel.fit(
                    asset_ne_md, style="bold bright_white", title="Nested Elements"
                )
                l2.add(p3)

        #
        # Now work on the Relationships
        #
        for relationship in asset_relationships:
            # Find the end guids - if one isn't in our list then display
            rel_end1 = relationship["end1"]
            rel_end1_type = rel_end1["type"]["typeName"]
            rel_end1_guid = rel_end1["guid"]
            rel_end1_unique_name = rel_end1.get("uniqueName", "---")

            rel_end2 = relationship["end2"]
            rel_end2_type = rel_end2["type"]["typeName"]
            rel_end2_guid = rel_end2["guid"]
            rel_end2_unique_name = rel_end2.get("uniqueName", "---")

            if (rel_end1_guid not in guid_list) or (rel_end2_guid not in guid_list):
                # rel_end1_class_md = build_classifications(rel_end1["classifications"])
                # rel_end2_class_md = build_classifications(rel_end2["classifications"])

                relationship_guid = relationship["guid"]
                relationship_type = relationship["type"]["typeName"]
                relationship_created_by = relationship["versions"]["createdBy"]
                relationship_creation_time = relationship["versions"]["createTime"]
                relationship_properties = relationship.get("properties", "--- ")
                relationship_md = (
                    f"Relationship Type {relationship_type}\n"
                    f"* GUID: {relationship_guid}\n* Created by: {relationship_created_by} \n"
                    f"* Creation Time: {relationship_creation_time}\n"
                    f"* Properties: {relationship_properties}\n"
                )

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

                # if rel_end1_class_md is not None:
                #     rel_end1_md = rel_end1_class_md + rel_end1_md

                rel_end2_md = (
                    f"* End2:\n"
                    f"\t* Type: {rel_end2_type}\n"
                    f"\t* GUID: {rel_end2_guid}\n"
                    f"\t* Unique Name: {rel_end2_unique_name}\n"
                )

                # if rel_end2_class_md is not None:
                #     rel_end1_md = rel_end2_class_md + rel_end1_md
                #
                # for prop in relationship_properties.keys():
                #     relationship_md += f"* {prop}: {relationship_properties[prop]}\n"

                relationship_md += rel_end1_md + rel_end2_md

                relationship_panel = Panel.fit(
                    Markdown(relationship_md),
                    style="bold bright_white",
                    title="Asset Relationships",
                )
                tree.add(relationship_panel)
        with console.screen():
            print("\n\n")
        print(tree)

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        console.print_exception()
        console.print(
            "\n\n ======> Most likely the GUID you provided is either incorrect or not an asset\n[red bold]"
        )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    try:
        asset_guid = Prompt.ask("Enter the Asset GUID to view:", default="")
        asset_viewer(asset_guid, server, url, userid, user_pass)
    except KeyboardInterrupt as e:
        # console.print_exception()
        pass
    except Exception as e:
        console.print_exception()


if __name__ == "__main__":
    main()
