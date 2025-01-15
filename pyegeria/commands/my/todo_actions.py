"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



Execute ToDo actions.

"""
import os
import time
from datetime import datetime

import click

from pyegeria import MyProfile
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    print_exception_response,
)

erins_guid = "dcfd7e32-8074-4cdf-bdc5-9a6f28818a9d"
peter_guid = "59f0232c-f834-4365-8e06-83695d238d2d"
tanya_guid = "a987c2d2-c8b6-4882-b344-c47956d2de97"

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get(
    "EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443"
)
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")


@click.command("create-todo")
@click.option("--server", default=EGERIA_VIEW_SERVER, help="Egeria view server to use.")
@click.option(
    "--url",
    default=EGERIA_VIEW_SERVER_URL,
    help="URL of Egeria platform to connect to.",
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
@click.option("--name", help="Name of Todo", required=True)
@click.option(
    "--description",
    help="Brief description of To Do item",
    required=True,
)
@click.option("--type", help="Type of Todo", required=True, default="forMe")
@click.option(
    "--priority",
    type=int,
    help="Priority of Todo",
    required=True,
    default=0,
)
@click.option(
    "--due",
    help="Due date of Todo (yyyy-mm-dd)",
    default=datetime.now().strftime("%Y-%m-%d"),
    required=True,
)
@click.option(
    "--assigned-to",
    help="Party the Todo is assigned to",
    required=True,
    default=peter_guid,
)
def create_todo(
    server,
    url,
    userid,
    password,
    timeout,
    name,
    description,
    type,
    priority,
    due,
    assigned_to,
):
    """Create a new ToDo item"""
    m_client = MyProfile(server, url, user_id=userid, user_pwd=password)
    m_client.create_egeria_bearer_token()
    try:
        body = {
            "properties": {
                "class": "ToDoProperties",
                "qualifiedName": f"{name}-{time.asctime()}",
                "name": name,
                "description": description,
                "toDoType": type,
                "priority": priority,
                "dueTime": due,
                "status": "OPEN",
            },
            "assignToActorGUID": assigned_to,
        }

        resp = m_client.create_to_do(body)
        # if type(resp) is str:
        click.echo(f"Response was {resp}")
        # elif type(resp) is dict:
        #     click.echo(json.dumps(resp), indent = 2)

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()


@click.command("delete-todo")
@click.option(
    "--server", default=EGERIA_VIEW_SERVER, help="Egeria metadata store to load"
)
@click.option(
    "--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
@click.argument("todo-guid")
def delete_todo(server, url, userid, password, timeout, todo_guid):
    """Delete the todo item specified"""
    m_client = MyProfile(server, url, user_id=userid, user_pwd=password)
    m_client.create_egeria_bearer_token()
    try:
        m_client.delete_to_do(todo_guid)

        click.echo(f"Deleted Todo item {todo_guid}")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()


@click.command("change-todo-status")
@click.argument("todo-guid")
@click.option(
    "--server", default=EGERIA_VIEW_SERVER, help="Egeria metadata store to load"
)
@click.option(
    "--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
@click.option(
    "--new-status",
    type=click.Choice(
        ["OPEN", "IN_PROGRESS", "WAITING", "COMPLETE", "ABANDONED"],
        case_sensitive="False",
    ),
    help="Enter the new ToDo item status",
    required=True,
)
def change_todo_status(server, url, userid, password, timeout, todo_guid, new_status):
    """Update a ToDo item status"""
    m_client = MyProfile(server, url, user_id=userid, user_pwd=password)
    m_client.create_egeria_bearer_token()
    try:
        body = {"class": "ToDoProperties", "toDoStatus": new_status}

        m_client.update_to_do(todo_guid, body, is_merge_update=True)

        click.echo(f"Changed todo item {todo_guid} status to {new_status}.")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()


@click.command("mark-todo-complete")
@click.option(
    "--server", default=EGERIA_VIEW_SERVER, help="Egeria metadata store to load"
)
@click.option(
    "--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
@click.argument("todo-guid")
def mark_todo_complete(server, url, userid, password, timeout, todo_guid):
    """Mark the specified todo as complete"""
    m_client = MyProfile(server, url, user_id=userid, user_pwd=password)
    try:
        m_client.create_egeria_bearer_token()
        body = {
            "class": "ToDoProperties",
            "completionTime": time.asctime(),
            "toDoStatus": "COMPLETE",
        }

        m_client.update_to_do(todo_guid, body, is_merge_update=True)

        click.echo(f"Marked todo item {todo_guid} as complete.")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()


@click.command("reassign-todo")
@click.option(
    "--server", default=EGERIA_VIEW_SERVER, help="Egeria metadata store to load"
)
@click.option(
    "--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
@click.argument("todo-guid")
@click.argument("new-actor-guid")
def reassign_todo(server, url, userid, password, timeout, todo_guid, new_actor_guid):
    """Reassign ToDo item to new actor"""
    m_client = MyProfile(server, url, user_id=userid, user_pwd=password)
    m_client.create_egeria_bearer_token()
    try:
        m_client.reassign_to_do(todo_guid, new_actor_guid)

        click.echo(f"Reassigned Todo item {todo_guid} to {new_actor_guid}")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()
