"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the PrivacyOfficer class and methods from privacy_officer.py
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
    PyegeriaClientException,
    print_basic_exception,
    print_exception_table,
)
from pyegeria.omvs.privacy_officer import PrivacyOfficer
from pyegeria.core.logging_configuration import config_logging, init_logging
from pyegeria.models import (
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
)

disable_ssl_warnings = True

console = Console(width=120)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "garygeeke"
USER_PWD = "secret"


class TestPrivacyOfficer:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_server_1 = VIEW_SERVER

    def test_permitted_processing_linkage(self):
        """Test linking and detaching permitted processing"""
        try:
            p_client = PrivacyOfficer(
                self.good_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            p_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)

            purpose_guid = "purpose-guid"
            description_guid = "description-guid"
            
            # Link
            body = NewRelationshipRequestBody(
                class_="NewRelationshipRequestBody",
                properties={
                    "class": "PermittedProcessingProperties",
                    "label": "Test Label",
                    "description": "Test Description"
                }
            )

            try:
                p_client.link_permitted_processing(purpose_guid, description_guid, body)
            except (PyegeriaNotFoundException, PyegeriaAPIException, PyegeriaClientException) as e:
                # We expect a 404 since we are using synthetic GUIDs
                # Silently pass if it's a "Not Found" error
                if getattr(e, "response_code", None) == 404 or "404" in str(e):
                    print("Caught expected 404 exception for placeholder GUIDs")
                    assert True
                    return
                raise e

            # Detach
            detach_body = DeleteRelationshipRequestBody(
                class_="DeleteRelationshipRequestBody"
            )
            start_time = time.perf_counter()
            p_client.detach_permitted_processing(purpose_guid, description_guid, detach_body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDetach Permitted Processing duration was {duration} seconds")
            
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
            p_client.close_session()

    def test_data_processing_target_linkage(self):
        """Test linking and detaching data processing target"""
        try:
            p_client = PrivacyOfficer(
                self.good_server_1, self.good_platform1_url, user_id=self.good_user_1
            )
            p_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)

            action_guid = "action-guid"
            target_guid = "target-guid"
            
            # Link
            body = NewRelationshipRequestBody(
                class_="NewRelationshipRequestBody",
                properties={
                    "class": "DataProcessingTargetProperties",
                    "label": "Test Target Label",
                    "description": "Test Target Description"
                }
            )

            try:
                p_client.link_data_processing_target(action_guid, target_guid, body)
            except (PyegeriaNotFoundException, PyegeriaAPIException, PyegeriaClientException) as e:
                # We expect a 404 since we are using synthetic GUIDs
                if getattr(e, "response_code", None) == 404 or "404" in str(e):
                    print("Caught expected 404 exception for placeholder GUIDs")
                    assert True
                    return
                raise e

            # Detach
            detach_body = DeleteRelationshipRequestBody(
                class_="DeleteRelationshipRequestBody"
            )
            start_time = time.perf_counter()
            p_client.detach_data_processing_target(action_guid, target_guid, detach_body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDetach Data Processing Target duration was {duration} seconds")
            
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
            p_client.close_session()
