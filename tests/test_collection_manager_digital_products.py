
import json
import time
from datetime import datetime
from rich import print, print_json
from rich.console import Console
from pyegeria.omvs.collection_manager import CollectionManager, DeploymentStatusSearchString, DeploymentStatusFilterRequestBody
from pyegeria.core._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaException,
    PyegeriaConnectionException,
    PyegeriaClientException,
    PyegeriaAPIException,
    PyegeriaUnknownException,
    print_basic_exception,
    print_validation_error,
)
from pydantic import ValidationError

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"

console = Console(width=250)

class TestCollectionManagerDigitalProducts:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_view_server_1 = VIEW_SERVER

    def test_find_digital_products(self):
        c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
        try:
            c_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            start_time = time.perf_counter()
            search_string = "activityStatus Valid Values"
            # Test with parameters
            response = c_client.find_digital_products(search_string=search_string, deployment_status="ACTIVE", output_format="JSON")
            duration = time.perf_counter() - start_time
            print(f"\nfind_digital_products duration: {duration} seconds")
            
            if isinstance(response, list):
                print(f"Found {len(response)} digital products")
            else:
                print(f"Response: {response}")
            
            assert response is not None
            
        except (PyegeriaException, ValidationError) as e:
            if "CONNECTION_ERROR" in str(e):
                print("Skipping test: Egeria server not reachable")
            else:
                print_basic_exception(e)
                raise e
        finally:
            c_client.close_session()

    def test_find_digital_products_with_body(self):
        c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
        try:
            c_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            
            body = {
                "class": "DeploymentStatusSearchString",
                "searchString": "*",
                "deploymentStatus": "ACTIVE",
                "startsWith": False,
                "ignoreCase": True
            }
            
            response = c_client.find_digital_products(body=body)
            assert response is not None
            
        except (PyegeriaException, ValidationError) as e:
            if "CONNECTION_ERROR" in str(e):
                print("Skipping test: Egeria server not reachable")
            else:
                raise e
        finally:
            c_client.close_session()

    def test_get_digital_products_by_category(self):
        c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
        try:
            c_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            
            response = c_client.get_digital_products_by_category(category="TestCategory", deployment_status="ACTIVE")
            assert response is not None
            
        except (PyegeriaException, ValidationError) as e:
            if "CONNECTION_ERROR" in str(e):
                print("Skipping test: Egeria server not reachable")
            else:
                raise e
        finally:
            c_client.close_session()

    def test_get_digital_products_by_category_with_body(self):
        c_client = CollectionManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
        try:
            c_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            
            body = DeploymentStatusFilterRequestBody(
                class_="DeploymentStatusFilterRequestBody",
                filter="TestCategory",
                deployment_status="ACTIVE"
            )
            
            response = c_client.get_digital_products_by_category(category="TestCategory", body=body)
            assert response is not None
            
        except (PyegeriaException, ValidationError) as e:
            if "CONNECTION_ERROR" in str(e):
                print("Skipping test: Egeria server not reachable")
            else:
                raise e
        finally:
            c_client.close_session()
