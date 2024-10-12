#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


A command line interface for Egeria Users - all commands

This is an emerging capability based on the **click** package. Feedback welcome!

"""
import click
from trogon import tui

from commands.cat.get_asset_graph import asset_viewer
from commands.cat.get_collection import collection_viewer
from commands.cat.get_project_dependencies import project_dependency_viewer
from commands.cat.get_project_structure import project_structure_viewer
from commands.cat.get_tech_type_elements import tech_viewer
from commands.cat.get_tech_type_template import template_viewer
from commands.cat.list_assets import display_assets
from commands.cat.list_cert_types import display_certifications
from commands.cat.list_glossary import display_glossary_terms
from commands.cat.list_projects import display_project_list
from commands.cat.list_relationships import list_relationships
from commands.cat.list_tech_types import display_tech_types
from commands.cat.list_todos import display_to_dos as list_todos
from commands.cat.list_user_ids import list_user_ids
from commands.cat.list_archives import display_archive_list
from commands.cli.ops_config import Config
from commands.my.list_my_profile import display_my_profile
from commands.my.list_my_roles import display_my_roles
from commands.my.monitor_my_todos import display_my_todos
from commands.my.monitor_open_todos import display_todos
from commands.cat.old_list_deployed_database_schemas import (
    list_deployed_database_schemas,
)
from commands.cat.list_deployed_catalogs import list_deployed_catalogs
from commands.cat.list_deployed_databases import list_deployed_databases
from commands.cat.glossary_actions import create_glossary, delete_glossary, create_term
from commands.my.todo_actions import (
    mark_todo_complete,
    reassign_todo,
    delete_todo,
    create_todo,
)


from commands.ops.gov_server_actions import (
    add_catalog_target,
    remove_catalog_target,
    update_catalog_target,
    refresh_gov_eng_config,
    stop_server,
    start_server,
)
from commands.ops.list_catalog_targets import display_catalog_targets
from commands.ops.load_archive import load_archive
from commands.ops.monitor_engine_activity import display_engine_activity
from commands.ops.monitor_engine_activity_c import display_engine_activity_c
from commands.ops.monitor_gov_eng_status import display_gov_eng_status
from commands.ops.monitor_integ_daemon_status import (
    display_integration_daemon_status,
)
from commands.ops.monitor_platform_status import (
    display_status as p_display_status,
)
from commands.ops.monitor_server_status import (
    display_status as s_display_status,
)
from commands.ops.refresh_integration_daemon import refresh_connector
from commands.ops.restart_integration_daemon import restart_connector
from commands.ops.monitor_server_startup import display_startup_status

from commands.tech.get_element_info import display_elements
from commands.tech.get_guid_info import display_guid
from commands.tech.get_tech_details import tech_details_viewer
from commands.tech.list_asset_types import display_asset_types
from commands.tech.list_elements import list_elements
from commands.tech.list_registered_services import display_registered_svcs
from commands.tech.list_related_specification import (
    display_related_specification,
)
from commands.tech.list_relationship_types import display_relationship_types
from commands.tech.list_tech_templates import display_templates_spec
from commands.tech.list_valid_metadata_values import display_metadata_values
from commands.tech.list_gov_action_processes import display_gov_processes


@tui()
# @tui('menu', 'menu', 'A textual command line interface')
@click.version_option("0.0.1", prog_name="egeria_ops")
@click.group()
@click.option(
    "--server",
    default="active-metadata-store",
    envvar="EGERIA_METADATA_STORE",
    help="Egeria metadata store to work with",
)
@click.option(
    "--url",
    default="https://localhost:9443",
    envvar="EGERIA_PLATFORM_URL",
    help="URL of Egeria metadata store platform to connect to",
)
@click.option(
    "--integration-daemon",
    default="integration-daemon",
    envvar="EGERIA_INTEGRATION_DAEMON",
    help="Egeria integration daemon to work with",
)
@click.option(
    "--integration_daemon_url",
    default="https://localhost:9443",
    envvar="EGERIA_INTEGRATION_DAEMON_URL",
    help="URL of Egeria integration daemon platform to connect to",
)
@click.option(
    "--view_server",
    default="view-server",
    envvar="EGERIA_VIEW_SERVER",
    help="Egeria view server to work with",
)
@click.option(
    "--view_server_url",
    default="https://localhost:9443",
    envvar="EGERIA_VIEW_SERVER_URL",
    help="URL of Egeria view server platform to connect to",
)
@click.option(
    "--engine_host",
    default="engine-host",
    envvar="EGERIA_ENGINE_HOST",
    help="Egeria engine host to work with",
)
@click.option(
    "--engine_host_url",
    default="https://localhost:9443",
    envvar="EGERIA_ENGINE_HOST_URL",
    help="URL of Egeria engine host platform to connect to",
)
@click.option(
    "--admin_user",
    default="garygeeke",
    envvar="EGERIA_ADMIN_USER",
    help="Egeria admin user",
)
@click.option(
    "--admin_user_password",
    default="secret",
    envvar="EGERIA_ADMIN_PASSWORD",
    help="Egeria admin password",
)
@click.option(
    "--userid", default="erinoverview", envvar="EGERIA_USER", help="Egeria user"
)
@click.option(
    "--password",
    default="secret",
    envvar="EGERIA_PASSWORD",
    help="Egeria user password",
)
@click.option("--timeout", default=60, help="Number of seconds to wait")
@click.option("--verbose", is_flag=True, default=False, help="Enable verbose mode")
@click.option(
    "--paging",
    is_flag=True,
    default=False,
    help="Enable paging snapshots vs live updates",
)
@click.option(
    "--jupyter",
    is_flag=True,
    default=False,
    envvar="EGERIA_JUPYTER",
    help="Enable for rendering in a Jupyter terminal",
)
@click.option(
    "--width",
    default=200,
    envvar="EGERIA_WIDTH",
    help="Screen width, in characters, to use",
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
    paging,
    verbose,
    jupyter,
    width,
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
        paging,
        verbose,
        jupyter,
        width,
    )
    ctx.max_content_width = 200
    ctx.ensure_object(Config)
    if verbose:
        click.echo(f"we are in verbose mode - server is {server}")


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
def show(ctx):
    """Display an Egeria Object"""
    pass


@show.command("my-profile")
@click.pass_context
def show_my_profile(ctx):
    """Display my profiles

    Usage: show my-profile

    """
    c = ctx.obj
    display_my_profile(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


@show.command("my-roles")
@click.pass_context
def show_my_roles(ctx):
    """Display my profiles

    Usage: show my-profile

    """
    c = ctx.obj
    display_my_roles(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


@show.command("my-to-dos")
@click.pass_context
def show_my_todos(ctx):
    """Show my To-Dos

    Usage: show my-to-dos

    """
    c = ctx.obj
    display_my_todos(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


@show.command("open-to-dos")
@click.pass_context
def show_open_todos(ctx):
    """Display a live status view of Egeria servers for the specified Egeria platform

    Usage: show tech-details <tech-name>

           tech-name is a valid technology name (see 'show tech-types')
    """
    c = ctx.obj
    display_todos(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


#
#  my: Tell
#


@my.group("tell")
@click.pass_context
def tell(ctx):
    """Perform actions an Egeria Objects"""
    pass


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
def show(ctx):
    """Display an Egeria Object"""
    pass


@show.command("get-elements")
@click.pass_context
@click.option("--om_type", default="Project", help="Metadata type to query")
def get_element_info(ctx, om_type):
    """Display the elements for an Open Metadata Type"""
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


@show.command("list-elements")
@click.pass_context
@click.option("--om_type", default="Project", help="Metadata type to query")
def list_element_info(ctx, om_type):
    """Display the elements for an Open Metadata Type"""
    c = ctx.obj
    list_elements(
        om_type,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show.command("list-processes")
@click.pass_context
def list_element_info(ctx):
    """Display the valid metadata values for a property and type"""
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


@show.command("guid-info")
@click.argument("guid", nargs=1)
@click.pass_context
def show_guid_infos(ctx, guid):
    """Display a live status view of known platforms

    Usage: show guid-info <a guid>

    """
    c = ctx.obj
    display_guid(guid, c.server, c.url, c.userid, c.password, c.jupyter, c.width)


@show.command("tech-types")
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


@show.command("tech-details")
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


@show.command("asset-types")
@click.pass_context
def show_asset_types(ctx):
    """Display engine-host status information"""
    c = ctx.obj
    display_asset_types(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


@show.command("registered-services")
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


@show.command("related-specifications")
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


@show.command("relationship-types")
@click.option(
    "--rel-type",
    default="AssetOwner",
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


@show.command("tech-templates")
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


@show.command("tech-template-spec")
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


@show.command("gov-action-processes")
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


@show.command("valid-metadata-values")
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


#
#  tech Users: Tell
#


@tech.group("tell")
@click.pass_context
def tell(ctx):
    """Perform actions an Egeria Objects"""
    pass


#
#   Catalog User: Show
#


@cli.group("cat")
@click.pass_context
def cat(ctx):
    """Commands for the more tech user"""
    pass


@cat.group("show")
@click.pass_context
def show(ctx):
    """Display an Egeria Object"""
    pass


@show.command("tech-types")
@click.option("--tech_type", default="*", help="Tech type to search for")
@click.pass_context
def show_tech_types(ctx, tech_type):
    """List deployed technology types"""
    c = ctx.obj
    display_tech_types(
        tech_type, c.view_server, c.view_server_url, c.userid, c.password
    )


@show.command("tech-type-elements")
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


@show.command("tech-type-templates")
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


@show.command("certification-types")
@click.option("--search-string", default="CertificationType", help="")
@click.pass_context
def show_certification_types(ctx, search_string):
    """Show certification types
    - generally stay with the default..
    """
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


@show.command("project-structure")
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


@show.command("project-dependencies")
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


@show.command("relationships")
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


@show.command("assets")
@click.argument("search-string")
@click.pass_context
def show_assets(ctx, search_string):
    """Find and display assets

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


