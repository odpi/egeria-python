#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


A object_action line interface for Egeria Catalog User functions

This is an emerging capability based on the **click** package. Feedback welcome!

"""
import os

import click
from trogon import tui
from pyegeria import config_logging, get_app_config

from commands.cat.list_format_set import execute_format_set_action
from commands.cat.dr_egeria_md import process_markdown_file
from commands.cat.get_asset_graph import asset_viewer
from commands.cat.get_collection import collection_viewer
from commands.cat.get_project_dependencies import project_dependency_viewer
from commands.cat.get_project_structure import project_structure_viewer
from commands.cat.get_tech_type_elements import tech_viewer
from commands.cat.glossary_actions import (
    create_glossary,
    create_term,
    delete_glossary,
    delete_term,
    export_terms_csv,
    import_terms_csv,
    create_category,
    update_category,
    delete_category,
    add_term_to_category,
    remove_term_from_category)
from commands.cat.list_assets import display_assets
from commands.cat.list_categories import display_categories
from commands.cat.list_cert_types import display_certifications
from commands.cat.list_collections import display_collections
from commands.cat.list_deployed_catalogs import list_deployed_catalogs
from commands.cat.list_deployed_database_schemas import (
    list_deployed_database_schemas,
    )
from commands.cat.list_deployed_databases import list_deployed_databases
from commands.cat.list_deployed_servers import display_servers_by_dep_imp
from commands.cat.list_glossaries import display_glossaries
from commands.cat.list_projects import display_project_list
from commands.cat.list_tech_type_elements import list_tech_elements
from commands.cat.list_tech_types import display_tech_types
from commands.cat.list_terms import display_glossary_terms
from commands.cat.list_todos import display_to_dos as list_todos
from commands.cat.list_user_ids import list_user_ids
from commands.cli.ops_config import Config
from commands.my.todo_actions import (
    create_todo,
    delete_todo,
    mark_todo_complete,
    reassign_todo,
    )
from commands.tech.list_asset_types import display_asset_types

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
app_settings = get_app_config()
app_config = app_settings["Environment"]
# config_logging()


# @tui
# @tui('menu','menu','A textual object_action line interface')
@tui()
# @tui('menu', 'menu', 'A textual object_action line interface')
@click.version_option("5.4 ", prog_name="hey_egeria")
@click.group()
@click.option(
    "--server",
    default=app_config['Egeria Metadata Store'],
    help="Egeria metadata store to work with",
)
@click.option(
    "--url",
    default=app_config.egeria_platform_url,
    help="URL of Egeria metadata store platform to connect to",
)
@click.option(
    "--integration_daemon",
    default=app_config.egeria_integration_daemon,
    help="Egeria integration daemon to work with",
)
@click.option(
    "--integration_daemon_url",
    default=app_config.egeria_integration_daemon_url,
    help="URL of Egeria integration daemon platform to connect to",
)
@click.option(
    "--view_server",
    default=app_config.egeria_view_server,
    help="Egeria view server to work with",
)
@click.option(
    "--view_server_url",
    default=app_config.egeria_view_server_url,
    help="URL of Egeria view server platform to connect to",
)
@click.option(
    "--engine_host",
    default=app_config.egeria_engine_host,
    help="Egeria engine host to work with",
)
@click.option(
    "--engine_host_url",
    default=app_config.egeria_engine_host_url,
    help="URL of Egeria engine host platform to connect to",
)

@click.option(
    "--userid",
    default=EGERIA_USER,
    help="Egeria user",
)
@click.option(
    "--password",
    default=EGERIA_USER_PASSWORD,
    help="Egeria user password",
)
@click.option("--timeout", default=60, help="Number of seconds to wait")
@click.option(
    "--jupyter",
    is_flag=True,
    type=bool,
    default=app_config.egeria_jupyter,
    help="Enable for rendering in a Jupyter terminal",
)
@click.option(
    "--width",
    default=app_config.console__width,
    type=int,
    help="Screen width, in characters, to use",
)
@click.option(
    "--home_glossary_guid",
    default=app_settings.User_Profile.home_glossary_guid,
    help="Glossary name to use as the home glossary",
)
@click.option(
    "--glossary_path",
    default=app_config.egeria_platform_glossary_path,
    help="Path to glossary import/export files",
)

@click.option(
    "--root_path",
    default=app_config.pyegeria_root,
    help="Root path to use for file operations",
)

@click.option(
    "--inbox_path",
    default=app_config.dr_egeria_inbox,
    help="Path to inbox files",
)
@click.option(
    "--outbox_path",
    default=app_config.dr_egeria_outbox,
    help="Path to outbox files",
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
    userid,
    password,
    timeout,
    jupyter,
    width,
    home_glossary_guid,
    glossary_path,
    root_path,
    inbox_path,
    outbox_path,
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
        userid,
        password,
        timeout,
        jupyter,
        width,
        home_glossary_guid,
        glossary_path,
        root_path,
        inbox_path,
        outbox_path
    )
    ctx.max_content_width = 250
    ctx.ensure_object(Config)


@cli.group("show")
def show():
    """Display Egeria Objects"""
    pass


@show.group("info")
@click.pass_context
def info(ctx):
    """Group of md_commands to show information about various Egeria objects"""
    pass


@info.command("list-output-set")
@click.option("--format-set", help="Format set to output")
@click.option("--output-format", default = "TABLE", help="Output format type")
@click.option('--search-string', default="*", help="Search string")
@click.pass_context
def show_format_set(ctx, format_set, output_format, search_string):
    """Dynamically generate output based on a format set"""
    c = ctx.obj

    execute_format_set_action(
        format_set, c.view_server, c.view_server_url,
        c.userid, c.password, output_format, search_string = search_string
    )



@info.command("tech-types")
@click.option("--tech_type", default="*", help="Tech type to search for")
@click.pass_context
def show_tech_types(ctx, tech_type):
    """List deployed technology types"""
    c = ctx.obj
    display_tech_types(
        tech_type, c.view_server, c.view_server_url, c.userid, c.password
    )


@info.command("collections")
@click.option("--collection", default="*", help="Collection to search for")
@click.pass_context
def show_collections(ctx, collection):
    """List Collections"""
    c = ctx.obj
    display_collections(
        collection, c.view_server, c.view_server_url, c.userid, c.password
    )


@show.group("assets")
@click.pass_context
def asset_group(ctx):
    """Show assets known to Egerias"""
    pass


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


@asset_group.command("asset-graph")
@click.argument("asset_guid", nargs=1)
@click.pass_context
def show_asset_graph(ctx, asset_guid):
    """Display a tree graph of information about an asset

    Usage: show asset-graph <asset-guid>

           asset-guid must be a valid asset guid. These can be found through other md_commands such as 'show tech-type-elements'

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


