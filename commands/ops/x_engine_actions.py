"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



Execute engine actions.

"""

import click

# from ops_config import Config, pass_config
from pyegeria import EgeriaTech
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    print_exception_response,
)


@click.command("stop")
@click.option("--server", help="OMAG Server to stop")
@click.pass_context
def stop_server(ctx, server):
    """Stop an OMAG server daemon"""
    c = ctx.obj
    p_client = EgeriaTech(c.view_server, c.view_server_url, c.userid, c.password)
    token = p_client.create_egeria_bearer_token()
    try:
        server_guid = p_client.get_guid_for_name(server)

        p_client.shutdown_server(server_guid)
        click.echo(f"Stopped server {server}")
    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        p_client.close_session()


@click.command("start")
@click.option("--server", help="OMAG Server to start")
def start_server(ctx, server):
    """Start or restart an OMAG server from its known configuration"""
    c = ctx.obj
    p_client = EgeriaTech(c.view_server, c.view_server_url, c.userid, c.password)
    token = p_client.create_egeria_bearer_token()
    try:
        server_guid = p_client.get_element_guid_by_unique_name(server, "name")
        p_client.activate_server_with_stored_config(server_guid)

        click.echo(f"Started server {server}")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        p_client.close_session()


@click.command("refresh")
@click.pass_context
def refresh(ctx):
    """Start or restart an engine-host from its known configuration"""
    c = ctx.obj
    p_client = EgeriaTech(c.view_server, c.view_server_url, c.userid, c.password)
    token = p_client.create_egeria_bearer_token()
    try:
        engine_host_guid = p_client.get_guid_for_name(c.engine_host)
        p_client.refresh_gov_eng_config(engine_host_guid)

        click.echo(f"Refreshed server {c.engine_host}")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        p_client.close_session()
