"""
Functional tests for the MyProfile OMVS client against a live Egeria (e.g. the
egeria-workspaces quick start). Run explicitly; not part of the CI unit suite:

    pytest tests/functional-tests/test_my_profile.py

These tests deliberately do not catch PyegeriaException: an Egeria error fails the
test. They used to catch it and print "failed as expected or due to env", which hid
real defects (ISSUE-115, ISSUE-116) and calls to methods that no longer exist.

Some tests write to Egeria (blog/activity entries, to-dos, an action). To-dos and
actions are deleted again; activity entries are not, so use a disposable instance.
"""
import json
from datetime import datetime

import pytest
from rich.console import Console
from rich.markdown import Markdown

from pyegeria import NO_ELEMENTS_FOUND
from pyegeria.omvs.my_profile import MyProfile

console = Console(width=150)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "erinoverview"
USER_PWD = "secret"

# AssetMaker's action queries default to ["IN_PROGRESS"]; a new to-do is REQUESTED
OPEN_STATUSES = ["REQUESTED", "WAITING", "IN_PROGRESS"]


def show(label: str, response) -> None:
    print(f"\n{label}: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\n{label}: {response}")


def guids(response) -> list[str]:
    """GUIDs of the elements in a JSON result; [] for the "No elements found" string."""
    if isinstance(response, list):
        return [element["elementHeader"]["guid"] for element in response]
    assert response == NO_ELEMENTS_FOUND, f"Unexpected response: {response}"
    return []


def assert_list_or_none_found(response) -> None:
    assert isinstance(response, list) or response == NO_ELEMENTS_FOUND, f"Unexpected response: {response}"


