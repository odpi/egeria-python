"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


Functional tests for the ActorManager class.

These tests require a running Egeria environment (view server) and mirror the
style used by other functional tests (e.g., test_collection_manager_omvs.py).
They perform end-to-end scenarios for create/update/find/get/delete of:
- Actor Profiles
- Actor Roles
- User Identities

Additionally, a simple relationship scenario is included to link and detach a
User Identity to/from an Actor Profile.
"""

import json
import time
from datetime import datetime

from loguru import logger
from pydantic import ValidationError

from pyegeria.actor_manager import ActorManager
from pyegeria._exceptions_new import (
    PyegeriaInvalidParameterException,
    PyegeriaException,
    PyegeriaConnectionException,
    PyegeriaClientException,
    PyegeriaAPIException,
    PyegeriaUnknownException,
    PyegeriaNotFoundException,
    PyegeriaUnauthorizedException,
    print_basic_exception,
    print_validation_error,
)
from pyegeria.logging_configuration import config_logging, init_logging


# Align logging/init style with other tests
config_logging()
init_logging(True)


VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


def _unique_qname(prefix: str) -> str:
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}::{ts}"


class TestActorManager:
    good_platform1_url = PLATFORM_URL
    good_view_server_1 = VIEW_SERVER
    good_user_1 = USER_ID

    # -----------------------------
    # Actor Profile end-to-end
    # -----------------------------
    def test_actor_profile_scenario(self):
        client = None
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            token = client.create_egeria_bearer_token(self.good_user_1, USER_PWD)

            qualified_name = _unique_qname("ActorProfile")

            # Create
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "typeName": "ActorProfile",
                    "qualifiedName": qualified_name,
                    "displayName": qualified_name.split("::")[0],
                    "description": "Functional test profile",
                },
            }
            guid = client.create_actor_profile(body)
            print(f"Created ActorProfile GUID: {guid}")
            assert isinstance(guid, str) and len(guid) > 0

            # Update
            update_body = {
                "class": "UpdateElementRequestBody",
                "isMergeUpdate": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "description": "Updated functional test profile",
                },
            }
            client.update_actor_profile(guid, update_body)

            # Find (search)
            res = client.find_actor_profiles(search_string=qualified_name, output_format="DICT")
            print("find_actor_profiles result (DICT):")
            try:
                print(json.dumps(res, indent=4, default=str))
            except Exception:
                print(str(res))
            assert res is not None

            # Get by name (filter)
            get_by_name = client.get_actor_profiles_by_name(filter_string=qualified_name, output_format="DICT")
            print("get_actor_profiles_by_name result (DICT):")
            try:
                print(json.dumps(get_by_name, indent=4, default=str))
            except Exception:
                print(str(get_by_name))
            assert get_by_name is not None

            # Get by GUID
            got = client.get_actor_profile_by_guid(guid, output_format="DICT")
            print("get_actor_profile_by_guid result (DICT):")
            try:
                print(json.dumps(got, indent=4, default=str))
            except Exception:
                print(str(got))
            assert got is not None

            # Relationship scenario: create a user identity and link to this profile, then detach
            uid_qn = _unique_qname("UserIdentity")
            uid_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "UserIdentityProperties",
                    "typeName": "UserIdentity",
                    "qualifiedName": uid_qn,
                    "userId": uid_qn[-8:],
                },
            }
            user_identity_guid = client.create_user_identity(uid_body)
            print(f"Created UserIdentity GUID: {user_identity_guid}")
            assert isinstance(user_identity_guid, str) and len(user_identity_guid) > 0

            # Link identity to actor profile
            # client.link_identity_to_profile(user_identity_guid, guid)

            # Detach identity from actor profile
            # client.detach_identity_from_profile(user_identity_guid, guid)

            # Delete child entity first (user identity), then the profile
            client.delete_user_identity(user_identity_guid, cascade=True)
            client.delete_actor_profile(guid, cascade=True)

            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaConnectionException,
            PyegeriaClientException,
            PyegeriaAPIException,
            PyegeriaUnknownException,
            PyegeriaNotFoundException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_basic_exception(e)
            assert False, "Actor Profile scenario failed"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error in Actor Profile scenario"
        finally:
            if client:
                client.close_session()

    # -----------------------------
    # Actor Role end-to-end
    # -----------------------------
    def test_actor_role_scenario(self):
        client = None
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            token = client.create_egeria_bearer_token(self.good_user_1, USER_PWD)

            qualified_name = _unique_qname("ActorRole")

            # Create
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorRoleProperties",
                    "typeName": "ActorRole",
                    "qualifiedName": qualified_name,
                    "displayName": qualified_name.split("::")[0],
                    "description": "Functional test role",
                    "scope": "Test scope",
                },
            }
            guid = client.create_actor_role(body)
            print(f"Created ActorRole GUID: {guid}")
            assert isinstance(guid, str) and len(guid) > 0

            # Update
            update_body = {
                "class": "UpdateElementRequestBody",
                "isMergeUpdate": True,
                "properties": {
                    "class": "ActorRoleProperties",
                    "description": "Updated functional test role",
                },
            }
            client.update_actor_role(guid, update_body)

            # Find
            res = client.find_actor_roles(search_string=qualified_name, output_format="DICT")
            print("find_actor_roles result (DICT):")
            try:
                print(json.dumps(res, indent=4, default=str))
            except Exception:
                print(str(res))
            assert res is not None

            # Get by name
            get_by_name = client.get_actor_roles_by_name(filter_string=qualified_name, output_format="DICT")
            print("get_actor_roles_by_name result (DICT):")
            try:
                print(json.dumps(get_by_name, indent=4, default=str))
            except Exception:
                print(str(get_by_name))
            assert get_by_name is not None

            # Get by GUID
            got = client.get_actor_role_by_guid(guid, output_format="DICT")
            print("get_actor_role_by_guid result (DICT):")
            try:
                print(json.dumps(got, indent=4, default=str))
            except Exception:
                print(str(got))
            assert got is not None

            # Delete
            client.delete_actor_role(guid, cascade=True)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaConnectionException,
            PyegeriaClientException,
            PyegeriaAPIException,
            PyegeriaUnknownException,
            PyegeriaNotFoundException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_basic_exception(e)
            assert False, "Actor Role scenario failed"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error in Actor Role scenario"
        finally:
            if client:
                client.close_session()

    # -----------------------------
    # User Identity end-to-end
    # -----------------------------
    def test_user_identity_scenario(self):
        client = None
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            token = client.create_egeria_bearer_token(self.good_user_1, USER_PWD)

            qualified_name = _unique_qname("UserIdentity")

            # Create
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "UserIdentityProperties",
                    "typeName": "UserIdentity",
                    "qualifiedName": qualified_name,
                    "userId": qualified_name[-8:],
                },
            }
            guid = client.create_user_identity(body)
            print(f"Created UserIdentity GUID: {guid}")
            assert isinstance(guid, str) and len(guid) > 0

            # Update
            update_body = {
                "class": "UpdateElementRequestBody",
                "isMergeUpdate": True,
                "properties": {
                    "class": "UserIdentityProperties",
                    "distinguishedName": f"CN={qualified_name}",
                },
            }
            client.update_user_identity(guid, update_body)

            # Find
            res = client.find_user_identities(search_string=qualified_name, output_format="DICT")
            print("find_user_identities result (DICT):")
            try:
                print(json.dumps(res, indent=4, default=str))
            except Exception:
                print(str(res))
            assert res is not None

            # Get by name
            get_by_name = client.get_user_identities_by_name(filter_string=qualified_name, output_format="DICT")
            print("get_user_identities_by_name result (DICT):")
            try:
                print(json.dumps(get_by_name, indent=4, default=str))
            except Exception:
                print(str(get_by_name))
            assert get_by_name is not None

            # Get by GUID
            got = client.get_user_identity_by_guid(guid, output_format="DICT")
            print("get_user_identity_by_guid result (DICT):")
            try:
                print(json.dumps(got, indent=4, default=str))
            except Exception:
                print(str(got))
            assert got is not None

            # Delete
            client.delete_user_identity(guid, cascade=True)
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaConnectionException,
            PyegeriaClientException,
            PyegeriaAPIException,
            PyegeriaUnknownException,
            PyegeriaNotFoundException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_basic_exception(e)
            assert False, "User Identity scenario failed"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error in User Identity scenario"
        finally:
            if client:
                client.close_session()

    # -----------------------------
    # Individual method tests: Actor Profile
    # -----------------------------
    def test_create_actor_profile(self):
        client = None
        guid = None
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            qn = _unique_qname("ActorProfile")
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "typeName": "ActorProfile",
                    "displayName": "Puddy",
                    "qualifiedName": "ActorProfile::Puddy"
                },
            }
            guid = client.create_actor_profile(body)
            assert isinstance(guid, str) and len(guid) > 0
            if guid:
                print(f"Created ActorProfile with GUID: {guid}")
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "create_actor_profile failed"
        finally:
            try:
                if client and guid:
                    client.delete_actor_profile(guid, cascade=True)
            finally:
                if client:
                    client.close_session()

    def test_update_actor_profile(self):
        client = None
        guid = None
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            qn = _unique_qname("ActorProfile")
            guid = client.create_actor_profile({
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "typeName": "ActorProfile",
                    "qualifiedName": qn,
                },
            })
            update_body = {
                "class": "UpdateElementRequestBody",
                "isMergeUpdate": True,
                "properties": {"class": "ActorProfileProperties", "description": "updated"},
            }
            client.update_actor_profile(guid, update_body)
            got = client.get_actor_profile_by_guid(guid, output_format="DICT")
            print("get_actor_profile_by_guid result (DICT):")
            try:
                print(json.dumps(got, indent=4, default=str))
            except Exception:
                print(str(got))
            assert got is not None
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "update_actor_profile failed"
        finally:
            try:
                if client and guid:
                    client.delete_actor_profile(guid, cascade=True)
            finally:
                if client:
                    client.close_session()

    def test_find_actor_profiles(self):
        client = None
        guid = None
        qn = _unique_qname("ActorProfile")
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            # guid = client.create_actor_profile({
            #     "class": "NewElementRequestBody",
            #     "isOwnAnchor": True,
            #     "properties": {
            #         "class": "ActorProfileProperties",
            #         "typeName": "ActorProfile",
            #         "qualifiedName": qn,
            #     },
            # })
            res = client.find_actor_profiles( metadata_element_types=['Person','Team'],output_format="DICT", report_spec="Actor-Profiles")
            print("find_actor_profiles result (DICT):")
            try:
                print(json.dumps(res, indent=4, default=str))
            except Exception:
                print(str(res))
            assert res is not None
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "find_actor_profiles failed"
        finally:
            try:
                if client and guid:
                    client.delete_actor_profile(guid, cascade=True)
            finally:
                if client:
                    client.close_session()

    def test_get_actor_profiles_by_name(self):
        client = None
        guid = None
        qn = _unique_qname("ActorProfile")
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            guid = client.create_actor_profile({
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "typeName": "ActorProfile",
                    "qualifiedName": qn,
                },
            })
            res = client.get_actor_profiles_by_name(filter_string=qn, output_format="DICT")
            print("get_actor_profiles_by_name result (DICT):")
            try:
                print(json.dumps(res, indent=4, default=str))
            except Exception:
                print(str(res))
            assert res is not None
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "get_actor_profiles_by_name failed"
        finally:
            try:
                if client and guid:
                    client.delete_actor_profile(guid, cascade=True)
            finally:
                if client:
                    client.close_session()

    def test_get_actor_profile_by_guid(self):
        client = None
        guid = "22eca01b-fbab-476b-a2ff-266399f3ac0a"
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            qn = _unique_qname("ActorProfile")
            guid = client.create_actor_profile({
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "typeName": "ActorProfile",
                    "qualifiedName": qn,
                },
            })
            got = client.get_actor_profile_by_guid(guid, output_format="DICT")
            print("get_actor_profile_by_guid result (DICT):")
            try:
                print(json.dumps(got, indent=4, default=str))
            except Exception:
                print(str(got))
            assert got is not None
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "get_actor_profile_by_guid failed"
        finally:
            try:
                if client and guid:
                    client.delete_actor_profile(guid, cascade=True)
            finally:
                if client:
                    client.close_session()

    def test_delete_actor_profile(self):
        client = None
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            qn = _unique_qname("ActorProfile")
            guid = client.create_actor_profile({
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "typeName": "ActorProfile",
                    "qualifiedName": qn,
                },
            })
            client.delete_actor_profile(guid, cascade=True)
            assert True
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "delete_actor_profile failed"
        finally:
            if client:
                client.close_session()

    # -----------------------------
    # Individual method tests: Actor Role
    # -----------------------------
    def test_create_actor_role(self):
        client = None
        guid = None
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            qn = _unique_qname("ActorRole")
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorRoleProperties",
                    "typeName": "ActorRole",
                    "qualifiedName": qn,
                },
            }
            guid = client.create_actor_role(body)
            print(f"Created ActorRole GUID: {guid}")
            assert isinstance(guid, str) and len(guid) > 0
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "create_actor_role failed"
        finally:
            try:
                if client and guid:
                    client.delete_actor_role(guid, cascade=True)
            finally:
                if client:
                    client.close_session()

    def test_update_actor_role(self):
        client = None
        guid = None
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            qn = _unique_qname("ActorRole")
            guid = client.create_actor_role({
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorRoleProperties",
                    "typeName": "ActorRole",
                    "qualifiedName": qn,
                },
            })
            update_body = {
                "class": "UpdateElementRequestBody",
                "isMergeUpdate": True,
                "properties": {"class": "ActorRoleProperties", "description": "updated"},
            }
            client.update_actor_role(guid, update_body)
            got = client.get_actor_role_by_guid(guid, output_format="DICT")
            print("get_actor_role_by_guid result (DICT):")
            try:
                print(json.dumps(got, indent=4, default=str))
            except Exception:
                print(str(got))
            assert got is not None
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "update_actor_role failed"
        finally:
            try:
                if client and guid:
                    client.delete_actor_role(guid, cascade=True)
            finally:
                if client:
                    client.close_session()

    def test_find_actor_roles(self):
        client = None
        guid = None
        qn = _unique_qname("ActorRole")
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            guid = client.create_actor_role({
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorRoleProperties",
                    "typeName": "ActorRole",
                    "qualifiedName": qn,
                },
            })
            res = client.find_actor_roles(search_string=qn, output_format="DICT")
            print("find_actor_roles result (DICT):")
            try:
                print(json.dumps(res, indent=4, default=str))
            except Exception:
                print(str(res))
            assert res is not None
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "find_actor_roles failed"
        finally:
            try:
                if client and guid:
                    client.delete_actor_role(guid, cascade=True)
            finally:
                if client:
                    client.close_session()

    def test_get_actor_roles_by_name(self):
        client = None
        guid = None
        qn = _unique_qname("ActorRole")
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            guid = client.create_actor_role({
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorRoleProperties",
                    "typeName": "ActorRole",
                    "qualifiedName": qn,
                },
            })
            res = client.get_actor_roles_by_name(filter_string=qn, output_format="DICT")
            print("get_actor_roles_by_name result (DICT):")
            try:
                print(json.dumps(res, indent=4, default=str))
            except Exception:
                print(str(res))
            assert res is not None
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "get_actor_roles_by_name failed"
        finally:
            try:
                if client and guid:
                    client.delete_actor_role(guid, cascade=True)
            finally:
                if client:
                    client.close_session()

    def test_get_actor_role_by_guid(self):
        client = None
        guid = None
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            qn = _unique_qname("ActorRole")
            guid = client.create_actor_role({
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorRoleProperties",
                    "typeName": "ActorRole",
                    "qualifiedName": qn,
                },
            })
            got = client.get_actor_role_by_guid(guid, output_format="DICT")
            print("get_actor_role_by_guid result (DICT):")
            try:
                print(json.dumps(got, indent=4, default=str))
            except Exception:
                print(str(got))
            assert got is not None
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "get_actor_role_by_guid failed"
        finally:
            try:
                if client and guid:
                    client.delete_actor_role(guid, cascade=True)
            finally:
                if client:
                    client.close_session()

    def test_delete_actor_role(self):
        client = None
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            qn = _unique_qname("ActorRole")
            guid = client.create_actor_role({
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorRoleProperties",
                    "typeName": "ActorRole",
                    "qualifiedName": qn,
                },
            })
            client.delete_actor_role(guid, cascade=True)
            assert True
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "delete_actor_role failed"
        finally:
            if client:
                client.close_session()

    # -----------------------------
    # Individual method tests: User Identity
    # -----------------------------
    def test_create_user_identity(self):
        client = None
        guid = None
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            qn = _unique_qname("UserIdentity")
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "UserIdentityProperties",
                    "typeName": "UserIdentity",
                    "qualifiedName": qn,
                    "userId": qn[-8:],
                },
            }
            guid = client.create_user_identity(body)
            print(f"Created UserIdentity GUID: {guid}")
            assert isinstance(guid, str) and len(guid) > 0
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "create_user_identity failed"
        finally:
            try:
                if client and guid:
                    client.delete_user_identity(guid, cascade=True)
            finally:
                if client:
                    client.close_session()

    def test_update_user_identity(self):
        client = None
        guid = None
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            qn = _unique_qname("UserIdentity")
            guid = client.create_user_identity({
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "UserIdentityProperties",
                    "typeName": "UserIdentity",
                    "qualifiedName": qn,
                    "userId": qn[-8:],
                },
            })
            update_body = {
                "class": "UpdateElementRequestBody",
                "isMergeUpdate": True,
                "properties": {"class": "UserIdentityProperties", "distinguishedName": f"CN={qn}"},
            }
            client.update_user_identity(guid, update_body)
            got = client.get_user_identity_by_guid(guid, output_format="DICT")
            print("get_user_identity_by_guid result (DICT):")
            try:
                print(json.dumps(got, indent=4, default=str))
            except Exception:
                print(str(got))
            assert got is not None
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "update_user_identity failed"
        finally:
            try:
                if client and guid:
                    client.delete_user_identity(guid, cascade=True)
            finally:
                if client:
                    client.close_session()

    def test_find_user_identities(self):
        client = None
        guid = None
        qn = _unique_qname("UserIdentity")
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            # guid = client.create_user_identity({
            #     "class": "NewElementRequestBody",
            #     "isOwnAnchor": True,
            #     "properties": {
            #         "class": "UserIdentityProperties",
            #         "typeName": "UserIdentity",
            #         "qualifiedName": qn,
            #         "userId": qn[-8:],
            #     },
            # })
            # res = client.find_user_identities(search_string=qn, output_format="DICT")
            res = client.find_user_identities( output_format="DICT", report_spec="User-Identities")
            print("find_user_identities result (DICT):")
            try:
                print(json.dumps(res, indent=4, default=str))
            except Exception:
                print(str(res))
            assert res is not None
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "find_user_identities failed"
        finally:
            try:
                if client and guid:
                    client.delete_user_identity(guid, cascade=True)
            finally:
                if client:
                    client.close_session()

    def test_get_user_identities_by_name(self):
        client = None
        guid = None
        qn = _unique_qname("UserIdentity")
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            guid = client.create_user_identity({
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "UserIdentityProperties",
                    "typeName": "UserIdentity",
                    "qualifiedName": qn,
                    "userId": qn[-8:],
                },
            })
            res = client.get_user_identities_by_name(filter_string=qn, output_format="DICT")
            print("get_user_identities_by_name result (DICT):")
            try:
                print(json.dumps(res, indent=4, default=str))
            except Exception:
                print(str(res))
            assert res is not None
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "get_user_identities_by_name failed"
        finally:
            try:
                if client and guid:
                    client.delete_user_identity(guid, cascade=True)
            finally:
                if client:
                    client.close_session()

    def test_get_user_identity_by_guid(self):
        client = None
        guid = None
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            qn = _unique_qname("UserIdentity")
            guid = client.create_user_identity({
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "UserIdentityProperties",
                    "typeName": "UserIdentity",
                    "qualifiedName": qn,
                    "userId": qn[-8:],
                },
            })
            got = client.get_user_identity_by_guid(guid, output_format="DICT")
            print("get_user_identity_by_guid result (DICT):")
            try:
                print(json.dumps(got, indent=4, default=str))
            except Exception:
                print(str(got))
            assert got is not None
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "get_user_identity_by_guid failed"
        finally:
            try:
                if client and guid:
                    client.delete_user_identity(guid, cascade=True)
            finally:
                if client:
                    client.close_session()

    def test_delete_user_identity(self):
        client = None
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            qn = _unique_qname("UserIdentity")
            guid = client.create_user_identity({
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "UserIdentityProperties",
                    "typeName": "UserIdentity",
                    "qualifiedName": qn,
                    "userId": qn[-8:],
                },
            })
            client.delete_user_identity(guid, cascade=True)
            assert True
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "delete_user_identity failed"
        finally:
            if client:
                client.close_session()

    # -----------------------------
    # Individual method tests: Relationships
    # -----------------------------
    def test_link_and_detach_identity_to_profile(self):
        client = None
        profile_guid = None
        uid_guid = None
        try:
            client = ActorManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            qn_p = _unique_qname("ActorProfile")
            profile_guid = client.create_actor_profile({
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "typeName": "ActorProfile",
                    "qualifiedName": qn_p,
                },
            })
            qn_u = _unique_qname("UserIdentity")
            uid_guid = client.create_user_identity({
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "UserIdentityProperties",
                    "typeName": "UserIdentity",
                    "qualifiedName": qn_u,
                    "userId": qn_u[-8:],
                },
            })
            client.link_identity_to_profile(uid_guid, profile_guid)
            client.detach_identity_from_profile(uid_guid, profile_guid)
            assert True
        except (PyegeriaException,) as e:
            print_basic_exception(e)
            assert False, "link/detach identity/profile failed"
        finally:
            try:
                if client and uid_guid:
                    client.delete_user_identity(uid_guid, cascade=True)
                if client and profile_guid:
                    client.delete_actor_profile(profile_guid, cascade=True)
            finally:
                if client:
                    client.close_session()
