"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module tests the ActorManager class and methods from actor_manager.py

A running Egeria environment is needed to run these tests.

"""
import json
import time
from datetime import datetime

from rich import print, print_json
from rich.console import Console

from pyegeria.actor_manager import ActorManager
from pyegeria._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaConnectionException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
    PyegeriaUnauthorizedException,
    print_basic_exception,
    print_exception_table,
    print_validation_error,
)
from pyegeria.logging_configuration import config_logging, init_logging
from pyegeria.models import (NewElementRequestBody, UpdateElementRequestBody, DeleteElementRequestBody)
from pyegeria.actor_manager import ActorManager
from pydantic import ValidationError

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


class TestActorManager:
    good_platform1_url = PLATFORM_URL

    good_user_1 = USER_ID
    good_user_2 = "peterprofile"
    good_server_1 = VIEW_SERVER
    good_server_2 = VIEW_SERVER
    good_view_server_1 = VIEW_SERVER
    good_view_server_2 = VIEW_SERVER

    def _unique_qname(self, prefix: str = "ActorProfile") -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}::{ts}"

    def test_create_actor_profile(self):
        """Test creating a basic actor profile with dict body"""
        actor_client = None
        try:
            actor_client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = actor_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            display_name = f"Test Actor Profile {datetime.now().strftime('%Y%m%d%H%M%S')}"
            description = "Test actor profile for automated testing"
            qualified_name = self._unique_qname("TestActorProfile")

            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "qualifiedName": qualified_name,
                    "displayName": display_name,
                    "description": description,
                }
            }

            response = actor_client.create_actor_profile(body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nCreated actor profile with GUID: {response}")
            assert type(response) is str
            assert len(response) > 0

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if actor_client:
                actor_client.close_session()

    def test_create_actor_profile_w_pyd(self):
        """Test creating an actor profile with Pydantic model"""
        actor_client = None
        try:
            actor_client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = actor_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            q_name = self._unique_qname("TestActorProfilePyd")
            body = NewElementRequestBody(
                class_="NewElementRequestBody",
                is_own_anchor=True,
                properties={
                    "class": "ActorProfileProperties",
                    "qualifiedName": q_name,
                    "displayName": f"Pydantic Actor Profile {datetime.now().strftime('%H%M%S')}",
                    "description": "Actor profile created with Pydantic model",
                }
            )

            validated_body = body.model_dump(mode='json', by_alias=True, exclude_none=True)
            response = actor_client.create_actor_profile(validated_body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nCreated actor profile with GUID: {response}")
            assert type(response) is str
            assert len(response) > 0

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if actor_client:
                actor_client.close_session()

    def test_find_actor_profiles(self):
        """Test finding actor profiles with search string"""
        actor_client = None
        try:
            actor_client = ActorManager(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = actor_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            search_string = "*"
            response = actor_client.find_actor_profiles(
                search_string,
                output_format="DICT"
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Found {len(response)} actor profiles")
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nResponse: " + response)
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if actor_client:
                actor_client.close_session()

    def test_get_actor_profiles_by_name(self):
        """Test getting actor profiles by name"""
        actor_client = None
        try:
            actor_client = ActorManager(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = actor_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            name = "Test Actor Profile"
            response = actor_client.get_actor_profiles_by_name(name)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Found {len(response)} actor profiles")
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nResponse: " + response)
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if actor_client:
                actor_client.close_session()

    def test_get_actor_profile_by_guid(self):
        """Test getting a specific actor profile by GUID"""
        actor_client = None
        try:
            actor_client = ActorManager(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = actor_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # First create an actor profile to retrieve
            q_name = self._unique_qname("TestActorProfileForRetrieval")
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "qualifiedName": q_name,
                    "displayName": "Actor Profile for GUID test",
                    "description": "Test actor profile to retrieve by GUID",
                }
            }
            profile_guid = actor_client.create_actor_profile(body)
            print(f"\n\nCreated actor profile with GUID: {profile_guid}")

            # Now retrieve it
            response = actor_client.get_actor_profile_by_guid(
                profile_guid,
                output_format="DICT"
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if isinstance(response, (list, dict)):
                print("\n\n" + json.dumps(response, indent=4))
            elif type(response) is str:
                print("\n\nResponse: " + response)
            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if actor_client:
                actor_client.close_session()

    def test_update_actor_profile(self):
        """Test updating an actor profile's properties"""
        actor_client = None
        try:
            actor_client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = actor_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # First create an actor profile to update
            q_name = self._unique_qname("TestActorProfileForUpdate")
            create_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "qualifiedName": q_name,
                    "displayName": "Original Actor Profile Name",
                    "description": "Original description",
                }
            }
            profile_guid = actor_client.create_actor_profile(create_body)
            print(f"\n\nCreated actor profile with GUID: {profile_guid}")

            # Now update it
            new_desc = "Updated description for testing"
            update_body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "qualifiedName": q_name,
                    "displayName": "Updated Actor Profile Name",
                    "description": new_desc,
                }
            }

            response = actor_client.update_actor_profile(profile_guid, update_body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nUpdated actor profile successfully")

            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if actor_client:
                actor_client.close_session()

    def test_delete_actor_profile(self):
        """Test deleting an actor profile"""
        actor_client = None
        try:
            actor_client = ActorManager(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = actor_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # Create an actor profile to delete
            q_name = self._unique_qname("ActorProfileToDelete")
            create_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "qualifiedName": q_name,
                    "displayName": "Actor Profile to Delete",
                    "description": "This actor profile will be deleted",
                }
            }
            profile_guid = actor_client.create_actor_profile(create_body)
            print(f"\n\nCreated actor profile with GUID: {profile_guid}")

            # Delete it
            response = actor_client.delete_actor_profile(profile_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nDeleted actor profile successfully")

            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if actor_client:
                actor_client.close_session()

    def test_crud_actor_profile_e2e(self):
        """End-to-end test: Create, Read, Update, Delete an actor profile"""
        actor_client = None
        try:
            actor_client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            created_guid = None
            display_name = f"E2E Test Actor Profile {datetime.now().strftime('%Y%m%d%H%M%S')}"

            token = actor_client.create_egeria_bearer_token(self.good_user_2, "secret")

            # CREATE
            print("\n\n=== CREATE ===")
            q_name = self._unique_qname("E2EActorProfile")
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "qualifiedName": q_name,
                    "displayName": display_name,
                    "description": "End-to-end test actor profile",
                }
            }

            create_resp = actor_client.create_actor_profile(body)
            created_guid = create_resp
            print(f"Created actor profile: {created_guid}")
            assert created_guid is not None

            # READ
            print("\n\n=== READ ===")
            got = actor_client.get_actor_profile_by_guid(created_guid, output_format="JSON")
            print_json(json.dumps(got, indent=4))
            assert got is not None

            # UPDATE
            print("\n\n=== UPDATE ===")
            new_desc = "Updated description in E2E test"
            upd_body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "qualifiedName": q_name,
                    "displayName": display_name,
                    "description": new_desc,
                }
            }

            upd_resp = actor_client.update_actor_profile(created_guid, upd_body)
            print("Updated actor profile successfully")

            # Verify update
            found = actor_client.get_actor_profile_by_guid(created_guid, output_format="JSON")
            print_json(json.dumps(found, indent=4))

            # DELETE
            print("\n\n=== DELETE ===")
            del_resp = actor_client.delete_actor_profile(created_guid)
            print("Deleted actor profile successfully")

            # Verify deletion
            try:
                after = actor_client.get_actor_profile_by_guid(created_guid, output_format="JSON")
                # If we get here, deletion might not have worked
                print("Warning: Actor profile still exists after deletion")
            except PyegeriaAPIException:
                print("Confirmed: Actor profile no longer exists")

            assert True

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if actor_client:
                actor_client.close_session()

    # Actor Role Tests
    def test_create_actor_role(self):
        """Test creating a basic actor role with dict body"""
        actor_client = None
        try:
            actor_client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = actor_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            display_name = f"Test Actor Role {datetime.now().strftime('%Y%m%d%H%M%S')}"
            description = "Test actor role for automated testing"
            qualified_name = self._unique_qname("TestActorRole")

            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorRoleProperties",
                    "qualifiedName": qualified_name,
                    "displayName": display_name,
                    "description": description,
                }
            }

            response = actor_client.create_actor_role(body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nCreated actor role with GUID: {response}")
            assert type(response) is str
            assert len(response) > 0

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if actor_client:
                actor_client.close_session()

    # User Identity Tests
    def test_create_user_identity(self):
        """Test creating a basic user identity with dict body"""
        actor_client = None
        try:
            actor_client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = actor_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            qualified_name = self._unique_qname("TestUserIdentity")
            user_id = f"testuser{datetime.now().strftime('%H%M%S')}"

            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "UserIdentityProperties",
                    "qualifiedName": qualified_name,
                    "userId": user_id,
                }
            }

            response = actor_client.create_user_identity(body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nCreated user identity with GUID: {response}")
            assert type(response) is str
            assert len(response) > 0

        except (
                PyegeriaInvalidParameterException,
                PyegeriaAPIException,
                PyegeriaUnauthorizedException,
                PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            if actor_client:
                actor_client.close_session()
