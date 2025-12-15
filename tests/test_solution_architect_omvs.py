"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module tests the SolutionArchitect class and methods from solution_architect.py

A running Egeria environment is needed to run these tests.

"""
import json
import time
from datetime import datetime

from rich import print, print_json
from rich.console import Console

from pyegeria import SolutionArchitect, PyegeriaException
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
from pyegeria._exceptions import PyegeriaException, print_basic_exception, print_validation_error, print_exception_response
from pyegeria.logging_configuration import config_logging, init_logging
from pyegeria.models import (NewElementRequestBody, UpdateElementRequestBody, DeleteElementRequestBody)
from pyegeria.solution_architect import SolutionArchitect
from pydantic import ValidationError

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "erinoverview"
USER_PWD = "secret"


class TestSolutionArchitect:
    good_platform1_url = PLATFORM_URL

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    good_server_1 = "simple-metadata-store"
    good_server_2 = "laz_kv"
    good_view_server_1 = "view-server"
    good_view_server_2 = VIEW_SERVER

    def _unique_qname(self, prefix: str = "SolutionElement") -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}::{ts}"

    # Information Supply Chain Tests
    
    def test_create_info_supply_chain(self):
        """Test creating an information supply chain with dict body"""
        sa_client = None
        try:
            sa_client = SolutionArchitect(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = sa_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            display_name = f"Test Supply Chain {datetime.now().strftime('%Y%m%d%H%M%S')}"
            description = "Test information supply chain for automated testing"
            qualified_name = self._unique_qname("TestSupplyChain")

            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "InformationSupplyChainProperties",
                    "qualifiedName": qualified_name,
                    "displayName": display_name,
                    "description": description,
                    "scope": "test",
                    "purposes": ["testing", "validation"]
                }
            }

            response = sa_client.create_info_supply_chain(body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nCreated information supply chain with GUID: {response}")
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
            if sa_client:
                sa_client.close_session()

    def test_find_info_supply_chains(self):
        """Test finding information supply chains with search string"""
        sa_client = None
        try:
            sa_client = SolutionArchitect(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = sa_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            search_string = "*"
            response = sa_client.find_information_supply_chains(
                search_string,
                output_format="DICT"
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Found {len(response)} information supply chains")
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
            if sa_client:
                sa_client.close_session()

    def test_get_info_supply_chain_by_guid(self):
        """Test getting a specific information supply chain by GUID"""
        sa_client = None
        try:
            sa_client = SolutionArchitect(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = sa_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # First create a supply chain to retrieve
            q_name = self._unique_qname("TestSupplyChainForRetrieval")
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "InformationSupplyChainProperties",
                    "qualifiedName": q_name,
                    "displayName": "Supply Chain for GUID test",
                    "description": "Test supply chain to retrieve by GUID",
                }
            }
            chain_guid = sa_client.create_info_supply_chain(body)
            print(f"\n\nCreated information supply chain with GUID: {chain_guid}")

            # Now retrieve it
            response = sa_client.get_info_supply_chain_by_guid(
                chain_guid,
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
            if sa_client:
                sa_client.close_session()

    def test_update_info_supply_chain(self):
        """Test updating an information supply chain's properties"""
        sa_client = None
        try:
            sa_client = SolutionArchitect(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = sa_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # First create a supply chain to update
            q_name = self._unique_qname("TestSupplyChainForUpdate")
            create_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "InformationSupplyChainProperties",
                    "qualifiedName": q_name,
                    "displayName": "Original Supply Chain Name",
                    "description": "Original description",
                }
            }
            chain_guid = sa_client.create_info_supply_chain(create_body)
            print(f"\n\nCreated information supply chain with GUID: {chain_guid}")

            # Now update it
            new_desc = "Updated description for testing"
            update_body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": True,
                "properties": {
                    "class": "InformationSupplyChainProperties",
                    "qualifiedName": q_name,
                    "displayName": "Updated Supply Chain Name",
                    "description": new_desc,
                }
            }

            response = sa_client.update_info_supply_chain(chain_guid, update_body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nUpdated information supply chain successfully")

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
            if sa_client:
                sa_client.close_session()

    def test_delete_info_supply_chain(self):
        """Test deleting an information supply chain"""
        sa_client = None
        try:
            sa_client = SolutionArchitect(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = sa_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            # Create a supply chain to delete
            q_name = self._unique_qname("SupplyChainToDelete")
            create_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "InformationSupplyChainProperties",
                    "qualifiedName": q_name,
                    "displayName": "Supply Chain to Delete",
                    "description": "This supply chain will be deleted",
                }
            }
            chain_guid = sa_client.create_info_supply_chain(create_body)
            print(f"\n\nCreated information supply chain with GUID: {chain_guid}")

            # Delete it
            response = sa_client.delete_info_supply_chain(chain_guid)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nDeleted information supply chain successfully")

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
            if sa_client:
                sa_client.close_session()

    # Solution Blueprint Tests
    
    def test_create_solution_blueprint(self):
        """Test creating a solution blueprint with dict body"""
        sa_client = None
        try:
            sa_client = SolutionArchitect(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = sa_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            display_name = f"Test Blueprint {datetime.now().strftime('%Y%m%d%H%M%S')}"
            description = "Test solution blueprint for automated testing"
            qualified_name = self._unique_qname("TestBlueprint")

            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "SolutionBlueprintProperties",
                    "qualifiedName": qualified_name,
                    "displayName": display_name,
                    "description": description,
                }
            }

            response = sa_client.create_solution_blueprint(body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nCreated solution blueprint with GUID: {response}")
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
            if sa_client:
                sa_client.close_session()

    def test_find_solution_blueprints(self):
        """Test finding solution blueprints with search string"""
        sa_client = None
        try:
            sa_client = SolutionArchitect(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = sa_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            search_string = "*"
            response = sa_client.find_solution_blueprints(
                search_string,
                output_format="DICT"
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Found {len(response)} solution blueprints")
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
            if sa_client:
                sa_client.close_session()

    # Solution Component Tests
    
    def test_create_solution_component(self):
        """Test creating a solution component with dict body"""
        sa_client = None
        try:
            sa_client = SolutionArchitect(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = sa_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            display_name = f"Test Component {datetime.now().strftime('%Y%m%d%H%M%S')}"
            description = "Test solution component for automated testing"
            qualified_name = self._unique_qname("TestComponent")

            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "SolutionComponentProperties",
                    "qualifiedName": qualified_name,
                    "displayName": display_name,
                    "description": description,
                }
            }

            response = sa_client.create_solution_component(body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nCreated solution component with GUID: {response}")
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
            if sa_client:
                sa_client.close_session()

    def test_find_solution_components(self):
        """Test finding solution components with search string"""
        sa_client = None
        try:
            sa_client = SolutionArchitect(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            token = sa_client.create_egeria_bearer_token(self.good_user_2, "secret")
            start_time = time.perf_counter()

            search_string = "*"
            response = sa_client.find_solution_components(
                search_string,
                output_format="DICT"
            )
            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Found {len(response)} solution components")
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
            if sa_client:
                sa_client.close_session()

    def test_crud_supply_chain_e2e(self):
        """End-to-end test: Create, Read, Update, Delete an information supply chain"""
        sa_client = None
        try:
            sa_client = SolutionArchitect(self.good_view_server_2, self.good_platform1_url, user_id=self.good_user_2)
            created_guid = None
            display_name = f"E2E Test Supply Chain {datetime.now().strftime('%Y%m%d%H%M%S')}"

            token = sa_client.create_egeria_bearer_token(self.good_user_2, "secret")

            # CREATE
            print("\n\n=== CREATE ===")
            q_name = self._unique_qname("E2ESupplyChain")
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "InformationSupplyChainProperties",
                    "qualifiedName": q_name,
                    "displayName": display_name,
                    "description": "End-to-end test information supply chain",
                }
            }

            create_resp = sa_client.create_info_supply_chain(body)
            created_guid = create_resp
            print(f"Created information supply chain: {created_guid}")
            assert created_guid is not None

            # READ
            print("\n\n=== READ ===")
            got = sa_client.get_info_supply_chain_by_guid(created_guid, output_format="JSON")
            print_json(json.dumps(got, indent=4))
            assert got is not None

            # UPDATE
            print("\n\n=== UPDATE ===")
            new_desc = "Updated description in E2E test"
            upd_body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": True,
                "properties": {
                    "class": "InformationSupplyChainProperties",
                    "qualifiedName": q_name,
                    "displayName": display_name,
                    "description": new_desc,
                }
            }

            upd_resp = sa_client.update_info_supply_chain(created_guid, upd_body)
            print("Updated information supply chain successfully")

            # Verify update
            found = sa_client.get_info_supply_chain_by_guid(created_guid, output_format="JSON")
            print_json(json.dumps(found, indent=4))

            # DELETE
            print("\n\n=== DELETE ===")
            del_resp = sa_client.delete_info_supply_chain(created_guid)
            print("Deleted information supply chain successfully")

            # Verify deletion
            try:
                after = sa_client.get_info_supply_chain_by_guid(created_guid, output_format="JSON")
                # If we get here, deletion might not have worked
                print("Warning: Supply chain still exists after deletion")
            except PyegeriaAPIException:
                print("Confirmed: Supply chain no longer exists")

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
            if sa_client:
                sa_client.close_session()