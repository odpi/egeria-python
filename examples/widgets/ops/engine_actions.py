"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This script restarts an integration daemon.

"""

import os
from rich import print, print_json
from rich.console import Console

import time
import click
# from ops_config import Config, pass_config
from pyegeria import ServerOps, AutomatedCuration, INTEGRATION_GUIDS, Platform
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)




@click.command('stop')
@click.pass_context
def stop_server(ctx):
    """Stop an engine-host daemon"""
    try:
        c = ctx.obj
        p_client = Platform(c.engine_host, c.engine_host_url, c.admin_user, c.admin_user_password)

        p_client.shutdown_server()

        click.echo(f"Stopped server {c.engine_host}")
    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)


@click.command('start')
@click.pass_context
def start_server(ctx):
    """Start or restart an engine-host from its known configuration """
    try:
        c = ctx.obj
        p_client = Platform(c.engine_host, c.engine_host_url, c.admin_user, c.admin_user_password)

        p_client.activate_server_stored_config()

        click.echo(f"Started server {c.engine_host}")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)

