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

# EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
# EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
# EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
# EGERIA_VIEW_SERVER = os.environ.get("VIEW_SERVER", "view-server")
# EGERIA_VIEW_SERVER_URL = os.environ.get(
#     "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
# )
# EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
# EGERIA_INTEGRATION_DAEMON_URL = os.environ.get(
#     "EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443"
# )
#
# EGERIA_USER = os.environ.get("EGERIA_USER", "garygeeke")
# EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")


@click.command("stop")
@click.option("--server", help="OMAG Server to stop")
# @click.option(
#     "--view-server", default=EGERIA_VIEW_SERVER, help="View Server to communicate with"
# )
# @click.option(
#     "--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to"
# )
# @click.option("--userid", default="garygeeke", envvar="EGERIA_USER", help="Egeria user")
# @click.option(
#     "--password",
#     default="secret",
#     envvar="EGERIA_PASSWORD",
#     help="Egeria user password",
# )
@click.pass_context
def stop_server(ctx, server):
    """Stop an engine-host daemon"""
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
# @click.option(
#     "--view-server", default=EGERIA_VIEW_SERVER, help="View Server to communicate with"
# )
# @click.option(
#     "--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to"
# )
# @click.option("--userid", default="garygeeke", envvar="EGERIA_USER", help="Egeria user")
# @click.option(
#     "--password",
#     default="secret",
#     envvar="EGERIA_USER_PASSWORD",
#     help="Egeria user password",
# )
def start_server(ctx, server):
    """Start or restart an engine-host from its known configuration"""
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
# @click.option(
#     "--engine-host", default=EGERIA_ENGINE_HOST, help="Engine Host to refresh"
# )
# @click.option(
#     "--view-server", default=EGERIA_VIEW_SERVER, help="View Server to communicate with"
# )
# @click.option(
#     "--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to"
# )
# @click.option("--userid", default="garygeeke", envvar="EGERIA_USER", help="Egeria user")
# @click.option(
#     "--password",
#     default="secret",
#     envvar="EGERIA_PASSWORD",
#     help="Egeria user password",
# )
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
