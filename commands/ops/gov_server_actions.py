"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


Click commands for Egeria server and catalog-target operations, used by `hey_egeria_ops tell` and
`hey_egeria tell`:

- `add-target`, `remove-target`, `update-target`: manage an integration connector's catalog targets.
- `refresh`: ask the engine host to reload its governance engine configuration.
- `start` / `stop`: activate an OMAG server from its stored configuration / shut it down.
"""

import click

from pyegeria import print_basic_exception, AutomatedCuration, EgeriaTech
from pyegeria.core.config import settings
from pyegeria.core._exceptions import (
    PyegeriaInvalidParameterException as PyegeriaInvalidParameterException,
    PyegeriaAPIException as PyegeriaAPIException,
    print_basic_exception as print_exception_response,
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
        c = ctx.obj
        a_client = AutomatedCuration(
            c.view_server, c.view_server_url, c.userid, c.password
        )
        token = a_client.create_egeria_bearer_token()

        integ_connector_guid = a_client.get_connector_guid(integration_connector)
        if not integ_connector_guid or integ_connector_guid == 'No connector found':
            raise PyegeriaInvalidParameterException('No Connector found')

        guid = a_client.add_catalog_target(
            integ_connector_guid,
            metadata_element_guid,
            catalog_target_name,
        )

        click.echo(
            f"Added catalog target to {integration_connector} with a return guid of {guid}"
        )

    except (PyegeriaInvalidParameterException, PyegeriaAPIException) as e:
        print_exception_response(e)


@click.command("remove-target")
@click.argument("relationship-guid")
@click.pass_context
def remove_catalog_target(ctx, relationship_guid: str):
    """Remove the catalog target specified by the relationship guid"""
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

    except (PyegeriaInvalidParameterException, PyegeriaAPIException) as e:
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

    except (PyegeriaInvalidParameterException, PyegeriaAPIException) as e:
        print_exception_response(e)


@click.command("refresh")
@click.option("--engine-host-guid", default=None, help="GUID of the engine host to refresh (default: the configured engine host, by name).")
@click.option("--engine", "gov_engine_name", default=None, help="Refresh only this governance engine (default: all).")
@click.option("--organization-name", default=settings.Environment.organization_name,
              help="Organization name prefix of the engine host's resource name")
@click.pass_context
def refresh_gov_eng_config(ctx, engine_host_guid: str, gov_engine_name: str, organization_name: str):
    """Ask the engine host to reload its governance engine configuration"""
    c = ctx.obj
    p_client = EgeriaTech(c.view_server, c.view_server_url, c.userid, c.password)
    token = p_client.create_egeria_bearer_token()
    try:
        p_client.refresh_gov_eng_config(
            gov_engine_name=gov_engine_name,
            server_guid=engine_host_guid,
            display_name=None if engine_host_guid else c.engine_host,
            organization_name=organization_name,
        )
        click.echo(f"Refreshed the governance engine configuration of {engine_host_guid or c.engine_host}")

    except (PyegeriaInvalidParameterException, PyegeriaAPIException) as e:
        print_exception_response(e)
    finally:
        p_client.close_session()


@click.command("start")
@click.pass_context
@click.option("--server", required=True, help="OMAG server to start, e.g. qs-metadata-store")
@click.option("--organization-name", default=settings.Environment.organization_name,
              help="Organization name prefix of the server's resource name")
def start_server(ctx, server, organization_name):
    """Activate an OMAG server from its stored configuration"""
    c = ctx.obj

    p_client = EgeriaTech(c.view_server, c.view_server_url, c.userid, c.password)
    token = p_client.create_egeria_bearer_token()
    try:
        p_client.activate_server_with_stored_config(display_name=server, organization_name=organization_name)

        click.echo(f"Started server {server}")

    except (PyegeriaInvalidParameterException, PyegeriaAPIException) as e:
        print_exception_response(e)
    finally:
        p_client.close_session()


@click.command("stop")
@click.option("--server", required=True, help="OMAG server to stop, e.g. qs-engine-host")
@click.option("--organization-name", default=settings.Environment.organization_name,
              help="Organization name prefix of the server's resource name")
@click.pass_context
def stop_server(ctx, server, organization_name):
    """Shut down an OMAG server (it can be started again later)"""
    c = ctx.obj
    p_client = EgeriaTech(c.view_server, c.view_server_url, c.userid, c.password)
    token = p_client.create_egeria_bearer_token()
    try:
        p_client.shutdown_server(display_name=server, organization_name=organization_name)
        click.echo(f"Stopped server {server}")
    except (PyegeriaInvalidParameterException, PyegeriaAPIException) as e:
        print_exception_response(e)
    finally:
        p_client.close_session()
