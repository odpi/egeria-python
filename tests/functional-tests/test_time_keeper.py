"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the TimeKeeper class and methods from time_keeper.py

A running Egeria environment is needed to run these tests.
"""
import time
from datetime import datetime

from rich import print
from rich.console import Console

from pyegeria.core._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaConnectionException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
    PyegeriaUnauthorizedException,
    print_basic_exception,
    print_exception_table,
)
from pyegeria.omvs.time_keeper import TimeKeeper
from pyegeria.core.logging_configuration import config_logging, init_logging

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


class TestTimeKeeper:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_user_2 = USER_ID
    good_view_server_1 = VIEW_SERVER

    def _unique_qname(self, prefix: str = "ContextEvent") -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}::{ts}"

    def test_create_context_event(self):
        """Test creating a context event"""
        tk_client = TimeKeeper(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
        try:
            tk_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)
            start_time = time.perf_counter()

            display_name = f"Test Context Event {datetime.now().strftime('%Y%m%d%H%M%S')}"
            qualified_name = self._unique_qname("TestCE")

            body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "ContextEventProperties",
                    "qualifiedName": qualified_name,
                    "displayName": display_name,
                    "description": "Test context event for automated testing",
                }
            }

            response = tk_client.create_context_event(body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nCreated context event with GUID: {response}")
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
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            print("Skipping test due to connection error (no Egeria running)")
        finally:
            tk_client.close_session()

    def test_update_context_event(self):
        """Test updating a context event"""
        tk_client = TimeKeeper(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
        try:
            tk_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)
            
            # First create one
            qualified_name = self._unique_qname("TestUpdateCE")
            body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "ContextEventProperties",
                    "qualifiedName": qualified_name,
                    "displayName": "Initial Name",
                }
            }
            guid = tk_client.create_context_event(body)
            
            # Now update
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "ContextEventProperties",
                    "displayName": "Updated Name",
                }
            }
            tk_client.update_context_event(guid, update_body)
            
            # Verify
            retrieved = tk_client.get_context_event_by_guid(guid)
            assert retrieved["properties"]["displayName"] == "Updated Name"

        except PyegeriaConnectionException:
            print("Skipping test due to connection error")
        except Exception as e:
            print(f"Error: {e}")
            assert False
        finally:
            tk_client.close_session()

    def test_delete_context_event(self):
        """Test deleting a context event"""
        tk_client = TimeKeeper(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
        try:
            tk_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)
            
            qualified_name = self._unique_qname("TestDeleteCE")
            body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "ContextEventProperties",
                    "qualifiedName": qualified_name,
                    "displayName": "To be deleted",
                }
            }
            guid = tk_client.create_context_event(body)
            
            delete_body = {"class": "DeleteElementRequestBody"}
            tk_client.delete_context_event(guid, delete_body)
            
            # Should fail to retrieve or return not found
            try:
                tk_client.get_context_event_by_guid(guid)
                assert False, "Should have been deleted"
            except (PyegeriaNotFoundException, PyegeriaAPIException):
                pass

        except PyegeriaConnectionException:
            print("Skipping test due to connection error")
        finally:
            tk_client.close_session()

    def test_find_context_events(self):
        """Test finding context events"""
        try:
            tk_client = TimeKeeper(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            tk_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)
            
            response = tk_client.find_context_events(search_string="*")
            print(f"\n\nFound context events: {response}")
            assert response is not None

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
            print("Skipping test due to connection error (no Egeria running)")
        finally:
            tk_client.close_session()