@show.group("glossary")
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
@click.option(
    "--output-format",
    type=click.Choice(["FORM", "REPORT", "TABLE"]),
    default="TABLE",
    help="Display on screen as table, or as FORM or REPORT file",
    )
@click.pass_context
def show_terms(ctx, search_string, glossary_guid, glossary_name, output_format):
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
        output_format,
    )

@glossary_group.command("glossaries")
@click.option("--search_string", default="*", help="Name to search for glossaries")
@click.option(
    "--output-format",
    type=click.Choice(["FORM", "REPORT", "TABLE"]),
    default="TABLE",
    help="Display on screen as table, or as FORM or REPORT file",
    )
@click.pass_context
def glossaries(ctx, search_string, output_format):
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
        output_format,
    )
@glossary_group.command("glossary-categories")
@click.option("--search_string", default="*", help="Name to search for categories")
@click.option(
    "--output-format",
    type=click.Choice(["FORM", "REPORT", "TABLE"]),
    default="TABLE",
    help="Display on screen as table, or as FORM or REPORT file",
    )
@click.pass_context
def categories(ctx, search_string, output_format):
    """Display a list of categories"""
    c = ctx.obj
    display_categories(
        search_string,
        c.view_server,
        c.view_server_url,
        c.userid,
        c.password,
        c.jupyter,
        c.width,
        output_format,
    )




@info.command("collection")
@click.option(
    "--root_collection",
    default="Digital Product Root",
    help="View of tree of collections from a given root",
)
@click.pass_context
def show_collection(ctx, root_collection):
    """Display a collection"""
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


@show.group("projects")
@click.pass_context
def projects(ctx):
    """Show project information in Egeria"""
    pass


@projects.command("projects")
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


@info.command("certification-types")
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


@projects.command("project-structure")
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


@projects.command("project-dependencies")
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


@info.command("to-dos")
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


@info.command("asset-types")
@click.pass_context
def show_asset_types(ctx):
    """Display engine-host status information"""
    c = ctx.obj
    display_asset_types(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


@info.command("user-ids")
@click.pass_context
def show_user_ids(ctx):
    """Display a list of known user ids"""
    c = ctx.obj
    list_user_ids(
        c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width
    )


@show.group("deployed-data")
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
#  Tell
#


@cli.group("tell")
@click.pass_context
def tell(ctx):
    """Perform actions an Egeria Objects"""
    pass

#
# dr.egeria
#
@tell.group("dr_egeria")
@click.pass_context
def tell_dr_egeria(ctx):
    """Execute Dr.Egeria actions"""
    pass

tell_dr_egeria.add_command(process_markdown_file)

@tell.group("glossary")
@click.pass_context
def tell_glossary(ctx):
    """Perform glossary actions"""
    pass




tell_glossary.add_command(create_glossary)
tell_glossary.add_command(delete_glossary)
tell_glossary.add_command(create_term)
tell_glossary.add_command(import_terms_csv)
tell_glossary.add_command(export_terms_csv)
tell_glossary.add_command(delete_term)
tell_glossary.add_command(create_category)
tell_glossary.add_command(delete_category)
tell_glossary.add_command(update_category)
tell_glossary.add_command(add_term_to_category)
tell_glossary.add_command(remove_term_from_category)

@tell.group("todo")
@click.pass_context
def tell_todo(ctx):
    """Perform todo actions"""
    pass


tell_todo.add_command(mark_todo_complete)
tell_todo.add_command(reassign_todo)
tell_todo.add_command(delete_todo)
tell_todo.add_command(create_todo)


if __name__ == "__main__":
    cli()
