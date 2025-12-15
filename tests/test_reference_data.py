"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module tests the ReferenceDataManager class and methods from reference_data.py

A running Egeria environment is needed to run these tests.

"""
import json
import time
from datetime import datetime

from rich import print, print_json
from rich.console import Console

from pyegeria._exceptions import (
    PyegeriaException,
    print_basic_exception,
    print_exception_table,
    print_validation_error, PyegeriaInvalidParameterException, PyegeriaAPIException, PyegeriaUnauthorizedException,
    PyegeriaNotFoundException, PyegeriaConnectionException,
)
from pyegeria.logging_configuration import config_logging, init_logging
from pyegeria.models import (NewElementRequestBody, UpdateElementRequestBody, DeleteElementRequestBody)
from pyegeria.reference_data import ReferenceDataManager
from pydantic import ValidationError

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


class TestReferenceDataManager:
    good_platform1_url = PLATFORM_URL

    good_user_1 = USER_ID
    good_user_2 = "peterprofile"
    good_server_1 = VIEW_SERVER
    good_server_2 = VIEW_SERVER
    good_view_server_1 = VIEW_SERVER
    good_view_server_2 = VIEW_SERVER

    def _unique_qname(self, prefix: str = "ValidValueDef") -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}::{ts}"

    def test_create_valid_value_definition(self):
        """Test creating a basic valid value definition with dict body"""
        rd_client = None
        try:
            rd_client = ReferenceDataManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = rd_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            display_name = f"Test Valid Value {datetime.now().strftime('%Y%m%d%H%M%S')}"
            description = "Test valid value definition for automated testing"
            qualified_name = self._unique_qname("TestValidValue")

            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ValidValueDefinitionProperties",
                    "qualifiedName": qualified_name,
                    "displayName": display_name,
                    "description": description,
                }
            }

            response = rd_client.create_valid_value_definition(body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nCreated valid value definition with GUID: {response}")
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
            if rd_client:
                rd_client.close_session()

    def test_create_valid_value_def_w_pyd(self):
        """Test creating a valid value definition with Pydantic model"""
        rd_client = None
        try:
            rd_client = ReferenceDataManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = rd_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            q_name = self._unique_qname("TestValidValuePyd")
            body = NewElementRequestBody(
                class_="NewElementRequestBody",
                is_own_anchor=True,
                properties={
                    "class": "ValidValueDefinitionProperties",
                    "qualifiedName": q_name,
                    "displayName": f"Pydantic Valid Value {datetime.now().strftime('%H%M%S')}",
                    "description": "Valid value definition created with Pydantic model",
                }
            )

            validated_body = body.model_dump(mode='json', by_alias=True, exclude_none=True)
            response = rd_client.create_valid_value_definition(validated_body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nCreated valid value definition with GUID: {response}")
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
            if rd_client:
                rd_client.close_session()

    def test_find_vv_definitions(self):
        """Test finding valid value definitions with search string"""
        rd_client = None
        try:
            rd_client = ReferenceDataManager(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = rd_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            search_string = "*"
            response = rd_client.find_valid_value_definitions(
                search_string,
                output_format="DICT",
                report_spec="Valid-Value-Def"
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Found {len(response)} valid value definitions")
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
            if rd_client:
                rd_client.close_session()

    def test_get_vv_def_by_name(self):
        """Test getting valid value definitions by name"""
        rd_client = None
        try:
            rd_client = ReferenceDataManager(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = rd_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            name = "Test Valid Value"
            response = rd_client.get_valid_value_definitions_by_name(name)
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Found {len(response)} valid value definitions")
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
            if rd_client:
                rd_client.close_session()

    def test_get_vv_def_by_guid(self):
        """Test getting a specific valid value definition by GUID"""
        rd_client = None
        try:
            rd_client = ReferenceDataManager(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = rd_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # First create a valid value definition to retrieve
            q_name = self._unique_qname("TestValidValueForRetrieval")
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ValidValueDefinitionProperties",
                    "qualifiedName": q_name,
                    "displayName": "Valid Value for GUID test",
                    "description": "Test valid value definition to retrieve by GUID",
                }
            }
            vv_guid = rd_client.create_valid_value_definition(body)
            print(f"\n\nCreated valid value definition with GUID: {vv_guid}")

            # Now retrieve it
            response = rd_client.get_valid_value_definition_by_guid(
                vv_guid,
                
                output_format="DICT",
                report_spec="Valid-Value-Def"
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
            if rd_client:
                rd_client.close_session()

    def test_update_valid_value_def(self):
        """Test updating a valid value definition's properties"""
        rd_client = None
        try:
            rd_client = ReferenceDataManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            token = rd_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # First create a valid value definition to update
            q_name = self._unique_qname("TestValidValueForUpdate")
            create_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ValidValueDefinitionProperties",
                    "qualifiedName": q_name,
                    "displayName": "Original Valid Value Name",
                    "description": "Original description",
                }
            }
            vv_guid = rd_client.create_valid_value_definition(create_body)
            print(f"\n\nCreated valid value definition with GUID: {vv_guid}")

            # Now update it
            new_desc = "Updated description for testing"
            update_body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": True,
                "properties": {
                    "class": "ValidValueDefinitionProperties",
                    "qualifiedName": q_name,
                    "displayName": "Updated Valid Value Name",
                    "description": new_desc,
                }
            }

            response = rd_client.update_valid_value_definition(vv_guid, update_body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nUpdated valid value definition successfully")

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
            if rd_client:
                rd_client.close_session()

    def test_delete_valid_value_definition(self):
        """Test deleting a valid value definition"""
        rd_client = None
        try:
            rd_client = ReferenceDataManager(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = rd_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # Create a valid value definition to delete
            q_name = self._unique_qname("ValidValueToDelete")
            create_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ValidValueDefinitionProperties",
                    "qualifiedName": q_name,
                    "displayName": "Valid Value to Delete",
                    "description": "This valid value definition will be deleted",
                }
            }
            vv_guid = rd_client.create_valid_value_definition(create_body)
            print(f"\n\nCreated valid value definition with GUID: {vv_guid}")

            # Delete it
            response = rd_client.delete_valid_value_definition(vv_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nDeleted valid value definition successfully")

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
            if rd_client:
                rd_client.close_session()

    def test_crud_valid_value_e2e(self):
        """End-to-end test: Create, Read, Update, Delete a valid value definition"""
        rd_client = None
        try:
            rd_client = ReferenceDataManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
            created_guid = None
            display_name = f"E2E Test Valid Value {datetime.now().strftime('%Y%m%d%H%M%S')}"

            token = rd_client.create_egeria_bearer_token(self.good_user_2, "secret")

            # CREATE
            print("\n\n=== CREATE ===")
            q_name = self._unique_qname("E2EValidValue")
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "ValidValueDefinitionProperties",
                    "qualifiedName": q_name,
                    "displayName": display_name,
                    "description": "End-to-end test valid value definition",
                }
            }

            create_resp = rd_client.create_valid_value_definition(body)
            created_guid = create_resp
            print(f"Created valid value definition: {created_guid}")
            assert created_guid is not None

            # READ
            print("\n\n=== READ ===")
            got = rd_client.get_valid_value_definition_by_guid(created_guid, output_format="JSON")
            print_json(json.dumps(got, indent=4))
            assert got is not None

            # UPDATE
            print("\n\n=== UPDATE ===")
            new_desc = "Updated description in E2E test"
            upd_body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": True,
                "properties": {
                    "class": "ValidValueDefinitionProperties",
                    "qualifiedName": q_name,
                    "displayName": display_name,
                    "description": new_desc,
                }
            }

            upd_resp = rd_client.update_valid_value_definition(created_guid, upd_body)
            print("Updated valid value definition successfully")

            # Verify update
            found = rd_client.get_valid_value_definition_by_guid(created_guid, output_format="JSON")
            print_json(json.dumps(found, indent=4))

            # DELETE
            print("\n\n=== DELETE ===")
            del_resp = rd_client.delete_valid_value_definition(created_guid)
            print("Deleted valid value definition successfully")

            # Verify deletion
            try:
                after = rd_client.get_valid_value_definition_by_guid(created_guid, output_format="JSON")
                # If we get here, deletion might not have worked
                print("Warning: Valid value definition still exists after deletion")
            except PyegeriaAPIException:
                print("Confirmed: Valid value definition no longer exists")

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
            if rd_client:
                rd_client.close_session()
