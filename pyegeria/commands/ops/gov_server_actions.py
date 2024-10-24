"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This script restarts an integration daemon.

"""

import os
from rich import print, print_json
from rich.console import Console

import click
from pyegeria import EgeriaTech, AutomatedCuration, INTEGRATION_GUIDS
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)


@click.command("add-target")
@click.argument("integration-connector")
@click.argument("metadata-element-guid")
@click.argument("catalog-target-name")
@click.pass_context
def add_catalog_target(
    ctx,
    integration_connector: str,
    metadata_element_guid: str,
    catalog_target_name: str,
) -> str:
    """Add catalog targets to the specified integration connector"""
    try:
        if integration_connector not in INTEGRATION_GUIDS.keys():
            click.echo("Integration connector is not known")

        c = ctx.obj
        a_client = AutomatedCuration(
            c.view_server, c.view_server_url, c.userid, c.password
        )
        token = a_client.create_egeria_bearer_token()

        guid = a_client.add_catalog_target(
            INTEGRATION_GUIDS[integration_connector],
            metadata_element_guid,
            catalog_target_name,
        )

        click.echo(
            f"Added catalog target to {integration_connector} with a return guid of {guid}"
        )

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)


@click.command("remove-target")
@click.argument("relationship-guid")
@click.pass_context
def remove_catalog_target(ctx, relationship_guid: str):
    """Remove the catalog target specified by the relationship guidr"""
    try:
        c = ctx.obj
        a_client = AutomatedCuration(
            c.view_server, c.view_server_url, c.userid, c.password
        )
        token = a_client.create_egeria_bearer_token()

        a_client.remove_catalog_target(relationship_guid)

        click.echo(
            f"Removed catalog target with relationship guid of {relationship_guid}"
        )

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)


@click.command("update-target")
@click.argument("relationship-guid")
@click.argument("catalog-target-name")
@click.pass_context
def update_catalog_target(ctx, relationship_guid: str, catalog_target_name: str):
    """Update the catalog target specified by the relationship guid"""
    try:
        c = ctx.obj
        a_client = AutomatedCuration(
            c.view_server, c.view_server_url, c.userid, c.password
        )
        token = a_client.create_egeria_bearer_token()

        guid = a_client.update_catalog_target(relationship_guid, catalog_target_name)

        click.echo(
            f"Update catalog target with relationship guid of  {relationship_guid} to a catalog target name of "
            f"{catalog_target_name} with a return guid of {guid}"
        )

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)


#
#   This method will be updated based on forthcoming changes on the Egeria server side
#
@click.command("refresh")
@click.option("-engine-host-guid", help="GUID of engine host to refresh.")
@click.pass_context
def refresh_gov_eng_config(ctx, engine_host_guid: str):
    """Start or restart an engine-host from its known configuration"""
    c = ctx.obj
    p_client = EgeriaTech(c.view_server, c.view_server_url, c.userid, c.password)
    token = p_client.create_egeria_bearer_token()
    try:
        p_client.refresh_gov_eng_config(None, None, c.engine_host)

        click.echo(f"Refreshed server {c.engine_host}")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        p_client.close_session()


@click.command("start")
@click.pass_context
@click.option("--server", default="simple-metadata-store", help="OMAG Server to start")
def start_server(ctx, server):
    """Start or restart an engine-host from its known configuration"""
    c = ctx.obj

    p_client = EgeriaTech(c.view_server, c.view_server_url, c.userid, c.password)
    token = p_client.create_egeria_bearer_token()
    try:
        server_guid = p_client.get_element_guid_by_unique_name(server, "name")
        p_client.activate_server_with_stored_config(None, server)

        click.echo(f"Started server {server}")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        p_client.close_session()


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
        p_client.shutdown_server(None, server)
        click.echo(f"Stopped server {server}")
    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        p_client.close_session()
