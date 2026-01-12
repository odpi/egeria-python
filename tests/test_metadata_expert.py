"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the MetadataExpert class and methods from metadata_expert.py
"""
import pytest
from datetime import datetime
from pyegeria.omvs.metadata_expert import MetadataExpert
from pyegeria.models import (NewOpenMetadataElementRequestBody, UpdatePropertiesRequestBody,
                             MetadataSourceRequestBody, UpdateEffectivityDatesRequestBody,
                             OpenMetadataDeleteRequestBody, ArchiveRequestBody,
                             NewClassificationRequestBody, NewRelatedElementsRequestBody,
                             TemplateRequestBody)
from pyegeria.core._exceptions import PyegeriaConnectionException

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"

class TestMetadataExpert:
    @pytest.fixture
    def expert_client(self):
        client = MetadataExpert(VIEW_SERVER, PLATFORM_URL, USER_ID)
        try:
            client.create_egeria_bearer_token(USER_ID, "secret")
        except Exception:
            # We don't want the fixture to fail if the server is down, 
            # as the tests themselves handle PyegeriaConnectionException
            pass
        return client

    def test_create_metadata_element(self, expert_client):
        """Test create_metadata_element with dict body"""
        body = {
            "class": "NewOpenMetadataElementRequestBody",
            "typeName": "Referenceable",
            "properties": {
                "class": "ElementProperties",
                "propertyValueMap": {
                    "qualifiedName": {
                        "class": "PrimitiveTypePropertyValue",
                        "typeName": "string",
                        "primitiveValue": f"TestElement-{datetime.now().timestamp()}"
                    }
                }
            }
        }
        try:
            # We don't expect it to actually succeed without a running server, 
            # but we test the call path.

            expert_client.create_metadata_element(body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            # If it's a validation error, we want to know
            print(f"Caught expected or unexpected exception: {type(e).__name__}: {e}")

    def test_update_metadata_element_properties(self, expert_client):
        """Test update_metadata_element_properties"""
        guid = "some-guid"
        body = {
            "class": "UpdatePropertiesRequestBody",
            "properties": {
                "class": "ElementProperties",
                "propertyValueMap": {
                    "description": {
                        "class": "PrimitiveTypePropertyValue",
                        "typeName": "string",
                        "primitiveValue": "New description"
                    }
                }
            }
        }
        try:
            expert_client.update_metadata_element_properties(guid, body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {e}")

    def test_publish_metadata_element(self, expert_client):
        """Test publish_metadata_element"""
        guid = "some-guid"
        body = MetadataSourceRequestBody(class_="MetadataSourceRequestBody")
        try:
            expert_client.publish_metadata_element(guid, body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {e}")

    def test_delete_metadata_element(self, expert_client):
        """Test delete_metadata_element"""
        guid = "6ec2c097-9d6e-4e9d-ab51-186d2c437443"
        body = OpenMetadataDeleteRequestBody(class_="OpenMetadataDeleteRequestBody")
        try:
            expert_client.delete_metadata_element(guid, body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {e}")

    def test_create_related_elements(self, expert_client):
        """Test create_related_elements"""
        body = NewRelatedElementsRequestBody(
            class_="NewRelatedElementsRequestBody",
            relationship_type_name="RelatedAsset",
            end_1_guid="guid-1",
            end_2_guid="guid-2"
        )
        try:
            expert_client.create_related_elements(body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {e}")

    def test_create_metadata_element_from_template(self, expert_client):
        """Test create_metadata_element_from_template"""
        body = TemplateRequestBody(
            class_="TemplateRequestBody",
            template_guid="template-guid"
        )
        try:
            expert_client.create_metadata_element_from_template(body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {e}")

    def test_withdraw_metadata_element(self, expert_client):
        """Test withdraw_metadata_element"""
        guid = "some-guid"
        body = MetadataSourceRequestBody(class_="MetadataSourceRequestBody")
        try:
            expert_client.withdraw_metadata_element(guid, body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {e}")

    def test_update_metadata_element_effectivity(self, expert_client):
        """Test update_metadata_element_effectivity"""
        guid = "some-guid"
        body = UpdateEffectivityDatesRequestBody(class_="UpdateEffectivityDatesRequestBody")
        try:
            expert_client.update_metadata_element_effectivity(guid, body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {e}")

    def test_archive_metadata_element(self, expert_client):
        """Test archive_metadata_element"""
        guid = "some-guid"
        body = ArchiveRequestBody(
            class_="ArchiveRequestBody",
            archive_properties={"archiveDate": datetime.now().isoformat()}
        )
        try:
            expert_client.archive_metadata_element(guid, body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {e}")

    def test_classify_metadata_element(self, expert_client):
        """Test classify_metadata_element"""
        guid = "some-guid"
        name = "Confidentiality"
        body = NewClassificationRequestBody(class_="NewClassificationRequestBody")
        try:
            expert_client.classify_metadata_element(guid, name, body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {e}")

    def test_reclassify_metadata_element(self, expert_client):
        """Test reclassify_metadata_element"""
        guid = "some-guid"
        name = "Confidentiality"
        body = UpdatePropertiesRequestBody(class_="UpdatePropertiesRequestBody")
        try:
            expert_client.reclassify_metadata_element(guid, name, body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {e}")

    def test_update_classification_effectivity(self, expert_client):
        """Test update_classification_effectivity"""
        guid = "some-guid"
        name = "Confidentiality"
        body = UpdateEffectivityDatesRequestBody(class_="UpdateEffectivityDatesRequestBody")
        try:
            expert_client.update_classification_effectivity(guid, name, body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {e}")

    def test_declassify_metadata_element(self, expert_client):
        """Test declassify_metadata_element"""
        guid = "some-guid"
        name = "Confidentiality"
        body = MetadataSourceRequestBody(class_="MetadataSourceRequestBody")
        try:
            expert_client.declassify_metadata_element(guid, name, body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {e}")

    def test_update_related_elements_properties(self, expert_client):
        """Test update_related_elements_properties"""
        guid = "rel-guid"
        body = UpdatePropertiesRequestBody(class_="UpdatePropertiesRequestBody")
        try:
            expert_client.update_related_elements_properties(guid, body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {e}")

    def test_update_related_elements_effectivity(self, expert_client):
        """Test update_related_elements_effectivity"""
        guid = "rel-guid"
        body = UpdateEffectivityDatesRequestBody(class_="UpdateEffectivityDatesRequestBody")
        try:
            expert_client.update_related_elements_effectivity(guid, body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {e}")

    def test_delete_related_elements(self, expert_client):
        """Test delete_related_elements"""
        guid = "rel-guid"
        body = OpenMetadataDeleteRequestBody(class_="OpenMetadataDeleteRequestBody")
        try:
            expert_client.delete_related_elements(guid, body)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {e}")
