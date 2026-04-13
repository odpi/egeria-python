"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the ProductManager class and methods

A running Egeria environment is needed to run these tests.
"""
import time
from datetime import datetime

from rich import print, print_json
from rich.console import Console
from pyegeria.omvs.product_manager import ProductManager
from pyegeria.omvs.actor_manager import ActorManager
from pyegeria.core.logging_configuration import config_logging, init_logging
from pyegeria.core._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaConnectionException,
    PyegeriaClientException,
    PyegeriaAPIException,
    PyegeriaUnknownException,
    print_basic_exception,
    print_validation_error,
)
from pydantic import ValidationError
from pyegeria.models import (
    NewElementRequestBody,
    UpdateElementRequestBody,
    NewRelationshipRequestBody,
)

disable_ssl_warnings = True
console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


class TestProductManager:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_user_2 = "peterprofile"
    good_server_1 = VIEW_SERVER
    good_view_server_1 = VIEW_SERVER

    def _unique_qname(self, prefix: str = "DigitalProduct") -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}::{ts}"

    def test_create_digital_product(self):
        try:
            pm_client = ProductManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )

            start_time = time.perf_counter()
            pm_client.create_egeria_bearer_token(self.good_user_1, "secret")
            duration = time.perf_counter() - start_time
            qname = self._unique_qname("Product")
            body = NewElementRequestBody(
                class_="NewElementRequestBody",
                properties={
                    "class": "DigitalProductProperties",
                    "qualifiedName": qname,
                    "displayName": "Test Digital Product",
                    "description": "A test product created by unit tests",
                    "productName": "TestProduct",
                    "productType": "Application",
                },
            )
            start_time = time.perf_counter()
            response = pm_client.create_digital_product(body=body)
            duration = time.perf_counter() - start_time
            print(f"response type is {type(response)}")
            print(f"\n\tDuration was {duration} seconds")

            if type(response) is str:
                print("\n\nGUID is: " + response)
                assert len(response) > 0
            else:
                print(f"Response: {response}")
                assert False, "Should return a GUID string"

        except (
            PyegeriaInvalidParameterException,
            PyegeriaConnectionException,
            PyegeriaClientException,
            PyegeriaAPIException,
            PyegeriaUnknownException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error"
        finally:
            pm_client.close_session()

    def test_get_digital_product_by_guid(self):
        try:
            pm_client = ProductManager(
                self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            pm_client.create_egeria_bearer_token(self.good_user_1, "secret")

            # First create one to be sure it exists
            qname = self._unique_qname("ProductGet")
            body = NewElementRequestBody(
                class_="NewElementRequestBody",
                properties={
                    "qualifiedName": qname,
                    "displayName": "Get Test",
                    "productName": "GetTestProduct",
                },
            )
            guid = pm_client.create_digital_product(body=body)

            start_time = time.perf_counter()
            response = pm_client.get_digital_product_by_guid(guid)
            duration = time.perf_counter() - start_time

            print(f"response type is {type(response)}")
            print(f"\n\tDuration was {duration} seconds")

            if type(response) is dict:
                print_json(data=response)
                assert response["properties"]["qualifiedName"] == qname
            else:
                assert False, "Should return a dictionary"

        except Exception as e:
            print(f"Exception: {e}")
            assert False
        finally:
            pm_client.close_session()

    def test_update_digital_product(self):
        try:
            pm_client = ProductManager(
                self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            pm_client.create_egeria_bearer_token(self.good_user_1, "secret")

            # Create
            qname = self._unique_qname("ProductUpdate")
            guid = pm_client.create_digital_product(
                body=NewElementRequestBody(
                    class_="NewElementRequestBody",
                    properties={
                        "qualifiedName": qname,
                        "displayName": "Before Update",
                        "productName": "UpdateTestProduct",
                    },
                )
            )

            # Update
            update_body = UpdateElementRequestBody(
                class_="UpdateElementRequestBody",
                properties={"displayName": "After Update"},
            )
            pm_client.update_digital_product(guid, body=update_body)

            # Verify
            updated = pm_client.get_digital_product_by_guid(guid)
            assert updated["properties"]["displayName"] == "After Update"
            print("Update successful")

        except Exception as e:
            print(f"Exception: {e}")
            assert False
        finally:
            pm_client.close_session()

    def test_delete_digital_product(self):
        try:
            pm_client = ProductManager(
                self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            pm_client.create_egeria_bearer_token(self.good_user_1, "secret")

            # Create
            qname = self._unique_qname("ProductDelete")
            guid = pm_client.create_digital_product(
                body=NewElementRequestBody(
                    class_="NewElementRequestBody",
                    properties={
                        "qualifiedName": qname,
                        "displayName": "To Be Deleted",
                        "productName": "DeleteTestProduct",
                    },
                )
            )

            # Delete
            pm_client.delete_digital_product(guid)
            print(f"Deleted product {guid}")

            # Verify deletion - should not find it
            try:
                deleted = pm_client.get_digital_product_by_guid(guid)
                assert False, "Should not find deleted product"
            except:
                print("Product successfully deleted")

        except Exception as e:
            print(f"Exception: {e}")
            assert False
        finally:
            pm_client.close_session()

    def test_link_digital_product_dependency(self):
        """Test linking two digital products with a dependency relationship"""
        try:
            pm_client = ProductManager(
                self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            pm_client.create_egeria_bearer_token(self.good_user_1, "secret")

            # Create consumer product
            qname1 = self._unique_qname("ConsumerProduct")
            consumer_guid = pm_client.create_digital_product(
                body=NewElementRequestBody(
                    class_="NewElementRequestBody",
                    properties={
                        "qualifiedName": qname1,
                        "displayName": "Consumer Product",
                        "productName": "ConsumerProduct",
                    },
                )
            )

            # Create consumed product
            qname2 = self._unique_qname("ConsumedProduct")
            consumed_guid = pm_client.create_digital_product(
                body=NewElementRequestBody(
                    class_="NewElementRequestBody",
                    properties={
                        "qualifiedName": qname2,
                        "displayName": "Consumed Product",
                        "productName": "ConsumedProduct",
                    },
                )
            )

            # Link dependency
            link_body = NewRelationshipRequestBody(
                class_="NewRelationshipRequestBody",
                properties={
                    "class": "DigitalProductDependencyProperties",
                    "label": "Test Dependency",
                    "description": "Test product dependency",
                },
            )
            pm_client.link_digital_product_dependency(
                consumer_guid, consumed_guid, body=link_body
            )
            print(f"Linked product dependency between {consumer_guid} and {consumed_guid}")

            # Detach dependency
            pm_client.detach_digital_product_dependency(consumer_guid, consumed_guid)
            print("Detached product dependency")

        except Exception as e:
            print(f"Exception: {e}")
            assert False
        finally:
            pm_client.close_session()

    def test_link_product_manager(self):
        """Test linking a product manager role to a digital product"""
        try:
            pm_client = ProductManager(
                self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            pm_client.create_egeria_bearer_token(self.good_user_1, "secret")

            # Create digital product
            qname = self._unique_qname("ManagedProduct")
            product_guid = pm_client.create_digital_product(
                body=NewElementRequestBody(
                    class_="NewElementRequestBody",
                    properties={
                        "qualifiedName": qname,
                        "displayName": "Managed Product",
                        "productName": "ManagedProduct",
                    },
                )
            )

            # Create actor role for product manager
            actor_client = ActorManager(
                self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            actor_client.create_egeria_bearer_token(self.good_user_1, "secret")

            role_qname = self._unique_qname("ProductManagerRole")
            role_guid = actor_client.create_actor_role(
                body=NewElementRequestBody(
                    class_="NewElementRequestBody",
                    properties={
                        "qualifiedName": role_qname,
                        "name": "Product Manager Role",
                        "description": "Test product manager role",
                    },
                )
            )

            # Link product manager
            link_body = NewRelationshipRequestBody(
                class_="NewRelationshipRequestBody",
                properties={
                    "class": "AssignmentScopeProperties",
                    "assignmentType": "Product Manager",
                    "description": "Test product manager assignment",
                },
            )
            pm_client.link_product_manager(product_guid, role_guid, body=link_body)
            print(f"Linked product manager {role_guid} to product {product_guid}")

            # Detach product manager
            pm_client.detach_product_manager(product_guid, role_guid)
            print("Detached product manager")

            # Cleanup
            actor_client.delete_actor_role(role_guid)
            actor_client.close_session()

        except Exception as e:
            print(f"Exception: {e}")
            assert False
        finally:
            pm_client.close_session()

    def test_create_digital_product_catalog(self):
        try:
            pm_client = ProductManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            pm_client.create_egeria_bearer_token(self.good_user_1, "secret")

            qname = self._unique_qname("ProductCatalog")
            body = NewElementRequestBody(
                class_="NewElementRequestBody",
                properties={
                    "class": "DigitalProductCatalogProperties",
                    "qualifiedName": qname,
                    "name": "Test Product Catalog",
                    "description": "A test catalog created by unit tests",
                },
            )
            response = pm_client.create_digital_product_catalog(body=body)

            if type(response) is str:
                print("\n\nCatalog GUID is: " + response)
                assert len(response) > 0
            else:
                print(f"Response: {response}")
                assert False, "Should return a GUID string"

        except Exception as e:
            print(f"Exception: {e}")
            assert False
        finally:
            pm_client.close_session()

    def test_get_digital_product_catalog_by_guid(self):
        try:
            pm_client = ProductManager(
                self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            pm_client.create_egeria_bearer_token(self.good_user_1, "secret")

            # First create one
            qname = self._unique_qname("CatalogGet")
            body = NewElementRequestBody(
                class_="NewElementRequestBody",
                properties={
                    "qualifiedName": qname,
                    "name": "Get Test Catalog",
                },
            )
            guid = pm_client.create_digital_product_catalog(body=body)

            # Get it
            response = pm_client.get_digital_product_catalog_by_guid(guid)

            if type(response) is dict:
                print_json(data=response)
                assert response["properties"]["qualifiedName"] == qname
            else:
                assert False, "Should return a dictionary"

        except Exception as e:
            print(f"Exception: {e}")
            assert False
        finally:
            pm_client.close_session()


if __name__ == "__main__":
    print("Manual test run")