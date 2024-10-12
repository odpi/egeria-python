#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


A command line interface for Egeria Catalog User functions

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
from commands.cat.glossary_actions import create_glossary, delete_glossary, create_term
from commands.cat.list_archives import display_archive_list
from commands.cat.list_assets import display_assets
from commands.cat.list_cert_types import display_certifications
from commands.cat.list_deployed_catalogs import list_deployed_catalogs
from commands.cat.old_list_deployed_database_schemas import (
    list_deployed_database_schemas,
)
from commands.cat.list_deployed_databases import list_deployed_databases
from commands.cat.list_glossary import display_glossary_terms
from commands.cat.list_projects import display_project_list
from commands.cat.list_relationships import list_relationships
from commands.cat.list_tech_types import display_tech_types
from commands.cat.list_todos import display_to_dos as list_todos
from commands.cat.list_user_ids import list_user_ids

# from pyegeria import ServerOps
from commands.cli.ops_config import Config
from commands.my.todo_actions import (
    mark_todo_complete,
    reassign_todo,
    delete_todo,
    create_todo,
)


# class Config(object):
#     def __init__(self, server: str = None, url: str = None, userid:str = None, password:str = None,
#                  timeout:int = 30, paging: bool = False):
#         self.server = server
#         self.url = url
#         self.userid = userid
#         self.password = password
#         self.timeout = timeout
#         self.paging = paging
#
#
# pass_config = click.make_pass_decorator(Config)


# @tui
# @tui('menu','menu','A textual command line interface')
@tui()
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
    "--integration_daemon",
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


@cli.group("show")
def show():
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


@show.command("certification-types")
@click.option("--search-string", default="CertificationType", help="")
@click.pass_context
def show_certification_types(ctx, search_string):
    """Show certification types
    - generally stay with the default.
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


@show.command("to-dos")
@click.option("--search-string", default="*", help="View the list of To-Do items")
@click.option(
    "--status",
    type=click.Choice(
        ["OPEN", "IN_PROGRESS", "WAITING", "COMPLETE", "ABANDONED", "None"],
        case_sensitive=False,
    ),
    help="Enter an optional status filter",
    required=False,
    default=None,
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


@show.command("list-schemas")
@click.option("--catalog", default="*", help="What database or catalog to search")
@click.pass_context
def list_deployed_schemas(ctx, catalog):
    """Display a tree graph of information about an asset"""
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


@show.command("list-catalogs")
@click.option("--search_server", default="*", help="Server to search for catalogs")
@click.pass_context
def list_catalogs(ctx, search_server):
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
#  Tell
#


@cli.group("tell")
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


if __name__ == "__main__":
    cli()
