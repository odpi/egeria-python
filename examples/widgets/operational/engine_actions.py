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
from pyegeria import ServerOps, AutomatedCuration, INTEGRATION_GUIDS
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)


@click.command('add-target')
@click.argument('integration-connector')
@click.argument('metadata-element')
@click.argument('catalog-target-name')
@click.pass_context
def add_catalog_target(ctx, integration_connector: str, metadata_element_guid:str, catalog_target_name:str)-> str:
    """Add catalog targets to the specified integration connector"""
    try:
        if integration_connector not in INTEGRATION_GUIDS.keys():
            click.echo('Integration connector is not known')

        c = ctx.obj
        a_client = AutomatedCuration(c.view_server, c.view_server_url, c.userid, c.password)
        token = a_client.create_egeria_bearer_token()

        guid = a_client.add_catalog_target(INTEGRATION_GUIDS[integration_connector], metadata_element_guid,
                                           catalog_target_name)

        click.echo(f"Added catalog target to {integration_connector} with a return guid of {guid}")


    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)



@click.command('remove-target')
@click.argument('relationship-guid')
@click.pass_context
def remove_catalog_target(ctx, relationship_guid: str):
    """Remove the catalog target specified by the relationship guidr"""
    try:
        c = ctx.obj
        a_client = AutomatedCuration(c.view_server, c.view_server_url, c.userid, c.password)
        token = a_client.create_egeria_bearer_token()

        a_client.remove_catalog_target(relationship_guid)

        click.echo(f"Removed catalog target with relationship guid of {relationship_guid}")


    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)


@click.command('update-target')
@click.argument('relationship-guid')
@click.argument('catalog-target-name')
@click.pass_context
def update_catalog_target(ctx, relationship_guid: str, catalog_target_name:str):
    """Update the catalog target specified by the relationship guid """
    try:
        c = ctx.obj
        a_client = AutomatedCuration(c.view_server, c.view_server_url, c.userid, c.password)
        token = a_client.create_egeria_bearer_token()

        guid = a_client.update_catalog_target(relationship_guid, catalog_target_name)

        click.echo(f"Update catalog target with relationship guid of  {relationship_guid} to a catalog target name of "
                   f"{catalog_target_name} with a return guid of {guid}")


    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)

