#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


A command line interface for Egeria operations.

This is an emerging capability based on the **click** package. Feedback welcome!

"""
import click
from trogon import tui

# from pyegeria import ServerOps
from examples.widgets.cli.ops_config import Config
from examples.widgets.operational.integration_daemon_actions import (add_catalog_target, remove_catalog_target,
                                                                     update_catalog_target, stop_server, start_server)
from examples.widgets.operational.list_catalog_targets import display_catalog_targets
from examples.widgets.operational.monitor_engine_activity import display_engine_activity
from examples.widgets.operational.monitor_gov_eng_status import display_gov_eng_status
from examples.widgets.operational.monitor_integ_daemon_status import display_integration_daemon_status
from examples.widgets.operational.monitor_platform_status import display_status as p_display_status
from examples.widgets.operational.monitor_server_list import display_status as display_list
from examples.widgets.operational.monitor_server_status import display_status as s_display_status
from examples.widgets.operational.refresh_integration_daemon import refresh_connector
from examples.widgets.operational.restart_integration_daemon import restart_connector


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
@tui()
@click.version_option("0.0.1", prog_name="egeria_ops")
@click.group()
@click.option('--server', default='active-metadata-store', envvar='EGERIA_METADATA_STORE',
              help='Egeria metadata store to work with')
@click.option('--url', default='https://localhost:9443', envvar='EGERIA_PLATFORM_URL',
              help='URL of Egeria metadata store platform to connect to')
@click.option('--integration-daemon', default='integration-daemon', envvar='EGERIA_INTEGRATION_DAEMON',
              help='Egeria integration daemon to work with')
@click.option('--integration_daemon_url', default='https://localhost:9443', envvar='EGERIA_INTEGRATION_DAEMON_URL',
              help='URL of Egeria integration daemon platform to connect to')
@click.option('--view_server', default='view-server', envvar='EGERIA_VIEW_SERVER',
              help='Egeria view server to work with')
@click.option('--view_server_url', default='https://localhost:9443', envvar='EGERIA_VIEW_SERVER_URL',
              help='URL of Egeria view server platform to connect to')
@click.option('--engine_host', default='engine-host', envvar='EGERIA_ENGINE_HOST',
              help='Egeria engine host to work with')
@click.option('--engine_host_url', default='https://localhost:9443', envvar='EGERIA_ENGINE_HOST_URL',
              help='URL of Egeria engine host platform to connect to')
@click.option('--admin_user', default='garygeeke', envvar='EGERIA_ADMIN_USER', help='Egeria admin user')
@click.option('--admin_user_password', default='secret', envvar='EGERIA_ADMIN_PASSWORD',
              help='Egeria admin password')
@click.option('--userid', default='garygeeke', envvar='EGERIA_USER', help='Egeria user')
@click.option('--password', default='secret', envvar='EGERIA_PASSWORD',
              help='Egeria user password')
@click.option('--timeout', default=60, help='Number of seconds to wait')
@click.option('--verbose', is_flag=True, default=False, help='Enable verbose mode')
@click.option('--paging', is_flag=True, default=False, help='Enable paging snapshots vs live updates')
@click.option('--jupyter', is_flag=True, default=False, envvar='EGERIA_JUPYTER',
              help='Enable for rendering in a Jupyter terminal')
@click.option('--width', default=200, envvar='EGERIA_WIDTH', help='Screen width, in characters, to use')
@click.pass_context
def cli(ctx, server, url, view_server, view_server_url, integration_daemon, integration_daemon_url,
        engine_host, engine_host_url, admin_user, admin_user_password, userid, password, timeout, paging,
        verbose, jupyter, width):
    """An Egeria Command Line interface for Operations """
    ctx.obj = Config(server, url, view_server, view_server_url, integration_daemon,
                     integration_daemon_url, engine_host, engine_host_url,
                     admin_user, admin_user_password, userid, password,
                     timeout, paging, verbose, jupyter, width)
    ctx.max_content_width = 200
    ctx.ensure_object(Config)
    if verbose:
        click.echo(f"we are in verbose mode - server is {server}")


@cli.group("show")
@click.pass_context
def show(ctx):
    """Display an Egeria Object"""
    pass


@show.group('platforms')
@click.pass_context
def show_platform(ctx):
    """Group of commands to show information about Egeria platforms"""
    pass


@show_platform.command('status')
@click.pass_context
def show_platform_status(ctx):
    """Display a live status view of known platforms"""
    c = ctx.obj
    p_display_status(c.view_server, c.view_server_url,
                     c.admin_user, c.admin_user_password)


@show.group("servers")
@click.pass_context
def show_server(ctx):
    """Group of commands to show information about Egeria servers"""
    pass


@show_server.command('status')
@click.option('--full', is_flag=True, default=False, help='If True, full server descriptions will be shown')
@click.pass_context
def show_server_status(ctx, full):
    """Display a live status view of Egeria servers for the specified Egeria platform"""
    c = ctx.obj
    if full:
        display_list(c.metadata_store, c.metadata_store_url, c.admin_user, c.admin_user_password, c.jupyter, c.width)
    else:
        s_display_status(c.metadata_store, c.metadata_store_url, c.admin_user, c.admin_user_password, c.jupyter,
                         c.width)


@show.group("engines")
@click.pass_context
def engine_host(ctx):
    """Group of commands to show information about Egeria engines"""
    pass


@engine_host.command("status")
@click.option('--list', is_flag=True, default=False, help='If True, a paged list will be shown')
@click.pass_context
def gov_eng_status(ctx, list):
    """Display engine-host status information"""
    c = ctx.obj
    display_gov_eng_status(c.engine_host, c.engine_host_url,
                           c.admin_user, c.admin_user_password,
                           list, c.jupyter, c.width)


@engine_host.command('activity')
@click.option('--list', is_flag=True, default=False, help='If True, a paged list will be shown')
@click.pass_context
def eng_activity_status(ctx, list):
    """Show Governance Activity in engine-host"""
    c = ctx.obj
    display_engine_activity(c.view_server, c.view_server_url,
                            c.admin_user, c.admin_user_password,
                            list, c.jupyter, c.width)


@show.group('integrations')
@click.pass_context
def integrations(ctx):
    """Group of commands to show information about Egeria integrations"""
    pass


@integrations.command("status")
@click.option('--list', is_flag=True, default=False, help='If True, a paged list will be shown')
@click.pass_context
def integrations_status(ctx, list):
    """Display integration-daemon status information"""
    c = ctx.obj
    display_integration_daemon_status(c.integration_daemon, c.integration_daemon_url,
                                      c.view_server, c.view_server_url,
                                      c.userid, c.password, list, c.jupyter, c.width)


@integrations.command("targets")
@click.pass_context
@click.argument('connector', nargs=1)
def integrations_status(ctx, connector):
    """Display Catalog Targets for a connector"""
    c = ctx.obj
    display_catalog_targets(connector, c.view_server, c.view_server_url,
                            c.userid, c.password, c.jupyter, c.width)


#
#  Tell
#

@cli.group('tell')
@click.pass_context
def tell(ctx):
    """Perform actions an Egeria Objects"""
    pass


@tell.group('integration_daemon')
@click.pass_context
def integration_daemon(ctx):
    """Group of commands to an integration-daemon"""
    pass


@integration_daemon.command('refresh')
@click.pass_context
@click.option('--connector', default='all', help="Name of connector to refresh or 'all' to refresh all")
def refresh_connectors(ctx, connector):
    """Refresh the specified integration connector or ALL connectors if not specified"""
    c = ctx.obj
    refresh_connector(connector, c.integration_daemon, c.integration_daemon_url,
                      c.userid, c.password)


@integration_daemon.command('restart')
@click.pass_context
@click.option('--connector', default='all', help="Name of connector to restart or 'all' to restart all")
def restart_connectors(ctx, connector):
    """Restart the specified integration connector or ALL connectors if not specified"""
    c = ctx.obj
    restart_connector(connector, c.integration_daemon, c.integration_daemon_url,
                      c.userid, c.password)


integration_daemon.add_command(add_catalog_target)
integration_daemon.add_command(remove_catalog_target)
integration_daemon.add_command(update_catalog_target)
integration_daemon.add_command(stop_server)
integration_daemon.add_command(start_server)

if __name__ == '__main__':
    cli()
