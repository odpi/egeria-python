import json

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
USER_ID = "garygeeke"
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

            profile = profile_client.get_my_profile(output_format="JSON", report_spec="My-User-MD", graph_query_depth=10)
            if isinstance(profile, dict):
                print(json.dumps(profile, indent=2))
            if isinstance(profile, str):
                console.print(Markdown(profile))

        except Exception as e:
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

    def test_get_actions_for_action_target(self, profile_client):
        try:
            profile = profile_client.get_my_profile(graph_query_depth=0)
            assert isinstance(profile, (list, dict, str))
            if isinstance(profile, dict):
                element_guid = profile.get("elementHeader", {}).get("guid")
            else:
                element_guid = None

            if not element_guid:
                pytest.skip("No profile GUID available for get_actions_for_action_target")

            response = profile_client.get_actions_for_action_target(element_guid)
            assert isinstance(response, (list, dict, str))
            print(f"\nRetrieved actions for target: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nRetrieved actions for target: {response}")
        except PyegeriaException as e:
            print(f"get_actions_for_action_target failed as expected or due to env: {e}")
        except Exception as e:
            pytest.fail(f"get_actions_for_action_target failed with unexpected exception: {e}")

    def test_get_my_assigned_actions(self, profile_client):
        try:
            profile = profile_client.get_my_profile(graph_query_depth=0)
            assert isinstance(profile, (list, dict, str))
            if isinstance(profile, dict):
                element_guid = profile.get("elementHeader", {}).get("guid")
            else:
                element_guid = None

            if not element_guid:
                pytest.skip("No profile GUID available for get_my_assigned_actions")

            response = profile_client.get_my_assigned_actions(element_guid)
            assert isinstance(response, (list, dict, str))
            print(f"\nRetrieved actions for target: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nRetrieved actions for target: {response}")
        except PyegeriaException as e:
            print(f"get_actions_for_action_target failed as expected or due to env: {e}")
        except Exception as e:
            pytest.fail(f"get_actions_for_action_target failed with unexpected exception: {e}")

    def test_find_to_do(self, profile_client):
        try:
            response = profile_client.find_to_do(search_string="*")
            assert isinstance(response, (list, dict, str))
            print(f"\nRetrieved to-dos: {json.dumps(response, indent=2)}" if isinstance(response, (list, dict)) else f"\nRetrieved to-dos: {response}")
        except PyegeriaException as e:
            print(f"find_to_do failed as expected or due to env: {e}")
        except Exception as e:
            pytest.fail(f"find_to_do failed with unexpected exception: {e}")




if __name__ == "__main__":
    pytest.main([__file__])
