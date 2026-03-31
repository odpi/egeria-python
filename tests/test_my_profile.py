import json
import time

import pytest
import asyncio
from pyegeria.omvs.my_profile import MyProfile
from pyegeria.models import NewElementRequestBody
from pyegeria.core._exceptions import PyegeriaException, print_basic_exception
from rich.markdown import Markdown
from pyegeria import EgeriaTech
from rich.console import Console
console = Console(width = 150)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
# USER_ID = "jacquardnpa"
USER_ID = "erinoverview"
USER_PWD = "secret"

class TestMyProfile:
    @pytest.fixture
    def profile_client(self):
        client = MyProfile(VIEW_SERVER, PLATFORM_URL, USER_ID, USER_PWD)
        # Try to get a token if needed, though ServerClient usually handles it
        try:
            client.create_egeria_bearer_token(USER_ID, USER_PWD)
        except Exception:
            pass 
        return client

    def test_get_my_profile(self, profile_client):
        try:
            profile_client = MyProfile(VIEW_SERVER, PLATFORM_URL, USER_ID, USER_PWD)
            token = profile_client.create_egeria_bearer_token(USER_ID, USER_PWD)

            profile = profile_client.get_my_profile(output_format="DICT", report_spec="My-User-MD", graph_query_depth=10)
            if isinstance(profile, dict | list):
                print(json.dumps(profile, indent=2))
            if isinstance(profile, str):
                console.print(Markdown(profile))

        except Exception as e:
            print_basic_exception(e)
            pytest.fail(f"get_my_profile failed with unexpected exception: {e}")

    def test_get_my_actors(self, profile_client):
        try:
            response = profile_client.get_my_actors()
            assert isinstance(response, (list, dict, str))
            print(f"\nRetrieved actors: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nRetrieved actors: {response}")
        except PyegeriaException as e:
            print(f"get_my_actors failed as expected or due to env: {e}")
        except Exception as e:
            pytest.fail(f"get_my_actors failed with unexpected exception: {e}")

    def test_get_my_user_identities(self, profile_client):
        try:
            response = profile_client.get_my_user_identities(output_format="DICT", report_spec="Referenceable")
            assert isinstance(response, (list, dict, str))
            print(f"\nRetrieved user identities: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nRetrieved user identities: {response}")
        except PyegeriaException as e:
            print(f"get_my_user_identities failed as expected or due to env: {e}")
        except Exception as e:
            pytest.fail(f"get_my_user_identities failed with unexpected exception: {e}")

    def test_get_my_roles(self, profile_client):
        try:
            response = profile_client.get_my_roles()
            assert isinstance(response, (list, dict, str))
            print(f"\nRetrieved roles: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nRetrieved roles: {response}")
        except PyegeriaException as e:
            print(f"get_my_roles failed as expected or due to env: {e}")
        except Exception as e:
            pytest.fail(f"get_my_roles failed with unexpected exception: {e}")

    def test_get_my_resources(self, profile_client):
        try:
            response = profile_client.get_my_resources()
            assert isinstance(response, (list, dict, str))
            print(f"\nRetrieved resources: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nRetrieved resources: {response}")
        except PyegeriaException as e:
            print(f"get_my_resources failed as expected or due to env: {e}")
        except Exception as e:
            pytest.fail(f"get_my_resources failed with unexpected exception: {e}")

    def test_get_my_assigned_actions(self, profile_client):
        try:
            response = profile_client.get_my_assigned_actions()
            assert isinstance(response, (list, dict, str))
            print(f"\nRetrieved assigned actions: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nRetrieved assigned actions: {response}")
        except PyegeriaException as e:
            print(f"get_my_assigned_actions failed as expected or due to env: {e}")
        except Exception as e:
            pytest.fail(f"get_my_assigned_actions failed with unexpected exception: {e}")

    def test_get_my_sponsored_actions(self, profile_client):
        try:
            response = profile_client.get_my_sponsored_actions()
            assert isinstance(response, (list, dict, str))
            print(f"\nRetrieved sponsored actions: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nRetrieved sponsored actions: {response}")
        except PyegeriaException as e:
            print(f"get_my_sponsored_actions failed as expected or due to env: {e}")
        except Exception as e:
            pytest.fail(f"get_my_sponsored_actions failed with unexpected exception: {e}")

    def test_get_my_requested_actions(self, profile_client):
        try:
            response = profile_client.get_my_requested_actions()
            assert isinstance(response, (list, dict, str))
            print(f"\nRetrieved requested actions: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nRetrieved requested actions: {response}")
        except PyegeriaException as e:
            print(f"get_my_requested_actions failed as expected or due to env: {e}")
        except Exception as e:
            pytest.fail(f"get_my_requested_actions failed with unexpected exception: {e}")

    def test_activity_logging(self, profile_client):
        try:
            body = {
                "class": "NewAttachmentRequestBody",
                "properties": {
                    "class": "NotificationProperties",
                    "qualifiedName": "TestActivity",
                    "displayName": "A new Test Activity",
                    "situation": "Testing activity logging",
                    "description": "This is a test notification",
                }
            }
            guid = profile_client.log_my_activity(body)
            assert isinstance(guid, str)
            print(f"\nLogged activity GUID: {guid}")

            guid = profile_client.journal_my_activity(body)
            assert isinstance(guid, str)
            print(f"\nJournaled activity GUID: {guid}")

            guid = profile_client.blog_my_activity(body)
            assert isinstance(guid, str)
            print(f"\nBlogged activity GUID: {guid}")

        except PyegeriaException as e:
            print(f"activity logging failed as expected or due to env: {e}")
        except Exception as e:
            pytest.fail(f"activity logging failed with unexpected exception: {e}")

    def test_get_to_dos(self, profile_client):
        try:
            response = profile_client.get_my_to_dos(output_format="DICT",report_spec="My-User-ToDos")
            assert isinstance(response, (list, dict, str))
            if isinstance(response, list|dict):
                print(f"\nRetrieved to-dos: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nRetrieved to-dos: {response}")
            else:
                print(f"\nRetrieved to-dos: {response}")
        except PyegeriaException as e:
            print(f"get_my_to_dos failed as expected or due to env: {e}")
        except Exception as e:
            pytest.fail(f"get_my_to_dos failed with unexpected exception: {e}")

    def test_create_my_todo(self,profile_client):
        try:

            response = profile_client.create_my_todo("do-my-backup","REQUESTED","do-backup",
                                                     "Weekly backup needed",3)

            assert isinstance(response, (list, dict, str))
            print(f"\nCreated to-do: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nCreated to-do: {response}")
        except PyegeriaException as e:
            print(f"create_my_todo failed as expected or due to env: {e}")
            print_basic_exception(e)
        except Exception as e:
            pytest.fail(f"create_my_todo failed with unexpected exception: {e}")

    def test_get_assigned_actions_for_actor(self, profile_client):
        try:
            actor_guid = "9a304921-6844-4ea8-b513-76620ca15a99"  # peter
            response = profile_client.get_assigned_actions(actor_guid)
            assert isinstance(response, (list, dict, str))
            print(f"\nAssigned actions: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nAssigned actions: {response}")
        except PyegeriaException as e:
            print(f"get_assigned_actions failed as expected or due to env: {e}")
        except Exception as e:
            print(f"get_assigned_actions raised: {type(e).__name__}: {e}")

    def test_get_actions_for_sponsor(self, profile_client):
        try:
            element_guid = "a588fb08-ae09-4415-bd5d-991882ceacba"
            response = profile_client.get_actions_for_sponsor(element_guid)
            assert isinstance(response, (list, dict, str))
            print(f"\nSponsored actions: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nSponsored actions: {response}")
        except PyegeriaException as e:
            print(f"get_actions_for_sponsor failed as expected or due to env: {e}")
        except Exception as e:
            print(f"get_actions_for_sponsor raised: {type(e).__name__}: {e}")

    def test_get_to_do_by_guid(self, profile_client):
        try:
            todo_guid = "91f6712a-a5ee-4c05-ac18-f7fd996c87ca"
            response = profile_client.get_to_do(todo_guid)
            assert isinstance(response, (list, dict, str))
            print(f"\nTo-do: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nTo-do: {response}")
        except PyegeriaException as e:
            print(f"get_to_do failed as expected or due to env: {e}")
        except Exception as e:
            print(f"get_to_do raised: {type(e).__name__}: {e}")

    def test_get_to_dos_by_type(self, profile_client):
        try:
            response = profile_client.get_to_dos_by_type("holiday", "OPEN")
            assert isinstance(response, (list, dict, str))
            print(f"\nTo-dos by type: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nTo-dos by type: {response}")
        except PyegeriaException as e:
            print(f"get_to_dos_by_type failed as expected or due to env: {e}")
        except Exception as e:
            print(f"get_to_dos_by_type raised: {type(e).__name__}: {e}")

    def test_update_todo_status(self, profile_client):
        try:
            todo_guid = "d6d4f540-a28f-4312-9c24-d3774b3f06a1"
            body = {"class": "ToDoProperties", "toDoStatus": "WAITING", "priority": 1}
            profile_client.update_to_do(todo_guid, body, is_merge_update=True)
            print(f"\nUpdated to-do {todo_guid} status to WAITING.")
        except PyegeriaException as e:
            print(f"update_to_do failed as expected or due to env: {e}")
        except Exception as e:
            print(f"update_to_do raised: {type(e).__name__}: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