@show.command("glossary-terms")
@click.option(
    "--search-string",
    default="*",
    help="List glossary terms similar to search string - minimum of 4 characters",
)
@click.option(
    "--glossary_guid",
    default=None,
    help="Optionally restrict search to glossary with the specified guid",
)
@click.pass_context
def show_terms(ctx, search_string, glossary_guid):
    """Find and display glossary terms"""
    c = ctx.obj
    display_glossary_terms(
        search_string,
        glossary_guid,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
    )


@show.command("asset-graph")
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


@show.command("collection")
@click.option(
    "--root_collection",
    default="Root Sustainability Collection",
    help="View of tree of collections from a given root",
)
@click.pass_context
def show_asset_graph(ctx, root_collection):
    """Display a tree graph of information about an asset"""
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


@show.command("projects")
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


@show.command("to-dos")
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
    """Display a tree graph of information about an asset"""
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


@show.command("user-ids")
@click.pass_context
def show_todos(ctx):
    """Display a tree graph of information about an asset"""
    c = ctx.obj
    list_user_ids(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


@show.command("list-archives")
@click.pass_context
def list_archives(ctx):
    """Display a tree graph of information about an asset"""
    c = ctx.obj
    display_archive_list(
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        False,
        c.jupyter,
        c.width,
    )


@show.command("list-deployed-schemas")
@click.option(
    "--search_catalog", default="*", help="What database or catalog to search"
)
@click.pass_context
def list_deployed_schemas(search_catalog, ctx):
    """Display a tree graph of information about an asset"""
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


@show.command("list-catalogs")
@click.option("--search_server", default="*", help="Server to search for catalogs")
@click.pass_context
def list_catalogs(search_server, ctx):
    """Display a tree graph of information about an asset"""
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


@show.command("list-databases")
@click.pass_context
def list_databases(ctx):
    """Display a tree graph of information about an asset"""
    c = ctx.obj
    list_deployed_databases(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


#
#  Catalog User: Tell
#


@cat.group("tell")
@click.pass_context
def tell(ctx):
    """Perform actions an Egeria Objects"""
    pass


tell.add_command(create_glossary)
tell.add_command(delete_glossary)
tell.add_command(create_term)
tell.add_command(mark_todo_complete)
tell.add_command(reassign_todo)
tell.add_command(delete_todo)
tell.add_command(create_todo)


@tell.group("survey")
@click.pass_context
def survey(ctx):
    """Refresh the specified integration connector or ALL connectors if not specified"""
    c = ctx.obj
    pass


@survey.command("survey-uc-server")
@click.pass_context
@click.option(
    "--uc_endpoint",
    default="https://localhost:8080",
    help="Endpoint of the Unity Catalog Server to Survey",
)
def survey_uc_server(ctx, uc_endpoint):
    """Survey the Unity Catalog server at the given endpoint"""
    c = ctx.obj
    pass
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
def show(ctx):
    """Display an Egeria Object"""
    pass


@show.group("platforms")
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


@show.group("servers")
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


@show.group("engines")
@click.pass_context
def engine_host(ctx):
    """Group of commands to show information about Egeria engines"""
    pass


@engine_host.command("status")
@click.option(
    "--list", is_flag=True, default=False, help="If True, a paged list will be shown"
)
@click.option(
    "--engine-host",
    default="engine-host",
    help="Name of the Engine Host to get status for",
)
@click.pass_context
def gov_eng_status(ctx, engine_host, list):
    """Display engine-host status information"""
    c = ctx.obj
    display_gov_eng_status(
        engine_host,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        list,
        c.jupyter,
        c.width,
    )


@engine_host.command("activity")
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
def eng_activity_status(ctx, list, compressed):
    """Show Governance Activity in engine-host"""
    c = ctx.obj
    if compressed:
        display_engine_activity_c(
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
            c.view_server,
            c.view_server_url,
            c.admin_user,
            c.admin_user_password,
            list,
            c.jupyter,
            c.width,
        )


@show.group("integrations")
@click.pass_context
def integrations(ctx):
    """Group of commands to show information about Egeria integrations"""
    pass


@integrations.command("status")
@click.option(
    "--list", is_flag=True, default=False, help="If True, a paged list will be shown"
)
@click.option(
    "--sorted", type=bool, default=True, help="If True, the table will be sorted"
)
@click.pass_context
def integrations_status(ctx, list, sorted):
    """Display integration-daemon status information"""
    c = ctx.obj
    display_integration_daemon_status(
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
@click.argument("connector", nargs=1)
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
def tell(ctx):
    """Perform actions an Egeria Objects"""
    pass


@tell.group("integration-daemon")
@click.pass_context
def integration_daemon(ctx):
    """Group of commands to an integration-daemon"""
    pass


@integration_daemon.command("refresh")
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


@integration_daemon.command("restart")
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


integration_daemon.add_command(add_catalog_target)
integration_daemon.add_command(remove_catalog_target)
integration_daemon.add_command(update_catalog_target)
integration_daemon.add_command(stop_server)
integration_daemon.add_command(start_server)


@tell.group("engine-host")
@click.pass_context
def engine_host(ctx):
    """Group of commands to an engine-host"""
    pass


engine_host.add_command(start_server)
engine_host.add_command(stop_server)
engine_host.add_command(refresh_gov_eng_config)


@tell.group("repository")
@click.pass_context
def repository(ctx):
    """Group of commands to a repository"""
    pass


repository.add_command(load_archive)

if __name__ == "__main__":
    cli()
