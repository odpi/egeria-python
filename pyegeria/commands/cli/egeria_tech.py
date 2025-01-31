#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


A command line interface for Egeria Data techs.

This is an emerging capability based on the **click** package. Feedback welcome!

"""
import os
import sys

import click
from trogon import tui

from pyegeria.commands.cat.list_tech_types import display_tech_types
from pyegeria.commands.cli.ops_config import Config
from pyegeria.commands.tech.get_guid_info import display_guid
from pyegeria.commands.tech.get_tech_details import tech_details_viewer
from pyegeria.commands.tech.list_asset_types import display_asset_types
from pyegeria.commands.tech.list_registered_services import display_registered_svcs
from pyegeria.commands.tech.list_relationship_types import display_relationship_types
from pyegeria.commands.tech.list_tech_templates import display_templates_spec
from pyegeria.commands.tech.list_valid_metadata_values import display_metadata_values
from pyegeria.commands.tech.list_anchored_elements import display_anchored_elements
from pyegeria.commands.tech.list_all_om_type_elements import list_elements
from pyegeria.commands.tech.list_all_om_type_elements_x import list_elements_x
from pyegeria.commands.tech.list_elements_by_classification_by_property_value import find_elements_by_classification_by_prop_value
from pyegeria.commands.tech.list_elements_by_property_value import find_elements_by_prop_value
from pyegeria.commands.tech.list_elements_by_property_value_x import find_elements_by_prop_value_x
from pyegeria.commands.tech.list_related_elements_with_prop_value import list_related_elements_with_prop_value

from pyegeria.commands.tech.get_element_info import display_elements
from pyegeria.commands.tech.list_related_specification import (
    display_related_specification,
)
from pyegeria.commands.tech.list_all_related_elements import list_related_elements
from pyegeria.commands.tech.list_elements_for_classification import (
    list_classified_elements,
)
from pyegeria.commands.tech.list_gov_action_processes import display_gov_processes
from pyegeria.commands.tech.get_tech_type_template import template_viewer

@tui()
@click.version_option("0.0.1", prog_name="egeria_ops")
@click.group()
@click.option(
    "--server",
    default=os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store"),
    help="Egeria metadata store to work with",
)
@click.option(
    "--url",
    default=os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443"),
    help="URL of Egeria metadata store platform to connect to",
)
@click.option(
    "--integration_daemon",
    default=os.environ.get("EGERIA_INTEGRATION_DAEMON", "integration-daemon"),
    help="Egeria integration daemon to work with",
)
@click.option(
    "--integration_daemon_url",
    default=os.environ.get("EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443"),
    help="URL of Egeria integration daemon platform to connect to",
)
@click.option(
    "--view_server",
    default=os.environ.get("EGERIA_VIEW_SERVER", "view-server"),
    help="Egeria view server to work with",
)
@click.option(
    "--view_server_url",
    default=os.environ.get("EGERIA_VIEW_SERVER_URL", "https://localhost:9443"),
    help="URL of Egeria view server platform to connect to",
)
@click.option(
    "--engine_host",
    default=os.environ.get("EGERIA_ENGINE_HOST", "engine-host"),
    help="Egeria engine host to work with",
)
@click.option(
    "--engine_host_url",
    default=os.environ.get("EGERIA_ENGINE_HOST_URL", "https://localhost:9443"),
    help="URL of Egeria engine host platform to connect to",
)
@click.option(
    "--admin_user",
    default=os.environ.get("EGERIA_ADMIN_USER", "garygeeke"),
    help="Egeria admin user",
)
@click.option(
    "--admin_user_password",
    default=os.environ.get("EGERIA_ADMIN_PASSWORD", "secret"),
    help="Egeria admin password",
)
@click.option(
    "--userid",
    default=os.environ.get("EGERIA_USER", "peterprofile"),
    help="Egeria user",
)
@click.option(
    "--password",
    default=os.environ.get("EGERIA_USER_PASSWORD", "secret"),
    help="Egeria user password",
)
@click.option("--timeout", default=60, help="Number of seconds to wait")
@click.option(
    "--jupyter",
    is_flag=True,
    default=os.environ.get("EGERIA_JUPYTER", "False"),
    help="Enable for rendering in a Jupyter terminal",
)
@click.option(
    "--width",
    default=os.environ.get("EGERIA_WIDTH", "200"),
    help="Screen width, in characters, to use",
)
@click.option(
    "--home_glossary_guid",
    default=os.environ.get("EGERIA_HOME_GLOSSARY_GUID", None),
    help="Glossary guid to use as the home glossary",
)
@click.option(
    "--glossary_path",
    default=os.environ.get("EGERIA_GLOSSARY_PATH", "/home/jovyan/loading-bay/glossary"),
    help="Path to glossary import/export files",
)
@click.pass_context
def cli(
    ctx,
    server,
    url,
    view_server,
    view_server_url,
    integration_daemon,
    integration_daemon_url,
    engine_host,
    engine_host_url,
    admin_user,
    admin_user_password,
    userid,
    password,
    timeout,
    jupyter,
    width,
    home_glossary_guid,
    home_glossary_path,
):
    """An Egeria Command Line interface for Operations"""
    ctx.obj = Config(
        server,
        url,
        view_server,
        view_server_url,
        integration_daemon,
        integration_daemon_url,
        engine_host,
        engine_host_url,
        admin_user,
        admin_user_password,
        userid,
        password,
        timeout,
        jupyter,
        width,
        home_glossary_guid,
        home_glossary_path,
    )
    ctx.max_content_width = 200
    ctx.ensure_object(Config)


@cli.group("show")
@click.pass_context
def show(ctx):
    """Display an Egeria Object"""
    pass


@show.group("info")
@click.pass_context
def show_info(ctx):
    """Show various Egeria information"""
    pass


@show.group("tech-types")
@click.pass_context
def show_tech(ctx):
    """Show information about Egeria technology types"""
    pass


@show.group("elements")
@click.pass_context
def show_elements(ctx):
    """Show information about Egeria elements"""


@show_elements.command("guid-info")
@click.argument("guid", nargs=1)
@click.pass_context
def show_guid_info(ctx, guid):
    """Display guid information

    Usage: show guid-info <a guid>

    """
    c = ctx.obj
    display_guid(guid, c.server, c.url, c.userid, c.password, c.jupyter, c.width)


@show_elements.command("anchored_elements")
@click.pass_context
@click.option(
    "--property_value",
    default="DeployedDatabaseSchema",
    help="value we are searching for",
)
@click.option(
    "--prop-list",
    default="anchorTypeName",
    help="List of properties we are searching",
)
def list_anchored_elements(ctx, property_value: str, prop_list: str):
    """List anchored elements with the specified properties"""
    c = ctx.obj
    if type(prop_list) is str:
        property_names = prop_list.split(",")
    elif type(prop_list) is list:
        property_names = prop_list
    else:
        property_names = []
        print(f"\nError --> Invalid property list - must be a string or list")
        sys.exit(4)
    display_anchored_elements(
        property_value,
        [prop_list],
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.timeout,
        c.jupyter,
        c.width,
    )

@show_elements.command("elements-by-classification")
@click.option(
    "--om-type",
    default="Referenceable",
    help="Open Metadata type to filter by",
)
@click.option(
    "--classification",
    default="GovernanceProject",
    help="Classification to filter byt",
)
@click.pass_context
def show_elements_by_classification(ctx, om_type, classification):
    """Show elements by classification"""
    c = ctx.obj
    list_classified_elements(
        om_type,
        classification,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )

@show_elements.command("elements-by-classification-by-prop-value")
@click.option(
    "--classification",
    default="GovernanceProject",
    help="Classification to filter by",
    )
@click.option(
    "--property_value",
    help="Property value to filter by",
)
@click.option(
    "--property_names",
    help="List of properties to search by",
)
@click.option(
    "--om-type",
    default="Referenceable",
    help="Open Metadata type to filter by",
)
@click.pass_context
def show_elements_by_classification_by_prop(ctx,  classification, property_value, property_names, om_type):
    """Show elements by classification and property value"""
    c = ctx.obj
    find_elements_by_classification_by_prop_value(
        om_type,
        classification,
        property_value,
        [property_names],
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )

@show_elements.command("elements-by-prop-value")
@click.option(
    "--property_value",
    help="Property value to filter by",
)
@click.option(
    "--property_names",
    help="List of properties to search by",
)
@click.option(
    "--om-type",
    default="Referenceable",
    help="Open Metadata type to filter by",
)
@click.option(
    "--extended",
    is_flag=True,
    default=False,
    help="If True, feedback information is displayed",
)
@click.pass_context
def show_elements_by_classification_by_prop(ctx,property_value, property_names, om_type, extended):
    """Show elements by classification and property value"""
    c = ctx.obj
    if extended:
        find_elements_by_prop_value_x(
            om_type,
            property_value,
            [property_names],
            c.view_server,
            c.view_server_url,
            c.userid,
            c.password,
            c.jupyter,
            c.width,
        )
    else:
        find_elements_by_prop_value(
            om_type,
            property_value,
            [property_names],
            c.view_server,
            c.view_server_url,
            c.userid,
            c.password,
            c.jupyter,
            c.width,
            )

@show_elements.command("related-elements")
@click.option(
    "--element-guid",
    help="GUID of the Element to navigate from.",
)
@click.option(
    "--om-type",
    default="Referenceable",
    help="Open metadata type to filter by.",
)
@click.option(
    "--rel-type",
    default="Certification",
    help="Relationship type to follow.",
)
@click.pass_context
def show_related_elements(ctx, element_guid, om_type, rel_type):
    """Show all elements related to specified guid"""
    c = ctx.obj
    list_related_elements(
        element_guid,
        om_type,
        rel_type,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_elements.command("related-elements_by_prop")
@click.option(
    "--element-guid",
    help="GUID of the Element to navigate from.",
)
@click.option(
    "--rel-type",
    default="Certification",
    help="Relationship type to follow.",
)
@click.option(
    "--property_value",
    help="Property value to filter by",
)
@click.option(
    "--property_names",
    help="List of properties to search by",
)
@click.option(
    "--om-type",
    default="Referenceable",
    help="Open metadata type to filter by.",
)

@click.pass_context
def show_related_elements(ctx, element_guid, rel_type, property_value, property_names, om_type):
    """Show elements related to specified guid and property value"""
    c = ctx.obj
    list_related_elements_with_prop_value(
        element_guid,
        rel_type,
        property_value,
        [property_names],
        om_type,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_elements.command("related-specifications")
@click.pass_context
@click.argument("element-guid")
def show_related_specifications(ctx, element_guid):
    """List specifications related to the given Element"""
    c = ctx.obj
    display_related_specification(
        element_guid,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_tech.command("tech-types")
@click.option("--search-string", default="*", help="Tech type to search for")
@click.pass_context
def show_tech_types(ctx, search_string):
    """List deployed technology types

    Usage: show tech-types <optional search-string>

    All tech-types will be returned if no search-string is specified.

    """

    c = ctx.obj
    display_tech_types(
        search_string, c.view_server, c.view_server_url, c.userid, c.password
    )


@show_tech.command("tech-details")
@click.argument("tech-name")
@click.pass_context
def show_tech_details(ctx, tech_name):
    """Display a live status view of Egeria servers for the specified Egeria platform

    Usage: show tech-details <tech-name>

           tech-name is a valid technology name (see 'show tech-types')
    """
    c = ctx.obj
    tech_details_viewer(
        tech_name,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_tech.command("tech-type-templates")
@click.option(
    "--tech-type",
    default="PostgreSQL Server",
    help="Specific tech type to get elements for",
)
@click.pass_context
def show_tech_type_templates(ctx, tech_type):
    """List technology type templates"""
    c = ctx.obj
    template_viewer(
        tech_type,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_info.command("asset-types")
@click.pass_context
def show_asset_types(ctx):
    """Display known asset types"""
    c = ctx.obj
    display_asset_types(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


@show_info.command("registered-services")
@click.option(
    "--services",
    type=click.Choice(
        [
            "all",
            "access-services",
            "common-services",
            "engine-services",
            "governance-services",
            "integration-services",
            "view-services",
        ],
        case_sensitive=False,
    ),
    default="all",
    help="Which service group to display",
)
@click.pass_context
def show_registered_services(ctx, services):
    """Show information about a registered services"""
    c = ctx.obj
    display_registered_svcs(
        services,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_info.command("relationship-types")
@click.option(
    "--om-type",
    default="Referenceable",
    help="Relationship type to get information about",
)
@click.pass_context
def show_relationship_types(ctx, rel_type):
    """Show information about the specified relationship type"""
    c = ctx.obj
    display_relationship_types(
        rel_type,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        False,
        c.jupyter,
        c.width,
    )




@show_tech.command("tech-templates")
@click.pass_context
@click.option(
    "--search-string", default="*", help="Technology type to get information about"
)
def tech_templates(ctx, search_string):
    """Display template information about the specified technology."""
    c = ctx.obj
    template_viewer(
        search_string,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_tech.command("tech-template-spec")
@click.pass_context
@click.option(
    "--search-string", default="*", help="Technology type to get information about"
)
def tech_template_spec(ctx, search_string):
    """Display template specification information about the specified technology."""
    c = ctx.obj
    display_templates_spec(
        search_string,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_info.command("gov-action-processes")
@click.pass_context
@click.option("--search-string", default="*", help="Search string")
def gov_action_processes(ctx, search_string):
    """Display available governance action processes."""
    c = ctx.obj
    display_gov_processes(
        search_string,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_info.command("valid-metadata-values")
@click.pass_context
@click.option("--property", default="projectHealth", help="Metadata property to query")
@click.option("--type-name", default="Project", help="Metadata type to query")
def valid_metadata_values(ctx, property, type_name):
    """Display the valid metadata values for a property and type"""
    c = ctx.obj
    display_metadata_values(
        property,
        type_name,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        False,
        c.jupyter,
        c.width,
    )




@show_info.command("processes")
@click.pass_context
def list_element_info(ctx):
    """Display processes"""
    c = ctx.obj
    list_elements(
        "GovernanceActionProcess",
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_elements.command("get-elements")
@click.pass_context
@click.option("--om_type", default="Referenceable", help="Metadata type to query")
def get_element_info(ctx, om_type):
    """Display graph of elements for an Open Metadata Type"""
    c = ctx.obj
    display_elements(
        om_type,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )

@show_elements.command("elements")
@click.pass_context
@click.option(
    "--extended",
    is_flag=True,
    default=False,
    help="If True, feedback information is displayed",
)
@click.option("--om_type", default="Referenceable", help="Metadata type to query")
def list_all_om_type_elements(ctx, om_type, extended):
    """Display all elements of a specific Open Metadata Type"""
    c = ctx.obj
    if extended:
        list_elements_x(
            om_type,
            c.view_server,
            c.view_server_url,
            c.userid,
            c.password,
            c.jupyter,
            c.width
        )
    else:
        list_elements(
            om_type,
            c.view_server,
            c.view_server_url,
            c.userid,
            c.password,
            c.jupyter,
            c.width
        )

#
#  Tell
#


# @cli.group("tell")
# @click.pass_context
# def tell(ctx):
#     """Perform actions an Egeria Objects"""
#     pass


if __name__ == "__main__":
    cli()
