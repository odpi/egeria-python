#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


A command line interface for Egeria operations.

This is an emerging capability based on the **click** package. Feedback welcome!

"""
import click
from trogon import tui
from pyegeria import ServerOps
from ops_config import Config, pass_config
import monitor_gov_eng_status
import monitor_server_status
import monitor_server_list
import monitor_integ_daemon_status
import monitor_platform_status
import monitor_engine_activity
import refresh_integration_daemon
import restart_integration_daemon
import integration_daemon_actions

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
@click.option('--server', default = 'active-metadata-store', envvar = 'EGERIA_METADATA_STORE',
              help='Egeria metadata store to work with')
@click.option('--url', default = 'https://localhost:9443', envvar= 'EGERIA_PLATFORM_URL',
              help='URL of Egeria metadata store platform to connect to')
@click.option('--integration-daemon', default = 'integration-daemon', envvar = 'EGERIA_INTEGRATION_DAEMON',
              help='Egeria integration daemon to work with')
@click.option('--integration_daemon_url', default = 'https://localhost:9443', envvar= 'EGERIA_INTEGRATION_DAEMON_URL',
              help='URL of Egeria integration daemon platform to connect to')
@click.option('--view_server', default = 'view-server', envvar = 'EGERIA_VIEW_SERVER',
              help='Egeria view server to work with')
@click.option('--view_server_url', default = 'https://localhost:9443', envvar= 'EGERIA_VIEW_SERVER_URL',
              help='URL of Egeria view server platform to connect to')
@click.option('--engine_host', default = 'engine-host', envvar = 'EGERIA_ENGINE_HOST',
              help='Egeria engine host to work with')
@click.option('--engine_host_url', default = 'https://localhost:9443', envvar= 'EGERIA_ENGINE_HOST_URL',
              help='URL of Egeria engine host platform to connect to')
@click.option('--admin_user', default = 'garygeeke', envvar = 'EGERIA_ADMIN_USER', help='Egeria admin user')
@click.option('--admin_user_password', default = 'secret', envvar = 'EGERIA_ADMIN_PASSWORD',
              help='Egeria admin password')
@click.option('--userid', default = 'garygeeke', envvar = 'EGERIA_USER', help='Egeria user')
@click.option('--password', default = 'secret', envvar = 'EGERIA_PASSWORD',
              help='Egeria user password')
@click.option('--timeout', default = 60, help = 'Number of seconds to wait')
@click.option('--verbose', is_flag = True, default = False, help = 'Enable verbose mode')
@click.option('--paging', is_flag = True, default = False, help = 'Enable paging snapshots vs live updates')
@click.pass_context
def cli(ctx, server, url, view_server, view_server_url, integration_daemon, integration_daemon_url,
        engine_host, engine_host_url, admin_user, admin_user_password, userid, password, timeout, paging, verbose):
    """An Egeria Command Line interface for Operations """
    ctx.obj = Config(server, url, view_server, view_server_url, integration_daemon,
                     integration_daemon_url, engine_host, engine_host_url,
                     admin_user, admin_user_password,userid, password,
                     timeout, paging, verbose)
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
    monitor_platform_status.display_status(c.view_server,c.view_server_url,
                                           c.admin_user,c.admin_user_password)


@show.group("servers")
@click.pass_context
def show_server(ctx):
    """Group of commands to show information about Egeria servers"""
    pass

@show_server.command('status')
@click.option('--full', is_flag=True, default = False, help='If True, full server descriptions will be shown')
@click.pass_context
def show_server_status(ctx, full):
    """Display a live status view of Egeria servers for the specified Egeria platform"""
    c = ctx.obj
    if full:
        monitor_server_list.display_status(c.metadata_store, c.metadata_store_url, c.admin_user,c.admin_user_password)
    else:
        monitor_server_status.display_status(c.metadata_store, c.metadata_store_url, c.admin_user,c.admin_user_password)

@show.group("engines")
@click.pass_context
def engine_host(ctx):
    """Group of commands to show information about Egeria engines"""
    pass

@engine_host.command("status")
@click.option('--list', is_flag=True, default = False, help='If True, a paged list will be shown')
@click.pass_context
def gov_eng_status(ctx,list):
    """Display engine-host status information"""
    c = ctx.obj
    monitor_gov_eng_status.display_gov_eng_status(c.engine_host, c.engine_host_url,
                                                                  c.userid, c.password,
                                                  list)

@engine_host.command('activity')
@click.option('--list', is_flag=True, default = False, help='If True, a paged list will be shown')
@click.pass_context
def eng_activity_status(ctx,list):
    """Show Governance Activity in engine-host"""
    c = ctx.obj
    monitor_engine_activity.display_engine_activity(c.view_server, c.view_server_url,
                                                      c.userid, c.password,
                                                      list)


@show.group('integrations')
@click.pass_context
def integrations(ctx):
    """Group of commands to show information about Egeria integrations"""
    pass

@integrations.command("status")
@click.option('--list', is_flag=True, default = False, help='If True, a paged list will be shown')
@click.pass_context
def integrations_status(ctx,list):
    """Display integration-daemon status information"""
    c = ctx.obj
    monitor_integ_daemon_status.display_integration_daemon_status(c.integration_daemon, c.integration_daemon_url,
                                                                      c.view_server, c.view_server_url,
                                                                 c.userid, c.password, list)

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
@click.option('--connector', default = 'all', help="Name of connector to refresh or 'all' to refresh all")
def refresh_connectors(ctx,connector):
    """Refresh the specified integration connector or ALL connectors if not specified"""
    c = ctx.obj
    refresh_integration_daemon.refresh_connector(connector,c.integration_daemon, c.integration_daemon_url,
                                   c.userid, c.passwordcatalog_target_actions.py )

@integration_daemon.command('restart')
@click.pass_context
@click.option('--connector', default = 'all', help="Name of connector to restart or 'all' to restart all")
def restart_connectors(ctx,connector):
    """Restart the specified integration connector or ALL connectors if not specified"""
    c = ctx.obj
    restart_integration_daemon.restart_connector(connector,c.integration_daemon, c.integration_daemon_url,
                                   c.userid, c.password)

integration_daemon.add_command(integration_daemon_actions.add_catalog_target)
integration_daemon.add_command(integration_daemon_actions.remove_catalog_target)
integration_daemon.add_command(integration_daemon_actions.update_catalog_target)
integration_daemon.add_command(integration_daemon_actions.stop_server)
integration_daemon.add_command(integration_daemon_actions.start_server)


if __name__ == '__main__':
    cli()