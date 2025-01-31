#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


A command line interface for Egeria operations.

This is an emerging capability based on the **click** package. Feedback welcome!

"""
import os

import click
from trogon import tui

# from pyegeria import ServerOps
from pyegeria.commands.cli.ops_config import Config

from pyegeria.commands.ops.gov_server_actions import (
    add_catalog_target,
    remove_catalog_target,
    update_catalog_target,
    refresh_gov_eng_config,
    start_server,
    stop_server,
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
from pyegeria.commands.ops.list_archives import display_archive_list


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


@tui()
# @tui('menu', 'menu', 'A textual command line interface')
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
        glossary_path
    )
    ctx.max_content_width = 200
    ctx.ensure_object(Config)


@cli.group("show")
@click.pass_context
def show(ctx):
    """Display an Egeria Object"""
    pass


@show.group("platforms")
@click.pass_context
def show_platforms(ctx):
    """Group of commands to show information about Egeria platforms"""
    pass


@show_platforms.command("status")
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

@show.group("repository")
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


@show.group("engines")
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
    "--compressed",
    is_flag=True,
    default=False,
    show_default=True,
    help="Compressed combines some attributes into a single column",
)
@click.option(
    "--list",
    is_flag=True,
    default=False,
    show_default=True,
    help="If True, a paged list will be shown",
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


@show.group("integrations")
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
@click.pass_context
def integrations_status(ctx, connector_list, list):
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
    )


@integrations.command("--targets")
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
#  Tell
#


@cli.group("tell")
@click.pass_context
def tell(ctx):
    """Perform actions an Egeria Objects"""
    pass


@tell.group("servers")
@click.pass_context
def servers(ctx):
    """Perform actions on OMAG Servers"""
    pass


servers.add_command(start_server)
servers.add_command(stop_server)


@tell.group("integration-daemon")
@click.pass_context
def integration_daemon(ctx):
    """Group of commands to an integration_daemon"""
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
    help="Name of the integration server to restart",
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


@tell.group("engine-host")
@click.pass_context
def engine_host(ctx):
    """Group of commands to an engine-host"""
    pass


engine_host.add_command(refresh_gov_eng_config)


@tell.group("repository")
@click.pass_context
def repository(ctx):
    """Group of commands to a repository"""
    pass


repository.add_command(load_archive)

if __name__ == "__main__":
    cli()
