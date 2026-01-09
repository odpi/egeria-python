"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the TemplateManager class and methods from template_manager_omvs.py

A running Egeria environment is needed to run these tests.
"""
import pytest
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
from pyegeria.egeria_client import Egeria
from pyegeria.core.logging_configuration import config_logging, init_logging

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

    def test_template_classification_lifecycle(self):
        """Test adding and removing template classifications"""
        client = Egeria(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
        
        try:
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            pytest.skip(f"Could not authenticate: {e}")
        
        try:
            # 1. Create a base element using MetadataExpert
            qname = self._unique_qname("TemplateClassLifecycle")
            guid = client.expert.create_metadata_element({
                "class": "NewOpenMetadataElementRequestBody",
                "typeName": "Referenceable",
                "properties": {
                    "class": "ElementProperties",
                    "propertyValueMap": {
                        "qualifiedName": {"class": "PrimitiveTypePropertyValue", "typeName": "string", "primitiveValue": qname}
                    }
                }
            })
            assert guid is not None

            # 2. Add Template classification
            client.templates.add_template_classification(guid, {
                "class": "NewClassificationRequestBody",
                "properties": {
                    "class": "TemplateProperties",
                    "displayName": "Test Template"
                }
            })
            print(f"Added template classification to {guid}")

            # 3. Remove Template classification
            client.templates.remove_template_classification(guid)
            print(f"Removed template classification from {guid}")

            # 4. Add Template Substitute classification
            client.templates.add_template_substitute_classification(guid, {
                "class": "NewClassificationRequestBody"
            })
            print(f"Added template substitute classification to {guid}")

            # 5. Remove Template Substitute classification
            client.templates.remove_template_substitute_classification(guid)
            print(f"Removed template substitute classification from {guid}")

            # Cleanup
            client.expert.delete_metadata_element(guid, {"class": "OpenMetadataDeleteRequestBody"})

        finally:
            client.close_session()

    def test_template_relationship_lifecycle(self):
        """Test linking and detaching template relationships"""
        client = Egeria(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_1)
        
        try:
            client.create_egeria_bearer_token(self.good_user_1, USER_PWD)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            pytest.skip(f"Could not authenticate: {e}")
        
        try:
            # 1. Create two elements
            q1 = self._unique_qname("Element")
            q2 = self._unique_qname("Template")
            
            e_guid = client.expert.create_metadata_element({
                "class": "NewOpenMetadataElementRequestBody",
                "typeName": "Referenceable",
                "properties": {"class": "ElementProperties", "propertyValueMap": {"qualifiedName": {"class": "PrimitiveTypePropertyValue", "typeName": "string", "primitiveValue": q1}}}
            })
            t_guid = client.expert.create_metadata_element({
                "class": "NewOpenMetadataElementRequestBody",
                "typeName": "Referenceable",
                "properties": {"class": "ElementProperties", "propertyValueMap": {"qualifiedName": {"class": "PrimitiveTypePropertyValue", "typeName": "string", "primitiveValue": q2}}}
            })

            # 2. Link Sourced From
            client.templates.link_sourced_from(e_guid, t_guid, {
                "class": "NewRelationshipRequestBody",
                "relationshipProperties": {"class": "SourceFromProperties", "sourceVersionNumber": 1}
            })
            print(f"Linked {e_guid} as sourced from {t_guid}")

            # 3. Detach Sourced From
            client.templates.detach_sourced_from(e_guid, t_guid)
            print(f"Detached sourced from relationship between {e_guid} and {t_guid}")

            # 4. Link Catalog Template
            client.templates.link_catalog_template(e_guid, t_guid, {
                "class": "NewRelationshipRequestBody",
                "relationshipProperties": {"class": "CatalogTemplateProperties"}
            })
            print(f"Linked {e_guid} to catalog template {t_guid}")

            # 5. Detach Catalog Template
            client.templates.detach_catalog_template(e_guid, t_guid)
            print(f"Detached catalog template relationship between {e_guid} and {t_guid}")

            # Cleanup
            client.expert.delete_metadata_element(e_guid, {"class": "OpenMetadataDeleteRequestBody"})
            client.expert.delete_metadata_element(t_guid, {"class": "OpenMetadataDeleteRequestBody"})

        finally:
            client.close_session()
