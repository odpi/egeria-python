#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


A command line interface for Egeria Users - of individual relevance

This is an emerging capability based on the **click** package. Feedback welcome!

"""
import os

import click
from trogon import tui

from pyegeria.commands.cli.ops_config import Config

from pyegeria.commands.my.monitor_open_todos import display_todos
from pyegeria.commands.my.monitor_my_todos import display_my_todos
from pyegeria.commands.my.list_my_profile import display_my_profile
from pyegeria.commands.my.list_my_roles import display_my_roles
from pyegeria.commands.my.todo_actions import (
    create_todo,
    delete_todo,
    change_todo_status,
    mark_todo_complete,
    reassign_todo,
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
        glossary_path,
    )
    ctx.max_content_width = 200
    ctx.ensure_object(Config)


@cli.group("show")
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
    """Display my roles"""
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
#  Tell
#


@cli.group("tell")
@click.pass_context
def tell(ctx):
    """Perform actions an Egeria Objects"""
    pass


tell.add_command(create_todo)
tell.add_command(delete_todo)
tell.add_command(change_todo_status)
tell.add_command(mark_todo_complete)
tell.add_command(reassign_todo)


if __name__ == "__main__":
    cli()