class TestMyProfile:
    @pytest.fixture
    def profile_client(self):
        client = MyProfile(VIEW_SERVER, PLATFORM_URL, USER_ID, USER_PWD)
        client.create_egeria_bearer_token(USER_ID, USER_PWD)
        yield client
        client.close_session()

    @pytest.fixture
    def profile_guid(self, profile_client) -> str:
        profile = profile_client.get_my_profile(output_format="JSON", graph_query_depth=0)
        if isinstance(profile, list):
            profile = profile[0]
        return profile["elementHeader"]["guid"]

    @pytest.fixture
    def todo_guid(self, profile_client):
        """A to-do created for the test user, deleted again afterwards."""
        guid = profile_client.create_my_todo(f"test-todo-{datetime.now().isoformat()}", "REQUESTED",
                                             "Functional test to-do", "Testing MyProfile", 3)
        assert isinstance(guid, str) and guid
        yield guid
        profile_client.delete_asset(guid)

    # --- The user's profile and what is linked to it ---

    def test_get_my_profile(self, profile_client):
        profile = profile_client.get_my_profile(output_format="JSON", report_spec="My-User-MD", graph_query_depth=10)
        assert profile and isinstance(profile, (dict, list))
        if isinstance(profile, str):
            console.print(Markdown(profile))
        else:
            print(json.dumps(profile, indent=2))

    def test_get_my_actors(self, profile_client):
        # Every demo persona has a user identity and roles linked to their profile
        response = profile_client.get_my_actors()
        show("Retrieved actors", response)
        assert isinstance(response, list) and response

    def test_get_my_user_identities(self, profile_client):
        response = profile_client.get_my_user_identities(output_format="JSON")
        show("Retrieved user identities", response)
        assert isinstance(response, list) and response
        assert {e["elementHeader"]["type"]["typeName"] for e in response} == {"UserIdentity"}

    def test_get_my_user_identities_as_dict(self, profile_client):
        response = profile_client.get_my_user_identities(output_format="DICT", report_spec="Referenceable")
        show("Retrieved user identities", response)
        assert isinstance(response, list) and response

    def test_get_my_roles(self, profile_client):
        response = profile_client.get_my_roles()
        show("Retrieved roles", response)
        assert isinstance(response, list) and response

    def test_get_my_resources(self, profile_client):
        # Resources (e.g. a bookmarks collection) are optional, so none is fine
        response = profile_client.get_my_resources()
        show("Retrieved resources", response)
        assert_list_or_none_found(response)

    def test_get_my_assigned_actions(self, profile_client):
        response = profile_client.get_my_assigned_actions()
        show("Retrieved assigned actions", response)
        assert_list_or_none_found(response)

    def test_get_my_sponsored_actions(self, profile_client):
        response = profile_client.get_my_sponsored_actions()
        show("Retrieved sponsored actions", response)
        assert_list_or_none_found(response)

    def test_get_my_requested_actions(self, profile_client):
        response = profile_client.get_my_requested_actions()
        show("Retrieved requested actions", response)
        assert_list_or_none_found(response)

    # --- Activity entries (not cleaned up) ---

    def test_blog_my_activity(self, profile_client):
        body = {
            "class": "NewAttachmentRequestBody",
            "properties": {
                "class": "NotificationProperties",
                "qualifiedName": f"Blog::Blog-{datetime.now().isoformat()}",
                "displayName": "A new Test Activity",
                "situation": "Testing activity logging",
                "description": "This is a test notification",
            }
        }
        response = profile_client.blog_my_activity(body=body)
        show("Blogged activity GUID", response)
        assert isinstance(response, str) and response

    def test_log_my_activity(self, profile_client):
        body = {
            "class": "NewAttachmentRequestBody",
            "properties": {
                "class": "ActivityEntryProperties",
                "qualifiedName": f"TestActivity-{datetime.now().isoformat()}",
                "displayName": "A new Test Activity",
                "situation": "Testing activity logging",
                "description": "This is a test notification",
            }
        }
        response = profile_client.log_my_activity(body=body)
        show("Logged activity GUID", response)
        assert isinstance(response, str) and response

    def test_get_my_entries(self, profile_client):
        response = profile_client.get_my_entries()
        show("Retrieved entries", response)
        assert isinstance(response, list)

    # --- To-dos and actions (created and deleted by each test) ---

    def test_get_my_to_dos_includes_new_todo(self, profile_client, todo_guid):
        response = profile_client.get_my_to_dos(output_format="JSON", report_spec="My-User-ToDos")
        assert todo_guid in guids(response)

    def test_get_todo_by_guid(self, profile_client, todo_guid):
        todo = profile_client.get_asset_by_guid(todo_guid, graph_query_depth=0)
        assert todo["elementHeader"]["type"]["typeName"] == "ToDo"
        assert todo["properties"]["activityStatus"] == "REQUESTED"
        assert todo["properties"]["priority"] == 3

    def test_update_todo_status(self, profile_client, todo_guid):
        profile_client.update_asset(todo_guid, {
            "class": "UpdateElementRequestBody",
            "mergeUpdate": True,
            "properties": {"class": "ToDoProperties", "activityStatus": "WAITING", "priority": 1},
        })
        todo = profile_client.get_asset_by_guid(todo_guid, graph_query_depth=0)
        assert todo["properties"]["activityStatus"] == "WAITING"
        assert todo["properties"]["priority"] == 1

    def test_new_todo_is_assigned_to_and_requested_by_me(self, profile_client, profile_guid, todo_guid):
        # create_my_todo makes the user's profile both the assignee and the originator
        assigned = profile_client.get_assigned_actions(profile_guid, activity_status_list=OPEN_STATUSES)
        requested = profile_client.get_actions_for_requester(profile_guid, activity_status_list=OPEN_STATUSES)
        assert todo_guid in guids(assigned)
        assert todo_guid in guids(requested)

    def test_get_actions_for_sponsor(self, profile_client, profile_guid):
        action_guid = profile_client.create_action({
            "class": "ActionRequestBody",
            "isOwnAnchor": True,
            "properties": {
                "class": "ToDoProperties",
                "qualifiedName": f"Todo::sponsored-test-{datetime.now().isoformat()}",
                "displayName": "Sponsored functional test to-do",
                "activityStatus": "REQUESTED",
            },
            "actionSponsorGUID": profile_guid,
        })
        try:
            sponsored = profile_client.get_actions_for_sponsor(profile_guid, activity_status_list=OPEN_STATUSES)
            assert action_guid in guids(sponsored)
        finally:
            profile_client.delete_asset(action_guid)

    def test_deleted_todo_is_gone(self, profile_client):
        guid = profile_client.create_my_todo(f"test-todo-{datetime.now().isoformat()}", "REQUESTED")
        profile_client.delete_asset(guid)
        response = profile_client.get_my_to_dos(output_format="JSON")
        assert guid not in guids(response)


if __name__ == "__main__":
    pytest.main([__file__])
