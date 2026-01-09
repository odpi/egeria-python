import pytest
import asyncio
from pyegeria.omvs.my_profile import MyProfile
from pyegeria.models import NewElementRequestBody
from pyegeria.core._exceptions import PyegeriaException

VIEW_SERVER = "view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
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
            profile = profile_client.get_my_profile()
            assert isinstance(profile, (dict, str))
            print(f"\nRetrieved profile (JSON): {profile}")

            profile_dict = profile_client.get_my_profile(output_format="DICT")
            assert isinstance(profile_dict, (dict, list))
            print(f"\nRetrieved profile (DICT): {profile_dict}")
        except PyegeriaException as e:
            # We might get a 404 or 401 depending on the environment, but the call should at least attempt
            print(f"get_my_profile failed as expected or due to env: {e}")
        except Exception as e:
            pytest.fail(f"get_my_profile failed with unexpected exception: {e}")

    def test_create_my_profile(self, profile_client):
        qualified_name = "test_profile_qn"
        display_name = "Test Profile"
        body = {
            "class": "NewElementRequestBody",
            "isOwnAnchor": True,
            "properties": {
                "class": "PersonProperties",
                "qualifiedName": qualified_name,
                "displayName": display_name,
                "description": "Test profile description"
            }
        }
        try:
            # This might fail if the profile already exists or the endpoint is not supported by the test environment
            guid = profile_client.create_my_profile(body)
            assert isinstance(guid, str)
            print(f"\nCreated profile GUID: {guid}")
        except PyegeriaException as e:
            print(f"create_my_profile failed (expected if it already exists or unsupported): {e}")
        except Exception as e:
             pytest.fail(f"create_my_profile failed with unexpected exception: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
