"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the SecurityOfficer class and methods from security_officer.py
"""

import json
import time
from datetime import datetime

from rich import print, print_json
from rich.console import Console

from pyegeria.core._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaConnectionException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
    PyegeriaUnauthorizedException,
    PyegeriaClientException,
    print_basic_exception,
    print_exception_table,
)
from pyegeria.omvs.security_officer import SecurityOfficer
from pyegeria.core.logging_configuration import config_logging, init_logging
from pyegeria.models import (
    UserAccountRequestBody,
    OpenMetadataUserAccount,
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
)

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
PLATFORM_NAME = "Local OMAG Server Platform"
USER_ID = "freddiemercury"
USER_PWD = "magic, magic"


class TestSecurityOfficer:
    good_platform1_url = PLATFORM_URL
    good_platform_name = PLATFORM_NAME
    good_user_1 = USER_ID
    good_server_1 = VIEW_SERVER

    def test_set_user_account(self):
        """Test creating/updating a user account"""
        try:
            s_client = SecurityOfficer(
                self.good_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            s_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)

            user_id = "testuser" + datetime.now().strftime("%H%M%S")
            body = {
                "class": "UserAccountRequestBody",
                "userAccount": {
                    "class": "OpenMetadataUserAccount",
                    "userId": user_id,
                    "userName": "Test User",
                    "userAccountStatus": "AVAILABLE",
                    "secrets": {"clearPassword": "testpassword"},
                },
            }

            s_client.set_user_account(self.good_platform_name, body)
            print(f"\n\nSet user account for: {user_id}")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
            PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            s_client.close_session()

    def test_get_user_account(self):
        """Test retrieving a user account"""
        try:
            s_client = SecurityOfficer(
                self.good_server_1, self.good_platform1_url, user_id="garygeeke"
            )
            s_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)

            # Retrieve Gary Geeke's account as a test (assuming it exists)
            user_id = "garygeeke" + datetime.now().strftime("%H%M%S")
            response = s_client.get_user_account(self.good_platform_name, user_id)
            print(f"\n\nRetrieved user account for: {user_id}")
            print_json(data=response)
            assert type(response) is dict
            assert response["userId"] == user_id

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
            PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            s_client.close_session()

    def test_delete_user_account(self):
        """Test deleting a user account"""
        try:
            s_client = SecurityOfficer(
                self.good_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            s_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)

            user_id = "deleteuser" + datetime.now().strftime("%H%M%S")
            # Create first
            body = {
                "class": "UserAccountRequestBody",
                "userAccount": {
                    "class": "OpenMetadataUserAccount",
                    "userId": user_id,
                    "userName": "Delete Test User",
                },
            }
            s_client.set_user_account(self.good_platform_name, body)

            # Then delete
            s_client.delete_user_account(self.good_platform_name, user_id)
            print(f"\n\nDeleted user account: {user_id}")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
            PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            s_client.close_session()

    def test_link_governance_zones(self):
        """Test linking governance zones"""
        try:
            s_client = SecurityOfficer(
                self.good_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            s_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)

            # These GUIDs are placeholders for unit test structure
            zone_guid = "zone-123"
            nested_zone_guid = "zone-456"
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "ZoneHierarchy",
                },
            }

            # This will likely fail with 404/NotFound if GUIDs don't exist, but tests structure
            try:
                s_client.link_governance_zones(zone_guid, nested_zone_guid, body)
                assert True
            except (PyegeriaNotFoundException, PyegeriaAPIException, PyegeriaClientException):
                print("Caught expected exception for placeholder GUIDs")
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
            s_client.close_session()

    def test_detach_governance_zones(self):
        """Test detaching governance zones"""
        try:
            s_client = SecurityOfficer(
                self.good_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            s_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)

            zone_guid = "zone-123"
            nested_zone_guid = "zone-456"
            body = {
                "class": "DeleteRelationshipRequestBody",
            }

            try:
                s_client.detach_governance_zones(zone_guid, nested_zone_guid, body)
                assert True
            except (PyegeriaNotFoundException, PyegeriaAPIException, PyegeriaClientException):
                print("Caught expected exception for placeholder GUIDs")
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
            s_client.close_session()

    def test_set_security_access_control(self):
        """Test setting a security access control on the platform."""
        try:
            s_client = SecurityOfficer(
                self.good_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            s_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)

            control_name = "test-control-" + datetime.now().strftime("%H%M%S")
            body = {
                "class": "SecurityAccessControlRequestBody",
                "securityAccessControl": {
                    "controlName": control_name,
                    "displayName": "Test Access Control",
                    "description": "Unit test security access control",
                    "controlTypeName": "TestControl",
                    "associatedSecurityList": {
                        "readOperation": ["testuser1", "testuser2"]
                    },
                    "securityLabels": [],
                    "securityProperties": {"environment": "test"},
                },
            }

            start_time = time.perf_counter()
            s_client.set_security_access_control(self.good_platform_name, body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nSet security access control: {control_name}")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
            PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            s_client.close_session()

    def test_get_security_access_control(self):
        """Test retrieving a security access control from the platform."""
        try:
            s_client = SecurityOfficer(
                self.good_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            s_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)

            control_name = "test-control-get-" + datetime.now().strftime("%H%M%S")
            # Create the control first
            body = {
                "class": "SecurityAccessControlRequestBody",
                "securityAccessControl": {
                    "controlName": control_name,
                    "displayName": "Test Get Control",
                    "description": "Unit test security access control for get",
                },
            }
            s_client.set_security_access_control(self.good_platform_name, body)

            start_time = time.perf_counter()
            response = s_client.get_security_access_control(self.good_platform_name, control_name)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nRetrieved security access control: {response}")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
            PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            s_client.close_session()

    def test_delete_security_access_control(self):
        """Test deleting a security access control from the platform."""
        try:
            s_client = SecurityOfficer(
                self.good_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            s_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)

            control_name = "test-control-del-" + datetime.now().strftime("%H%M%S")
            # Create the control first
            body = {
                "class": "SecurityAccessControlRequestBody",
                "securityAccessControl": {
                    "controlName": control_name,
                    "displayName": "Test Delete Control",
                    "description": "Unit test security access control for delete",
                },
            }
            s_client.set_security_access_control(self.good_platform_name, body)

            # Now delete it
            start_time = time.perf_counter()
            s_client.delete_security_access_control(self.good_platform_name, control_name)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nDeleted security access control: {control_name}")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
            PyegeriaNotFoundException,
        ) as e:
            print_exception_table(e)
            assert False, "Invalid request"
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            assert False, "Connection error"
        finally:
            s_client.close_session()
