"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the DigitalBusiness class and methods

A running Egeria environment is needed to run these tests.
"""
import asyncio
import json
import time
from datetime import datetime
from loguru import logger

from rich import print, print_json
from rich.console import Console
from pyegeria.digital_business import DigitalBusiness
from pyegeria.logging_configuration import config_logging, init_logging
from pyegeria._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaConnectionException,
    PyegeriaClientException,
    PyegeriaAPIException,
    PyegeriaUnknownException,
    print_basic_exception,
    print_validation_error, PyegeriaException,
)
from pydantic import ValidationError
from pyegeria.models import (
    NewElementRequestBody,
    UpdateElementRequestBody,
    DeleteElementRequestBody,
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
    NewClassificationRequestBody,
    DeleteClassificationRequestBody
)

disable_ssl_warnings = True
console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"

class TestDigitalBusiness:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_user_2 = "peterprofile"
    good_server_1 = VIEW_SERVER
    good_view_server_1 = VIEW_SERVER

    def _unique_qname(self, prefix: str = "DigitalBusiness") -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}::{ts}"

    def test_create_business_capability(self):
        try:
            db_client = DigitalBusiness(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1, user_pwd='secret')

            start_time = time.perf_counter()
            db_client.create_egeria_bearer_token(self.good_user_1,"secret")
            duration = time.perf_counter() - start_time
            qname = self._unique_qname("BusCap")
            body = NewElementRequestBody(
                class_="NewElementRequestBody",
                properties={
                    "class": "BusinessCapabilityProperties",
                    "qualifiedName": qname,
                    "displayName": "Test Business Capability",
                    "description": "A test capability created by unit tests"
                }
            )
            start_time = time.perf_counter()
            response = db_client.create_business_capability(body=body)
            duration = time.perf_counter() - start_time
            print(f"response type is {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            
            if type(response) is str:
                print("\n\nGUID is: " + response)
                assert len(response) > 0
            else:
                print(f"Response: {response}")
                assert False, "Should return a GUID string"

        except (PyegeriaInvalidParameterException, PyegeriaConnectionException,
                PyegeriaClientException, PyegeriaAPIException, PyegeriaUnknownException) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error"
        finally:
            db_client.close_session()

    def test_get_business_capability_by_guid(self):
        try:
            db_client = DigitalBusiness(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            db_client.create_egeria_bearer_token(self.good_user_1,"secret")

            # First create one to be sure it exists
            qname = self._unique_qname("BusCapGet")
            body = NewElementRequestBody(
                class_="NewElementRequestBody",
                properties={"qualifiedName": qname, "displayName": "Get Test"}
            )
            guid = db_client.create_business_capability(body=body)
            
            start_time = time.perf_counter()
            response = db_client.get_business_capability_by_guid(guid)
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
            db_client.close_session()

    def test_update_business_capability(self):
        try:
            db_client = DigitalBusiness(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            db_client.create_egeria_bearer_token(self.good_user_1,"secret")

            # Create
            qname = self._unique_qname("BusCapUpdate")
            guid = db_client.create_business_capability(body=NewElementRequestBody(
                class_="NewElementRequestBody",
                properties={"qualifiedName": qname, "displayName": "Before Update"}
            ))
            
            # Update
            update_body = UpdateElementRequestBody(
                class_="UpdateElementRequestBody",
                properties={"displayName": "After Update"}
            )
            db_client.update_business_capability(guid, body=update_body)
            
            # Verify
            response = db_client.get_business_capability_by_guid(guid)
            assert response["properties"]["displayName"] == "After Update"

        except Exception as e:
            print(f"Exception: {e}")
            assert False
        finally:
            db_client.close_session()

    def test_delete_business_capability(self):
        try:
            db_client = DigitalBusiness(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            db_client.create_egeria_bearer_token(self.good_user_1,"secret")

            # Create
            qname = self._unique_qname("BusCapDelete")
            guid = db_client.create_business_capability(body=NewElementRequestBody(
                class_="NewElementRequestBody",
                properties={"qualifiedName": qname}
            ))
            # guid = "d380f268-f8a3-4b1b-aaff-4d0f7115d69e"
            # Delete
            db_client.delete_business_capability(guid, body=DeleteElementRequestBody(class_="DeleteElementRequestBody"))
            
            # Verify deletion (should raise or return something indicating it's gone)
            # In Egeria often it's a 404 or similar.
            try:
                db_client.get_business_capability_by_guid(guid)
                assert False, "Should have been deleted"
            except Exception:
                pass # Expected

        except Exception as e:
            print(f"Exception: {e}")
            assert False
        finally:
            db_client.close_session()

    def test_find_business_capabilities(self):
        try:
            db_client = DigitalBusiness(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            db_client.create_egeria_bearer_token(self.good_user_1,"secret")

            response = db_client.find_business_capabilities(search_string="*", output_format="DICT",
                                                            report_spec="Referenceable")
            print(f"Found {len(response) if response else 0} capabilities")
            assert type(response) is list
            if isinstance(response, list):
                console.print(json.dumps(response, indent=2))
            elif isinstance(response, str):
                console.print(response)

        except Exception as e:
            print(f"Exception: {e}")
            assert False
        finally:
            db_client.close_session()

    def test_get_business_capabilities_by_name(self):
        try:
            db_client = DigitalBusiness(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            db_client.create_egeria_bearer_token(self.good_user_1,"secret")

            # qname = self._unique_qname("BusCapByName")
            # db_client.create_business_capability(body=NewElementRequestBody(
            #     class_="NewElementRequestBody",
            #     properties={"qualifiedName": qname, "displayName": "UniqueName"}
            # ))
            qname = "BusinessArea::GOV"
            response = db_client.get_business_capabilities_by_name(filter_string=qname)
            assert type(response) is list
            assert len(response) >= 1

        except (PyegeriaException) as e:
            print_basic_exception(e)
            assert False
        finally:
            db_client.close_session()

    def test_link_business_capability_dependency(self):
        try:
            db_client = DigitalBusiness(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            db_client.create_egeria_bearer_token(self.good_user_1,"secret")

            guid1 = db_client.create_business_capability(body=NewElementRequestBody(
                class_="NewElementRequestBody", properties={"qualifiedName": self._unique_qname("Cap1")}
            ))
            guid2 = db_client.create_business_capability(body=NewElementRequestBody(
                class_="NewElementRequestBody", properties={"qualifiedName": self._unique_qname("Cap2")}
            ))
            
            db_client.link_business_capability_dependency(guid1, guid2, body=NewRelationshipRequestBody(class_="NewRelationshipRequestBody"))
            
            # Cleanup
            db_client.detach_business_capability_dependency(guid1, guid2, body=DeleteRelationshipRequestBody(class_="DeleteRelationshipRequestBody"))

        except Exception as e:
            print(f"Exception: {e}")
            assert False
        finally:
            db_client.close_session()

    def test_link_digital_support(self):
        try:
            db_client = DigitalBusiness(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            db_client.create_egeria_bearer_token(self.good_user_1,"secret")

            cap_guid = db_client.create_business_capability(body=NewElementRequestBody(
                class_="NewElementRequestBody", properties={"qualifiedName": self._unique_qname("CapSupport")}
            ))
            
            # Using another capability as the "digital support" element for testing purposes
            support_guid = db_client.create_business_capability(body=NewElementRequestBody(
                class_="NewElementRequestBody", properties={"qualifiedName": self._unique_qname("SupportElement")}
            ))
            
            db_client.link_digital_support(cap_guid, support_guid, body=NewRelationshipRequestBody(class_="NewRelationshipRequestBody"))
            
            # Cleanup
            db_client.detach_digital_support(cap_guid, support_guid,
                                             body=DeleteRelationshipRequestBody(class_="DeleteRelationshipRequestBody"))

        except Exception as e:
            print(f"Exception: {e}")
            assert False
        finally:
            db_client.close_session()

    def test_business_significance(self):
        try:
            db_client = DigitalBusiness(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            db_client.create_egeria_bearer_token(self.good_user_1,"secret")

            guid = db_client.create_business_capability(body=NewElementRequestBody(
                class_="NewElementRequestBody", properties={"qualifiedName": self._unique_qname("SignificanceTest")}
            ))
            
            db_client.set_business_significant(guid, body=NewClassificationRequestBody(class_="NewClassificationRequestBody"))
            
            db_client.clear_business_significance(guid, body=DeleteClassificationRequestBody(class_="DeleteClassificationRequestBody"))

        except Exception as e:
            print(f"Exception: {e}")
            assert False
        finally:
            db_client.close_session()
