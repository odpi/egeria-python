"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



Execute ToDo actions.

"""
import json
import time

import click
# from ops_config import Config, pass_config
from pyegeria import ServerOps, AutomatedCuration, INTEGRATION_GUIDS, MyProfile
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

erins_guid = "a588fb08-ae09-4415-bd5d-991882ceacba"
peter_guid	="a187bc48-8154-491f-97b4-a2f3c3f1a00e"
tanya_guid	="26ec1614-bede-4b25-a2a3-f8ed26db3aaa"


@click.command('create-todo')
@click.option('--name',prompt='Todo Name',help='Name of Todo', required=True)
@click.option('--description',prompt='Description',help='Brief description of To Do item', required=True)
@click.option('--type',prompt='Todo Type',help='Type of Todo', required=True, default = 'forMe')
@click.option('--priority',prompt='Todo Priority',type = int, help='Priority of Todo', required=True, default= 0)
@click.option('--due',prompt='Due Date',help='Due date of Todo (yyyy-mm-dd)', required=True)
@click.option('--assigned-to',prompt='Assigned to',help='Party the Todo is assigned to', required=True,
              default = 'Peter')
@click.pass_context
def create_todo(ctx,name,description,type,priority,due,assigned_to):
    """Create a new ToDo item"""
    c = ctx.obj
    m_client = MyProfile(c.view_server, c.view_server_url, user_id=c.userid, user_pwd=c.password)
    token = m_client.create_egeria_bearer_token()
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
                "status": "OPEN"
            },
            "assignToActorGUID": peter_guid
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



@click.command('delete-todo')
@click.argument('todo-guid')
@click.pass_context
def delete_todo(ctx, todo_guid):
    """Delete the todo item specified """
    c = ctx.obj
    m_client = MyProfile(c.view_server, c.view_server_url, user_id=c.userid, user_pwd=c.password)
    token = m_client.create_egeria_bearer_token()
    try:
        m_client.delete_to_do(todo_guid)

        click.echo(f"Deleted Todo item {todo_guid}")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()

@click.command('change-todo-status')
@click.argument('todo-guid')
@click.option('--new-status', type=click.Choice(['OPEN','IN_PROGRESS','WAITING','COMPLETE', 'ABANDONED'],
               case_sensitive='False'), help = 'Enter the new ToDo item status', required=True)
@click.pass_context
def change_todo_status(ctx, todo_guid, new_status):
    """Update a ToDo item status"""
    c = ctx.obj
    m_client = MyProfile(c.view_server, c.view_server_url, user_id=c.userid, user_pwd=c.password)
    token = m_client.create_egeria_bearer_token()
    try:


        body = {
            "properties": {
                "class": "ToDoProperties",
                "toDoStatus": new_status
            },
        }
        m_client.update_to_do(todo_guid, body, is_merge_update=True)

        click.echo(f"Marked todo item {todo_guid} as complete.")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()

@click.command('mark-todo-complete')
@click.argument('todo-guid')
@click.pass_context
def mark_todo_complete(ctx, todo_guid):
    """Mark the specified todo as complete"""
    try:
        c = ctx.obj
        m_client = MyProfile(c.view_server, c.view_server_url, user_id=c.userid, user_pwd=c.password)
        token = m_client.create_egeria_bearer_token()
        body = {
            "properties": {
                "class": "ToDoProperties",
                "completionTime" : time.asctime(),
                "toDoStatus": "COMPLETE"
            },
        }
        m_client.update_to_do(todo_guid, body, is_merge_update=True)

        click.echo(f"Marked todo item {todo_guid} as complete.")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()
        

@click.command('reassign-todo')
@click.argument('todo-guid')
@click.argument('new-actor-guid')
@click.pass_context
def reassign_todo(ctx, todo_guid, new_actor_guid):
    """Reassign ToDo item to new actor"""
    c = ctx.obj
    m_client = MyProfile(c.view_server, c.view_server_url, user_id=c.userid, user_pwd=c.password)
    token = m_client.create_egeria_bearer_token()
    try:

        m_client.reassign_to_do(todo_guid, new_actor_guid)

        click.echo(f"Reassigned Todo item {todo_guid} to {new_actor_guid}")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()
