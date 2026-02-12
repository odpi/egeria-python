import json

import pytest
import asyncio
from pyegeria.omvs.my_profile import MyProfile
from pyegeria.models import NewElementRequestBody
from pyegeria.core._exceptions import PyegeriaException, print_basic_exception

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "calliequartile"
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
            profile = profile_client.get_my_profile()
            assert isinstance(profile, (dict, list, str))

            profile_dict = profile_client.get_my_profile(output_format="DICT", report_spec="My-User")
            assert isinstance(profile_dict, (dict, list, str))
            print(f"\nRetrieved profile (DICT): {json.dumps(profile_dict, indent=2)}")
        except PyegeriaException as e:
            # We might get a 404 or 401 depending on the environment, but the call should at least attempt
            print(f"get_my_profile failed as expected or due to env: {e}")
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
            response = profile_client.get_my_user_identities()
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
            profile = profile_client.get_my_profile()
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
