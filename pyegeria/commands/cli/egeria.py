#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


A command line interface for Egeria Users - all commands

This is an emerging capability based on the **click** package. Feedback welcome!

"""
import os
import sys

import click
from trogon import tui

from pyegeria.commands.cli.egeria_login_tui import login
from pyegeria.commands.cat.get_asset_graph import asset_viewer
from pyegeria.commands.cat.get_collection import collection_viewer
from pyegeria.commands.cat.get_project_dependencies import project_dependency_viewer
from pyegeria.commands.cat.get_project_structure import project_structure_viewer
from pyegeria.commands.cat.get_tech_type_elements import tech_viewer
from pyegeria.commands.cat.list_tech_type_elements import list_tech_elements
from pyegeria.commands.cli.egeria_ops import show_server
from pyegeria.commands.tech.get_tech_type_template import template_viewer
from pyegeria.commands.cat.list_assets import display_assets
from pyegeria.commands.cat.list_cert_types import display_certifications
from pyegeria.commands.cat.list_terms import display_glossary_terms
from pyegeria.commands.cat.list_projects import display_project_list
from pyegeria.commands.tech.list_anchored_elements import display_anchored_elements
from pyegeria.commands.tech.list_relationships import list_relationships
from pyegeria.commands.cat.list_tech_types import display_tech_types
from pyegeria.commands.cat.list_todos import display_to_dos as list_todos
from pyegeria.commands.cat.list_user_ids import list_user_ids
from pyegeria.commands.ops.list_archives import display_archive_list
from pyegeria.commands.cat.list_servers_deployed_imp import display_servers_by_dep_imp
from pyegeria.commands.cli.ops_config import Config
from pyegeria.commands.my.list_my_profile import display_my_profile
from pyegeria.commands.my.list_my_roles import display_my_roles
from pyegeria.commands.my.monitor_my_todos import display_my_todos
from pyegeria.commands.my.monitor_open_todos import display_todos
from pyegeria.commands.cat.list_deployed_database_schemas import (
    list_deployed_database_schemas,
)
from pyegeria.commands.cat.list_collections import display_collections
from pyegeria.commands.cat.list_deployed_catalogs import list_deployed_catalogs
from pyegeria.commands.cat.list_deployed_databases import list_deployed_databases
from pyegeria.commands.cat.glossary_actions import (
    create_glossary,
    delete_glossary,
    create_term,
    import_terms,
    delete_term,
    export_terms,
)
from pyegeria.commands.cat.list_glossaries import display_glossaries

from pyegeria.commands.my.todo_actions import (
    mark_todo_complete,
    change_todo_status,
    reassign_todo,
    delete_todo,
    create_todo,
)


from pyegeria.commands.ops.gov_server_actions import (
    add_catalog_target,
    remove_catalog_target,
    update_catalog_target,
    refresh_gov_eng_config,
    stop_server,
    start_server,
)
from pyegeria.commands.ops.list_catalog_targets import display_catalog_targets
from pyegeria.commands.ops.load_archive import load_archive
from pyegeria.commands.ops.monitor_engine_activity import display_engine_activity
from pyegeria.commands.ops.monitor_engine_activity_c import display_engine_activity_c
from pyegeria.commands.ops.monitor_gov_eng_status import display_gov_eng_status
from pyegeria.commands.ops.monitor_integ_daemon_status import (
    display_integration_daemon_status,
)
from pyegeria.commands.ops.monitor_platform_status import (
    display_status as p_display_status,
)
from pyegeria.commands.ops.monitor_server_status import (
    display_status as s_display_status,
)
from pyegeria.commands.ops.refresh_integration_daemon import refresh_connector
from pyegeria.commands.ops.restart_integration_daemon import restart_connector
from pyegeria.commands.ops.monitor_server_startup import display_startup_status

from pyegeria.commands.tech.get_element_info import display_elements
from pyegeria.commands.tech.get_guid_info import display_guid
from pyegeria.commands.tech.get_tech_details import tech_details_viewer
from pyegeria.commands.tech.list_asset_types import display_asset_types
from pyegeria.commands.tech.list_elements_for_classification import (
    list_classified_elements,
)
from pyegeria.commands.tech.list_all_om_type_elements import list_elements
from pyegeria.commands.tech.list_all_om_type_elements_x import list_elements_x
from pyegeria.commands.tech.list_elements_by_classification_by_property_value import find_elements_by_classification_by_prop_value
from pyegeria.commands.tech.list_elements_by_property_value import find_elements_by_prop_value
from pyegeria.commands.tech.list_elements_by_property_value_x import find_elements_by_prop_value_x
from pyegeria.commands.tech.list_related_elements_with_prop_value import list_related_elements_with_prop_value


from pyegeria.commands.tech.list_registered_services import display_registered_svcs
from pyegeria.commands.tech.list_related_specification import (
    display_related_specification,
)
from pyegeria.commands.tech.list_all_related_elements import list_related_elements

from pyegeria.commands.tech.list_relationship_types import display_relationship_types
from pyegeria.commands.tech.list_tech_templates import display_templates_spec
from pyegeria.commands.tech.list_valid_metadata_values import display_metadata_values
from pyegeria.commands.tech.list_gov_action_processes import display_gov_processes


@tui()
# @tui('menu', 'menu', 'A textual command line interface')
@click.version_option("0.5.2 ", prog_name="hey_egeria")
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
    default=os.environ.get("EGERIA_USER", "erinoverview"),
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
    type=bool,
    default=os.environ.get("EGERIA_JUPYTER", False),
    help="Enable for rendering in a Jupyter terminal",
)
@click.option(
    "--width",
    default=os.environ.get("EGERIA_WIDTH", 200),
    type=int,
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
    glossary_path,
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
        glossary_path,
    )
    ctx.max_content_width = 250
    ctx.ensure_object(Config)


#
#  my: Show
#
@cli.group("my")
@click.pass_context
def my(ctx):
    "Work with my information"
    pass


@my.group("show")
@click.pass_context
def my_show(ctx):
    """Display an Egeria Object"""
    pass


@my_show.command("my-profile")
@click.pass_context
def show_my_profile(ctx):
    """Display my profiles

    Usage: show my-profile

    """
    c = ctx.obj
    display_my_profile(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


@my_show.command("my-roles")
@click.pass_context
def show_my_roles(ctx):
    """Display my roles"""
    c = ctx.obj
    display_my_roles(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


@my_show.command("my-to-dos")
@click.pass_context
def show_my_todos(ctx):
    """Show my To-Dos

    Usage: show my-to-dos

    """
    c = ctx.obj
    display_my_todos(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


@my_show.command("open-to-dos")
@click.pass_context
def show_open_todos(ctx):
    """Display Open Todo items"""
    c = ctx.obj
    display_todos(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


#
#  my: Tell
#


@my.group("tell")
@click.pass_context
def my_tell(ctx):
    """Perform actions an Egeria Objects"""
    pass


my_tell.add_command(create_todo)
my_tell.add_command(delete_todo)
my_tell.add_command(change_todo_status)
my_tell.add_command(mark_todo_complete)
my_tell.add_command(reassign_todo)


#
#  tech User: Show
#
@cli.group("tech")
@click.pass_context
def tech(ctx):
    """Commands for tech Users"""
    pass


@tech.group("show")
@click.pass_context
def show_tech(ctx):
    """Display an Egeria Object"""
    pass


@show_tech.group("tech-info")
@click.pass_context
def show_tech_info(ctx):
    """Show various Egeria information"""
    pass


@show_tech.group("tech-types")
@click.pass_context
def show_tech_type(ctx):
    """Show information about Egeria technology types"""
    pass


@show_tech.group("elements")
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


@show_tech_type.command("list")
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


@show_tech_type.command("details")
@click.argument("tech-name")
@click.pass_context
def show_tech_details(ctx, tech_name):
    """Show technology type details"""
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


@show_tech_type.command("templates")
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


@show_tech_info.command("asset-types")
@click.pass_context
def show_asset_types(ctx):
    """Display asset types"""
    c = ctx.obj
    display_asset_types(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


@show_tech_info.command("registered-services")
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


@show_tech_info.command("relationship-types")
@click.option(
    "--om-type",
    default="Referenceable",
    help="Relationship type to get information about",
)
@click.pass_context
def show_relationship_types(ctx, om_type):
    """Show information about the specified relationship types"""
    c = ctx.obj
    display_relationship_types(
        om_type,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        False,
        c.jupyter,
        c.width,
    )





@show_tech_type.command("template-spec")
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


@show_tech_info.command("gov-action-processes")
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


@show_tech_info.command("relationships")
@click.option(
    "--relationship",
    default="Certification",
    help="Relationship type name to search for.",
)
@click.pass_context
def show_relationships(ctx, relationship):
    """Show the structure of the project starting from a root project"""
    c = ctx.obj
    list_relationships(
        relationship,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.timeout,
        c.jupyter,
        c.width,
    )


@show_tech_info.command("valid-metadata-values")
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


@show_tech_info.command("processes")
@click.pass_context
def list_element_info(ctx):
    """Display the governance action processes"""
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
    """Display a table of elements of an Open Metadata Type"""
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


#
#   Catalog User: Show
#


@cli.group("cat")
@click.pass_context
def cat(ctx):
    """Commands for all users"""
    pass


@cat.group("show")
@click.pass_context
def show_cat(ctx):
    """Display an Egeria Object"""
    pass


@show_cat.group("info")
@click.pass_context
def show_cat_info(ctx):
    """Group of commands to show information about various Egeria objects"""
    pass


@show_cat_info.command("tech-types")
@click.option("--tech_type", default="*", help="Tech type to search for")
@click.pass_context
def show_tech_types(ctx, tech_type):
    """List deployed technology types"""
    c = ctx.obj
    display_tech_types(
        tech_type, c.view_server, c.view_server_url, c.userid, c.password
    )


@show_cat_info.command("collections")
@click.option("--collection", default="*", help="Collection to search for")
@click.pass_context
def show_collections(ctx, collection):
    """List Collections"""
    c = ctx.obj
    display_collections(
        collection, c.view_server, c.view_server_url, c.userid, c.password
    )


@show_cat.group("assets")
@click.pass_context
def asset_group(ctx):
    """Show assets known to Egerias"""
    pass


@asset_group.command("elements-of-tech-type")
@click.option(
    "--tech_type",
    default="PostgreSQL Server",
    help="Specific tech type to get elements for",
)
@click.pass_context
def show_tech_type_elements(ctx, tech_type):
    """List technology type elements"""
    c = ctx.obj
    tech_viewer(tech_type, c.view_server, c.view_server_url, c.userid, c.password)


@asset_group.command("in-asset-domain")
@click.argument("search-string")
@click.pass_context
def show_assets(ctx, search_string):
    """Find and display assets in domain

    Usage: show assets <search-string>

           search-string must be greater than four characters.
    """
    c = ctx.obj
    display_assets(
        search_string,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        60,
        c.jupyter,
        c.width,
    )


@asset_group.command("asset-graph")
@click.argument("asset_guid", nargs=1)
@click.pass_context
def show_asset_graph(ctx, asset_guid):
    """Display a tree graph of information about an asset

    Usage: show asset-graph <asset-guid>

           asset-guid must be a valid asset guid. These can be found through other commands such as 'show tech-type-elements'

    """
    c = ctx.obj
    asset_viewer(
        asset_guid,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_cat.group("glossary")
@click.pass_context
def glossary_group(ctx):
    """Show glossary information"""
    pass


@glossary_group.command("glossary-terms")
@click.option(
    "--search-string",
    default="*",
    help="List glossary terms similar to search string - minimum of 4 characters",
)
@click.option(
    "--glossary-guid",
    default=os.environ.get("EGERIA_HOME_GLOSSARY_GUID", None),
    help="Optionally restrict search to glossary with the specified guid",
)
@click.option(
    "--glossary-name",
    default="*",
    help="Optionally restrict search to a specific named glossary",
)
@click.pass_context
def show_terms(ctx, search_string, glossary_guid, glossary_name):
    """Find and display glossary terms"""
    c = ctx.obj
    display_glossary_terms(
        search_string,
        glossary_guid,
        glossary_name,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@glossary_group.command("glossaries")
@click.option("--search_string", default="*", help="Name to search for glossaries")
@click.pass_context
def glossaries(ctx, search_string):
    """Display a list of glossaries"""
    c = ctx.obj
    display_glossaries(
        search_string,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_cat_info.command("collection-graph")
@click.option(
    "--root_collection",
    default="Coco Pharmaceuticals Governance Domains",
    help="View of tree of collections from a given root",
)
@click.pass_context
def show_collection(ctx, root_collection):
    """Display collection graph"""
    c = ctx.obj
    collection_viewer(
        root_collection,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_cat.group("projects")
@click.pass_context
def show_project_group(ctx):
    """Show project information in Egeria"""
    pass


@show_project_group.command("projects")
@click.option("--search-string", default="*", help="List Projects by Search String")
@click.pass_context
def show_projects(ctx, search_string):
    """Display a list of Egeria projects"""
    c = ctx.obj
    display_project_list(
        search_string,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        False,
        c.jupyter,
        c.width,
    )


@show_cat_info.command("certification-types")
@click.option("--search-string", default="CertificationType", help="")
@click.pass_context
def show_certification_types(ctx, search_string):
    """Show certification types"""
    c = ctx.obj
    display_certifications(
        search_string,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.timeout,
        c.jupyter,
        c.width,
    )


@show_cat_info.command("asset-types")
@click.pass_context
def show_asset_types(ctx):
    """Display known asset types"""
    c = ctx.obj
    display_asset_types(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


@show_project_group.command("project-structure")
@click.option(
    "--project",
    default="Clinical Trials Management",
    help="Enter the root project to start from",
)
@click.pass_context
def show_project_structure(ctx, project):
    """Show the organization structure of the project starting from a root project"""
    c = ctx.obj
    project_structure_viewer(
        project,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
        c.timeout,
    )


@show_project_group.command("project-dependencies")
@click.option(
    "--project",
    default="Clinical Trials Management",
    help="Enter the root project to start from",
)
@click.pass_context
def show_project_dependencies(ctx, project):
    """Show the dependencies of a project starting from a root project"""
    c = ctx.obj
    project_dependency_viewer(
        project,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
        c.timeout,
    )


@show_cat_info.command("to-dos")
@click.option("--search-string", default="*", help="View the list of To-Do items")
@click.option(
    "--status",
    type=click.Choice(
        ["OPEN", "IN_PROGRESS", "WAITING", "COMPLETE", "ABANDONED", "None"],
        case_sensitive=False,
    ),
    help="Enter an optional status filter",
    required=False,
    default="NONE",
)
@click.pass_context
def show_todos(ctx, search_string, status):
    """Display list of To Dost"""
    c = ctx.obj
    list_todos(
        search_string,
        status,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_cat_info.command("user-ids")
@click.pass_context
def show_todos(ctx):
    """Display a list of known user-ids"""
    c = ctx.obj
    list_user_ids(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


@show_cat.group("deployed-data")
@click.pass_context
def deployed_data(ctx):
    """Show deployed data resources known to Egeria"""
    pass


@deployed_data.command("deployed-servers")
@click.option(
    "--search-string",
    default="*",
    help="Filter deployed for deployed implementation type by search string",
)
@click.pass_context
def show_deployed_servers(ctx, search_string):
    """Display deployed servers"""
    c = ctx.obj
    display_servers_by_dep_imp(
        search_string,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@deployed_data.command("deployed-schemas")
@click.option("--catalog", default="*", help="What database or catalog to search")
@click.pass_context
def deployed_schemas(ctx, catalog):
    """Display deployed schemas"""
    c = ctx.obj
    list_deployed_database_schemas(
        catalog,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@deployed_data.command("catalogs")
@click.option("--search_server", default="*", help="Server to search for catalogs")
@click.pass_context
def list_catalogs(ctx, search_server):
    """Display deployed catalogs"""
    c = ctx.obj
    list_deployed_catalogs(
        search_server,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@deployed_data.command("databases")
@click.pass_context
def list_databases(ctx):
    """Display deployed databases"""
    c = ctx.obj
    list_deployed_databases(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


#
#  Tell-cat
#


@cat.group("tell")
@click.pass_context
def tell_cat(ctx):
    """Perform actions an Egeria Objects"""
    pass


@tell_cat.group("glossary")
@click.pass_context
def tell_glossary(ctx):
    """Perform glossary actions"""
    pass


tell_glossary.add_command(create_glossary)
tell_glossary.add_command(delete_glossary)
tell_glossary.add_command(delete_term)
tell_glossary.add_command(create_term)
tell_glossary.add_command(import_terms)
tell_glossary.add_command(export_terms)


@tell_cat.group("todo")
@click.pass_context
def tell_cat_todo(ctx):
    """Perform todo actions"""
    pass


tell_cat_todo.add_command(mark_todo_complete)
tell_cat_todo.add_command(reassign_todo)
tell_cat_todo.add_command(delete_todo)
tell_cat_todo.add_command(create_todo)


@show_cat_info.command("tech-types")
@click.option("--tech_type", default="*", help="Tech type to search for")
@click.pass_context
def show_tech_types(ctx, tech_type):
    """List deployed technology types"""
    c = ctx.obj
    display_tech_types(
        tech_type, c.view_server, c.view_server_url, c.userid, c.password
    )


@show_cat_info.command("certification-types")
@click.option("--search-string", default="CertificationType", help="")
@click.pass_context
def show_certification_types(ctx, search_string):
    """Show certification types"""
    c = ctx.obj
    display_certifications(
        search_string,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.timeout,
        c.jupyter,
        c.width,
    )


@show_project_group.command("project-structure")
@click.option(
    "--project",
    default="Clinical Trials Management",
    help="Enter the root project to start from",
)
@click.pass_context
def show_project_structure(ctx, project):
    """Show the organization structure of the project starting from a root project"""
    c = ctx.obj
    project_structure_viewer(
        project,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
        c.timeout,
    )


@show_project_group.command("project-dependencies")
@click.option(
    "--project",
    default="Clinical Trials Management",
    help="Enter the root project to start from",
)
@click.pass_context
def show_project_dependencies(ctx, project):
    """Show the dependencies of a project starting from a root project"""
    c = ctx.obj
    project_dependency_viewer(
        project,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
        c.timeout,
    )


@glossary_group.command("glossary-terms")
@click.option(
    "--search-string",
    default="*",
    help="List glossary terms similar to search string - minimum of 4 characters",
)
@click.option(
    "--glossary-guid",
    default=None,
    help="Optionally restrict search to glossary with the specified guid",
)
@click.option(
    "--glossary-name",
    default="*",
    help="Optionally restrict search to a specific named glossary",
)
@click.pass_context
def show_terms(ctx, search_string, glossary_guid, glossary_name):
    """Find and display glossary terms"""
    c = ctx.obj
    display_glossary_terms(
        search_string,
        glossary_guid,
        glossary_name,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@asset_group.command("asset-graph")
@click.argument("asset_guid", nargs=1)
@click.pass_context
def show_asset_graph(ctx, asset_guid):
    """Display a tree graph of information about an asset

    Usage: show asset-graph <asset-guid>

           asset-guid must be a valid asset guid. These can be found through other commands such as 'show tech-type-elements'

    """
    c = ctx.obj
    asset_viewer(
        asset_guid,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@asset_group.command("tech-type-elements")
@click.option(
    "--tech_type",
    default="PostgreSQL Server",
    help="Specific tech type to get elements for",
)
@click.pass_context
def list_tech_type_elements(ctx, tech_type):
    """List technology type elements"""
    c = ctx.obj
    list_tech_elements(
        tech_type, c.view_server, c.view_server_url, c.userid, c.password
    )


@show_project_group.command("projects")
@click.option("--search-string", default="*", help="List Projects by Search String")
@click.pass_context
def show_projects(ctx, search_string):
    """Display a list of Egeria projects"""
    c = ctx.obj
    display_project_list(
        search_string,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        False,
        c.jupyter,
        c.width,
    )


@show_cat_info.command("to-dos")
@click.option("--search-string", default="*", help="View the list of To-Do items")
@click.option(
    "--status",
    type=click.Choice(
        ["OPEN", "IN_PROGRESS", "WAITING", "COMPLETE", "ABANDONED", "None"],
        case_sensitive=False,
    ),
    help="Enter an optional status filter, default='OPEN'",
    required=False,
    default="OPEN",
)
@click.pass_context
def show_todos(ctx, search_string, status):
    """Display a list of To Dos"""
    c = ctx.obj
    list_todos(
        search_string,
        status,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_cat_info.command("user-ids")
@click.pass_context
def show_user_ids(ctx):
    """Display table of known user ids"""
    c = ctx.obj
    list_user_ids(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )



@deployed_data.command("deployed-servers")
@click.option(
    "--search-string",
    default="*",
    help="Filter deployed for deployed implementation type by search string",
)
@click.pass_context
def show_deployed_servers(ctx, search_string):
    """Show list of deployed servers"""
    c = ctx.obj
    display_servers_by_dep_imp(
        search_string,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@deployed_data.command("deployed-schemas")
@click.option(
    "--search_catalog", default="*", help="What database or catalog to search"
)
@click.pass_context
def deployed_schemas(ctx, search_catalog):
    """Display a list of deployed schemas"""
    c = ctx.obj
    list_deployed_database_schemas(
        search_catalog,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@deployed_data.command("catalogs")
@click.option("--search_server", default="*", help="Server to search for catalogs")
@click.pass_context
def catalogs(ctx, search_server):
    """Display a list of deployed catalogs"""
    c = ctx.obj
    list_deployed_catalogs(
        search_server,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@deployed_data.command("databases")
@click.pass_context
def databases(ctx):
    """Display a list of deployed databases"""
    c = ctx.obj
    list_deployed_databases(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


@glossary_group.command("glossaries")
@click.option("--search_string", default="*", help="Name to search for glossaries")
@click.pass_context
def glossaries(ctx, search_string):
    """Display a list of glossaries"""
    c = ctx.obj
    display_glossaries(
        search_string,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


# @tell_cat.group("survey")
# @click.pass_context
# def survey(ctx):
#     """Refresh the specified integration connector or ALL connectors if not specified"""
#     c = ctx.obj
#     pass
#
#
# @survey.command("survey-uc-server")
# @click.pass_context
# @click.option(
#     "--uc_endpoint",
#     default="https://localhost:8080",
#     help="Endpoint of the Unity Catalog Server to Survey",
# )
# def survey_uc_server(ctx, uc_endpoint):
#     """Survey the Unity Catalog server at the given endpoint"""
#     c = ctx.obj
#     pass
# restart_connector(connector, c.integration_daemon, c.integration_daemon_url,
#                   c.userid, c.password)


#
#  Operations: Show
#


@cli.group("ops")
@click.pass_context
def ops(ctx):
    """Commands to understand and manage operations"""
    pass


@ops.group("show")
@click.pass_context
def show_ops(ctx):
    """Display an Egeria Object"""
    pass

@show_ops.group("repository")
@click.pass_context
def show_repo(ctx):
    """Group of commands to show repository information"""
    pass


@show_repo.command("archives")
@click.pass_context
def show_archives(ctx):
    c= ctx.obj
    display_archive_list(
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        False,
        c.jupyter,
        c.width,
    )

@show_ops.group("platforms")
@click.pass_context
def show_platform(ctx):
    """Group of commands to show information about Egeria platforms"""
    pass


@show_platform.command("status")
@click.pass_context
def show_platform_status(ctx):
    """Display a live status view of known platforms"""
    c = ctx.obj
    p_display_status(
        c.view_server, c.view_server_url, c.admin_user, c.admin_user_password
    )


@show_ops.group("servers")
@click.pass_context
def show_server(ctx):
    """Group of commands to show information about Egeria servers"""
    pass


@show_server.command("status")
@click.option(
    "--full",
    is_flag=True,
    default=False,
    help="If set, full server descriptions will be shown",
)
@click.pass_context
def show_server_status(ctx, full):
    """Display a live status view of Egeria servers for the specified Egeria platform"""
    c = ctx.obj
    s_display_status(
        full,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_server.command("startup")
@click.pass_context
def show_startup_status(ctx):
    """Display a live status view of Egeria servers for the specified Egeria platform"""
    c = ctx.obj
    display_startup_status(
        c.server,
        c.url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show_ops.group("engines")
@click.pass_context
def engine_host(ctx):
    """Group of commands to show information about Egeria engines"""
    pass


@engine_host.command("status")
@click.option(
    "--engine-list",
    default="*",
    help="Enter the list of connectors you are interested in or ['*'] for all",
)
@click.option(
    "--list", is_flag=True, default=False, help="If True, a paged list will be shown"
)

@click.pass_context
def gov_eng_status(ctx, engine_list, list):
    """Display engine-host status information"""
    c = ctx.obj
    display_gov_eng_status(
        [engine_list],
        engine_host=c.engine_host,
        view_server=c.view_server,
        url=c.view_server_url,
        username=c.userid,
        user_pass=c.password,
        paging=list,
        jupyter=c.jupyter,
        width=c.width,
    )


@engine_host.command("activity")
@click.option(
    "--rowlimit",
    default=0,
    type=int,
    show_default=True,
    help="If non-zero, limit the number of rows returned",
)
@click.option(
    "--list", is_flag=True, default=False, help="If True, a paged list will be shown"
)
@click.option(
    "--compressed",
    is_flag=True,
    default=False,
    show_default=True,
    help="Compressed combines some attributes into a single column",
)
@click.pass_context
def eng_activity_status(ctx, rowlimit: int, list: bool, compressed: bool):
    """Show Governance Activity in engine-host"""
    c = ctx.obj
    if compressed:
        display_engine_activity_c(
            rowlimit,
            c.view_server,
            c.view_server_url,
            c.admin_user,
            c.admin_user_password,
            list,
            c.jupyter,
            c.width,
        )
    else:
        display_engine_activity(
            rowlimit,
            c.view_server,
            c.view_server_url,
            c.admin_user,
            c.admin_user_password,
            list,
            c.jupyter,
            c.width,
        )


@show_ops.group("integrations")
@click.pass_context
def integrations(ctx):
    """Group of commands to show information about Egeria integrations"""
    pass


@integrations.command("status")
@click.option(
    "--connector-list",
    default="*",
    help="Enter the list of connectors you are interested in or ['*'] for all",
)
@click.option(
    "--list", is_flag=True, default=False, help="If True, a paged list will be shown"
)
@click.option(
    "--sorted", type=bool, default=True, help="If True, the table will be sorted"
)
@click.pass_context
def integrations_status(ctx, connector_list, list, sorted):
    """Display integration_daemon status information"""
    c = ctx.obj
    display_integration_daemon_status(
        [connector_list],
        c.integration_daemon,
        c.integration_daemon_url,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        list,
        c.jupyter,
        c.width,
        sorted,
    )


@integrations.command("targets")
@click.pass_context
@click.argument("--connector", nargs=1)
def integrations_status(ctx, connector):
    """Display Catalog Targets for a connector"""
    c = ctx.obj
    display_catalog_targets(
        connector,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


#
#  Operations: Tell
#


@ops.group("tell")
@click.pass_context
def tell_ops(ctx):
    """Perform actions an Egeria Objects"""
    pass


@tell_ops.group("integration-daemon")
@click.pass_context
def tell_integration_daemon(ctx):
    """Group of commands to an integration_daemon"""
    pass


@tell_integration_daemon.command("refresh")
@click.pass_context
@click.option(
    "--connector",
    default="all",
    help="Name of connector to refresh or 'all' to refresh all",
)
@click.option(
    "--server",
    default="integration-daemon",
    help="Name of the integration server to refresh",
)
def refresh_connectors(ctx, server, connector):
    """Refresh the specified integration connector or ALL connectors if not specified"""
    c = ctx.obj
    refresh_connector(
        connector, server, c.view_server_url, c.view_server, c.userid, c.password
    )


@tell_integration_daemon.command("restart")
@click.pass_context
@click.option(
    "--connector",
    default="all",
    help="Name of connector to restart or 'all' to restart all",
)
@click.option(
    "--server",
    default="integration-daemon",
    help="Name of the integration server to refresh",
)
def restart_connectors(ctx, server, connector):
    """Restart the specified integration connector or ALL connectors if not specified"""
    c = ctx.obj
    restart_connector(
        connector, server, c.view_server_url, c.view_server, c.userid, c.password
    )


tell_integration_daemon.add_command(add_catalog_target)
tell_integration_daemon.add_command(remove_catalog_target)
tell_integration_daemon.add_command(update_catalog_target)
tell_integration_daemon.add_command(stop_server)
tell_integration_daemon.add_command(start_server)


@tell_ops.group("servers")
@click.pass_context
def servers(ctx):
    """Perform actions on OMAG Servers"""
    pass


servers.add_command(start_server)
servers.add_command(stop_server)


@tell_ops.group("engine-host")
@click.pass_context
def engine_host(ctx):
    """Group of commands to an engine-host"""
    pass


engine_host.add_command(start_server)
engine_host.add_command(stop_server)
engine_host.add_command(refresh_gov_eng_config)


@tell_ops.group("repository")
@click.pass_context
def repository(ctx):
    """Group of commands to a repository"""
    pass


repository.add_command(load_archive)

if __name__ == "__main__":
    while True:
        try:
            cli()
        except Exception as e:
            click.echo(f"Error: {e}")
