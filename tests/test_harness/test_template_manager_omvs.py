"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the TemplateManager class and methods from template_manager_omvs.py

A running Egeria environment is needed to run these tests.
"""
import time
from datetime import datetime
from rich import print
from rich.console import Console

from pyegeria._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaConnectionException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
    PyegeriaUnauthorizedException,
    print_basic_exception,
    print_exception_table,
)
from pyegeria.template_manager_omvs import TemplateManager
from pyegeria.logging_configuration import config_logging, init_logging

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"

class TestTemplateManager:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_view_server_1 = VIEW_SERVER

    def _unique_qname(self, prefix: str = "Template") -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}::{ts}"

    def test_create_metadata_element_in_store(self):
        """Test creating a metadata element in store"""
        try:
            tm_client = TemplateManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
            tm_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
            start_time = time.perf_counter()

            qualified_name = self._unique_qname("TestTemplateElement")
            body = {
                "class": "NewOpenMetadataElementRequestBody",
                "typeName": "Referenceable",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "ReferenceableProperties",
                    "qualifiedName": qualified_name,
                }
            }

            response = tm_client.create_metadata_element_in_store(body)
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print(f"\n\nCreated element with GUID: {response}")
            assert type(response) is str
            assert len(response) > 0
            return response

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
            tm_client.close_session()

    def test_update_metadata_element_in_store(self):
        """Test updating a metadata element in store"""
        tm_client = TemplateManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
        tm_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
        try:
            # Create first
            qualified_name = self._unique_qname("TestUpdateElement")
            create_body = {
                "class": "NewOpenMetadataElementRequestBody",
                "typeName": "Referenceable",
                "properties": {
                    "class": "ReferenceableProperties",
                    "qualifiedName": qualified_name,
                }
            }
            guid = tm_client.create_metadata_element_in_store(create_body)
            assert guid is not None

            # Update
            update_body = {
                "class": "UpdateOpenMetadataElementRequestBody",
                "properties": {
                    "class": "ReferenceableProperties",
                    "qualifiedName": qualified_name,
                    "description": "Updated description"
                }
            }
            tm_client.update_metadata_element_in_store(guid, update_body)
            print(f"Updated element {guid}")

        finally:
            tm_client.close_session()

    def test_classify_declassify_metadata_element(self):
        """Test classifying and declassifying a metadata element"""
        tm_client = TemplateManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
        tm_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
        try:
            # Create
            qualified_name = self._unique_qname("TestClassify")
            create_body = {
                "class": "NewOpenMetadataElementRequestBody",
                "typeName": "Referenceable",
                "properties": {
                    "class": "ReferenceableProperties",
                    "qualifiedName": qualified_name,
                }
            }
            guid = tm_client.create_metadata_element_in_store(create_body)

            # Classify
            classify_body = {
                "class": "ClassificationRequestBody",
                "properties": {
                    "class": "ClassificationProperties",
                }
            }
            tm_client.classify_metadata_element_in_store(guid, "Template", classify_body)
            print(f"Classified element {guid} as Template")

            # Declassify
            declassify_body = {
                "class": "ClassificationRequestBody"
            }
            tm_client.declassify_metadata_element_in_store(guid, "Template", declassify_body)
            print(f"Declassified element {guid}")

        finally:
            tm_client.close_session()

    def test_delete_metadata_element_in_store(self):
        """Test deleting a metadata element"""
        tm_client = TemplateManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
        tm_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
        try:
            # Create
            qualified_name = self._unique_qname("TestDelete")
            create_body = {
                "class": "NewOpenMetadataElementRequestBody",
                "typeName": "Referenceable",
                "properties": {
                    "class": "ReferenceableProperties",
                    "qualifiedName": qualified_name,
                }
            }
            guid = tm_client.create_metadata_element_in_store(create_body)

            # Delete
            delete_body = {
                "class": "DeleteElementRequestBody"
            }
            tm_client.delete_metadata_element_in_store(guid, delete_body)
            print(f"Deleted element {guid}")

        finally:
            tm_client.close_session()

    def test_create_related_elements(self):
        """Test creating related elements"""
        tm_client = TemplateManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
        tm_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
        try:
            # Create two elements
            q1 = self._unique_qname("Rel1")
            q2 = self._unique_qname("Rel2")
            g1 = tm_client.create_metadata_element_in_store({
                "class": "NewOpenMetadataElementRequestBody",
                "typeName": "Referenceable",
                "properties": {"class": "ReferenceableProperties", "qualifiedName": q1}
            })
            g2 = tm_client.create_metadata_element_in_store({
                "class": "NewOpenMetadataElementRequestBody",
                "typeName": "Referenceable",
                "properties": {"class": "ReferenceableProperties", "qualifiedName": q2}
            })

            # Create relationship
            rel_body = {
                "class": "NewRelatedElementsRequestBody",
                "relationshipTypeName": "Peer",
                "end1GUID": g1,
                "end2GUID": g2
            }
            rel_guid = tm_client.create_related_elements_in_store(rel_body)
            print(f"Created relationship {rel_guid}")
            assert rel_guid is not None

        finally:
            tm_client.close_session()

    def test_create_metadata_element_from_template(self):
        """Test creating a metadata element from template"""
        tm_client = TemplateManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
        tm_client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
        try:
            # Create template
            q1 = self._unique_qname("TemplateBase")
            guid = tm_client.create_metadata_element_in_store({
                "class": "NewOpenMetadataElementRequestBody",
                "typeName": "Referenceable",
                "properties": {"class": "ReferenceableProperties", "qualifiedName": q1}
            })
            tm_client.classify_metadata_element_in_store(guid, "Template", {"class": "ClassificationRequestBody"})

            # Create from template
            q2 = self._unique_qname("FromTemplate")
            from_template_body = {
                "class": "TemplateRequestBody",
                "templateGUID": guid,
                "replacementProperties": {
                    "class": "ReferenceableProperties",
                    "qualifiedName": q2
                }
            }
            new_guid = tm_client.create_metadata_element_from_template(from_template_body)
            print(f"Created from template: {new_guid}")
            assert new_guid is not None

        finally:
            tm_client.close_session()
