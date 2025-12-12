"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



Execute Glossary actions.

"""

import csv
import json
import os
import sys
import time
from datetime import datetime

import click


from pyegeria import EgeriaTech, body_slimmer, settings
from pyegeria._exceptions import (
    PyegeriaException, print_basic_exception
)
app_config = settings.Environment

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

COLLECTION_TYPES = ["Collection", "Glossary", "CollectionFolder", "RootCollection", "WorkItemList", "SolutionBlueprint" ]


@click.command("add-element-to-collection")
@click.option("--element-guid", required=True, default = "",help="GUID of the element to add to a Collection")
@click.option("--collection-guid", required=True, default = "", help="GUID of the Collection to add an element to")
@click.option("--server", default=app_config.egeria_view_server, help="Egeria view server to use")
@click.option(
    "--url", default=app_config.egeria_view_server_url, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")


def add_element_to_collection(server, url, userid, password, timeout, element_guid, collection_guid):
    """Add a glossary term to a Collection"""
    m_client = EgeriaTech(server, url, user_id=userid, user_pwd=password)
    token = m_client.create_egeria_bearer_token()
    try:
        element_guid = element_guid.strip()
        collection_guid = collection_guid.strip()
        m_client.add_to_collection(element_guid, collection_guid)

        click.echo(
            f"Added element with GUID: {element_guid} to Collection with GUID: {collection_guid}\n"
        )

    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        m_client.close_session()

@click.command("remove-element-from-collection")
@click.option("--element-guid", required=True, default = "",help="GUID of the element to remove from the collection")
@click.option("--collection-guid", required=True, default = "", help="GUID of collection to remove the element from")

@click.option("--server", default=app_config.egeria_view_server, help="Egeria view server to use")
@click.option(
    "--url", default=app_config.egeria_view_server_url, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")

def remove_element_from_collection(server, url, userid, password, timeout, element_guid, collection_guid):
    """Remove an element from a Collection"""
    m_client = EgeriaTech(server, url, user_id=userid, user_pwd=password)
    token = m_client.create_egeria_bearer_token()
    try:
        element_guid = element_guid.strip()
        collection_guid = collection_guid.strip()
        body = {
            "class": "DeleteRelationshipRequestBody"
        }
        m_client.remove_from_collection( collection_guid, element_guid, body)

        click.echo(
            f"Removed term with GUID: {element_guid} from Collection with GUID: {collection_guid}\n"
        )

    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        m_client.close_session()


@click.command("create-collection")
@click.option("--name", help="Collection Name",default = "", required=True)
@click.option("--kind", help="Kind of Collection", default = "Collection",
            type=click.Choice(COLLECTION_TYPES, case_sensitive=False))
@click.option(
    "--description",
    help="Description of the Collection",
    default="A description goes here",
)
@click.option(
    "--category", default = "",
    help="Category of the Collection"
)
@click.option("--server", default=app_config.egeria_view_server, help="Egeria view server to use.")
@click.option(
    "--url", default=app_config.egeria_view_server_url, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
def create_collection(
    server: str,
    url: str,
    userid: str,
    password: str,
    timeout: int,
    name: str,
    kind: str,
    description: str,
    category: str,
) -> None:
    """Create a new Collection"""

    try:
        m_client = EgeriaTech(server, url, userid, password)
        token = m_client.create_egeria_bearer_token()

        collection_guid = m_client.create_collection( display_name = name, description = description, category = category,
                                                      prop = [kind])
        print(f"New categry \'{name}\' created with id of \'{collection_guid}\'")

    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        m_client.close_session()


@click.command("update-collection")
@click.option("--name", help="Collection Name", default = "",required=False)
@click.option("--description", default = "",help="Description of the Collection")
@click.option("--category", default = "", help="Category of the Collection")
@click.option("--server", default=app_config.egeria_view_server, help="Egeria view server to use")
@click.option(
    "--url", default=app_config.egeria_view_server_url, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
@click.argument("collection-guid")

def update_collection(collection_guid, name, description, category, server, url, userid, password, timeout, ):
    """Update the collection specified"""
    m_client = EgeriaTech(server, url, user_id=userid, user_pwd=password)
    token = m_client.create_egeria_bearer_token()
    try:
        body = {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "CollectionProperties",
            "name" : name,
            "description" : description,
            "category": category
          },
        }
        m_client.update_collection(collection_guid, body_slimmer(body))

        click.echo(f"Updated glossary: {collection_guid}")

    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        m_client.close_session()

@click.command("delete-collection")
@click.argument("collection-guid")
@click.option("--server", default=app_config.egeria_view_server, help="Egeria view server to use")
@click.option(
    "--url", default=app_config.egeria_view_server_url, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")

def delete_collection(server, url, userid, password, timeout, collection_guid):
    """Delete the collection specified"""
    m_client = EgeriaTech(server, url, user_id=userid, user_pwd=password)
    token = m_client.create_egeria_bearer_token()
    try:
        m_client.delete_collection(collection_guid)

        click.echo(f"Deleted collection: {collection_guid}")

    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        m_client.close_session()