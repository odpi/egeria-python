#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


A object_action line interface for Egeria operations.

This is an emerging capability based on the **click** package. Feedback welcome!

"""
import os

import click
from trogon import tui
from loguru import logger
from pyegeria import config_logging,  settings

# from pyegeria import ServerOps
from commands.cli.ops_config import Config
from commands.ops.gov_server_actions import (
    add_catalog_target,
    refresh_gov_eng_config,
    remove_catalog_target,
    start_server,
    stop_server,
    update_catalog_target,
)
from commands.ops.list_archives import display_archive_list
from commands.ops.list_catalog_targets import display_catalog_targets
from commands.ops.load_archive import load_archive
from commands.ops.monitor_active_engine_activity import display_engine_activity
from commands.ops.monitor_engine_activity import display_engine_activity_c
from commands.ops.monitor_engine_status import display_gov_eng_status
from commands.ops.monitor_daemon_status import (
    display_integration_daemon_status,
)
from commands.ops.monitor_platform_status import (
    display_status as p_display_status,
)
from commands.ops.monitor_server_startup import display_startup_status
from commands.ops.monitor_server_status import (
    display_status as s_display_status,
)
from commands.ops.refresh_integration_daemon import refresh_connector
from commands.ops.restart_integration_daemon import restart_connector

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
app_settings = settings
app_config = app_settings.Environment
# config_logging()

@tui()
# @tui('menu', 'menu', 'A textual object_action line interface')
@click.version_option("5.4 ", prog_name="hey_egeria")
@click.group()
@click.option(
    "--server",
    default=app_config.egeria_metadata_store,
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
    default=app_config.console_width,
    type=int,
    help="Screen width, in characters, to use",
)
@click.option(
    "--home_glossary_name",
    default=app_settings.User_Profile.egeria_home_glossary_name,
    help="Glossary name to use as the home glossary",
)
@click.option(
    "--glossary_path",
    default=app_config.egeria_glossary_path,
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
    home_glossary_name,
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
        home_glossary_name,
        glossary_path,
        root_path,
        inbox_path,
        outbox_path
    )
    ctx.max_content_width = 300
    ctx.ensure_object(Config)



@cli.group("show")
@click.pass_context
def show(ctx):
    """Display an Egeria Object"""
    pass


@show.group("platforms")
@click.pass_context
def show_platforms(ctx):
    """Group of md_commands to show information about Egeria platforms"""
    pass


@show_platforms.command("status")
@click.pass_context
def show_platform_status(ctx):
    """Display a live status view of known platforms"""
    c = ctx.obj
    p_display_status(
        c.view_server, c.view_server_url, c.userid, c.password
    )


@show.group("servers")
@click.pass_context
def show_server(ctx):
    """Group of md_commands to show information about Egeria servers"""
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
    """Group of md_commands to show repository information"""
    pass


@show_repo.command("archives")
@click.pass_context
def show_archives(ctx):
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


@show.group("engines")
@click.pass_context
def engine_host(ctx):
    """Group of md_commands to show information about Egeria engines"""
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


@engine_host.command("current-activity")
@click.option(
    "--rowlimit",
    default=0,
    type=int,
    show_default=True,
    help="If non-zero, limit the number of rows returned",
)

@click.option(
    "--list",
    is_flag=True,
    default=False,
    show_default=True,
    help="If True, a paged list will be shown",
)
@click.pass_context
def current_eng_activity_status(ctx, rowlimit: int, list: bool):
    """Show Governance Activity in engine-host"""
    c = ctx.obj
    compressed = False
    if compressed:
        display_engine_activity_c(
            rowlimit,
            c.view_server,
            c.view_server_url,
            c.userid,
            c.password,
            list,
            c.jupyter,
            c.width,
        )
    else:
        display_engine_activity(
            rowlimit,
            c.view_server,
            c.view_server_url,
            c.userid,
            c.password,
            list,
            c.jupyter,
            c.width,
        )


@show.group("integrations")
@click.pass_context
def integrations(ctx):
    """Group of md_commands to show information about Egeria integrations"""
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
    display_catalog_targets(connector, c.view_server, c.view_server_url, c.userid, c.password, c.jupyter, c.width)


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
    """Group of md_commands to an integration_daemon"""
    pass


@integration_daemon.command("refresh")
@click.pass_context
@click.option(
    "--connector",
    default="all",
    help="Name of connector to refresh or 'all' to refresh all",
)

def refresh_connectors(ctx,  connector):
    """Refresh the specified integration connector or ALL connectors if not specified"""
    c = ctx.obj
    refresh_connector(
        connector, c.integration_daemon, c.integration_daemon_url, c.view_server, c.userid, c.password
    )


@integration_daemon.command("restart")
@click.pass_context
@click.option(
    "--connector",
    default="all",
    help="Name of connector to restart or 'all' to restart all",
)
def restart_connectors(ctx,  connector):
    """Restart the specified integration connector or ALL connectors if not specified"""
    c = ctx.obj
    restart_connector(
        connector, c.integration_daemon, c.integration_daemon_url, c.view_server, c.userid, c.password
    )


integration_daemon.add_command(add_catalog_target)
integration_daemon.add_command(remove_catalog_target)
integration_daemon.add_command(update_catalog_target)


@tell.group("engine-host")
@click.pass_context
def engine_host(ctx):
    """Group of md_commands to an engine-host"""
    pass


engine_host.add_command(refresh_gov_eng_config)


@tell.group("repository")
@click.pass_context
def repository(ctx):
    """Group of md_commands to a repository"""
    pass


repository.add_command(load_archive)

if __name__ == "__main__":
    cli()
