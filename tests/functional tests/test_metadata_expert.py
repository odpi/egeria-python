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

    def test_get_metadata_guid_by_unique_name(self, expert_client):
        """Get a GUID by unique name."""
        try:
            response = expert_client.get_metadata_guid_by_unique_name(
                "Open Metadata Digital Product Glossary", "displayName"
            )
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_get_element_by_guid(self, expert_client):
        """Get a metadata element by its GUID."""
        guid = '5dc94eb4-5cf9-41f5-b24c-cfb8fc7e1772'
        try:
            response = expert_client.get_metadata_element_by_guid(guid)
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_get_element_graph(self, expert_client):
        """Get an anchored element graph (full)."""
        guid = "5dc94eb4-5cf9-41f5-b24c-cfb8fc7e1772"
        try:
            response = expert_client.get_anchored_element_graph(guid, mermaid_only=False)
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_get_element_mermaid_graph(self, expert_client):
        """Get an anchored element graph (mermaid only)."""
        guid = "5dc94eb4-5cf9-41f5-b24c-cfb8fc7e1772"
        try:
            response = expert_client.get_anchored_element_graph(guid, mermaid_only=True)
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_get_element_by_unique_name(self, expert_client):
        """Get a metadata element by its unique (qualified) name."""
        try:
            response = expert_client.get_metadata_element_by_unique_name(
                "GlossaryTerm::CO2 Emission Scope", "qualifiedName"
            )
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_get_metadata_element_history(self, expert_client):
        """Get the history of a metadata element."""
        guid = "5dc94eb4-5cf9-41f5-b24c-cfb8fc7e1772"
        try:
            response = expert_client.get_element_history(guid)
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_find_metadata_elements_with_string(self, expert_client):
        """Find metadata elements matching a search string."""
        body = {
            "class": "SearchStringRequestBody",
            "searchString": "Emission",
            "typeName": "GlossaryTerm",
            "effectiveTime": None,
            "limitResultsByStatus": [],
            "asOfTime": None,
            "sequencingOrder": "CREATION_DATE_RECENT",
            "sequencingProperty": "",
        }
        try:
            response = expert_client.find_metadata_elements_with_string(
                "Emission", body=body, page_size=1000
            )
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_get_all_related_metadata_elements(self, expert_client):
        """Get all related elements for a given GUID."""
        guid = "43e630ec-2afb-40fb-a0ba-c08e0c6215dc"
        body = {
            "class": "ResultsRequestBody",
            "effectiveTime": None,
            "limitResultsByStatus": ["ACTIVE"],
            "asOfTime": None,
            "sequencingOrder": "CREATION_DATE_RECENT",
            "sequencingProperty": "",
            "mermaidOnly": False,
        }
        try:
            response = expert_client.get_all_related_elements(guid, body, mermaid_only=False)
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_get_all_related_metadata_elements_mermaid(self, expert_client):
        """Get all related elements for a given GUID (mermaid only)."""
        guid = "1f71e403-1187-4f03-a1dd-ae7dc105f06f"
        body = {
            "class": "ResultsRequestBody",
            "effectiveTime": None,
            "limitResultsByStatus": ["ACTIVE"],
            "asOfTime": None,
            "sequencingOrder": "PROPERTY_ASCENDING",
            "sequencingProperty": "fileName",
        }
        try:
            response = expert_client.get_all_related_elements(guid, body, mermaid_only=True)
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_get_related_metadata_elements(self, expert_client):
        """Get related elements of a specific relationship type."""
        guid = "a2c7378b-289d-49e2-92eb-cf5e72822d1f"
        body = {
            "class": "ResultsRequestBody",
            "effectiveTime": None,
            "limitResultsByStatus": ["ACTIVE"],
            "asOfTime": None,
            "sequencingOrder": "CREATION_DATE_RECENT",
            "sequencingProperty": "",
        }
        try:
            response = expert_client.get_related_metadata_elements(
                guid, "EngineActionRequestSource", body, mermaid_only=False
            )
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_get_all_metadata_element_relationships(self, expert_client):
        """Get all relationships between two elements."""
        end1_guid = "81467053-ec51-4b11-9ee7-95168f61b104"
        end2_guid = "3e7a0f56-a656-405a-a349-906b23969d4c"
        body = {
            "class": "ResultsRequestBody",
            "effectiveTime": None,
            "limitResultsByStatus": ["ACTIVE"],
            "asOfTime": None,
            "sequencingOrder": "CREATION_DATE_RECENT",
            "sequencingProperty": "",
        }
        try:
            response = expert_client.get_all_metadata_element_relationships(
                end1_guid, end2_guid, body
            )
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_get_metadata_element_relationships(self, expert_client):
        """Get relationships of a specific type between two elements."""
        end1_guid = "81467053-ec51-4b11-9ee7-95168f61b104"
        end2_guid = "3e7a0f56-a656-405a-a349-906b23969d4c"
        body = {
            "class": "ResultsRequestBody",
            "effectiveTime": None,
            "limitResultsByStatus": ["ACTIVE"],
            "asOfTime": None,
            "sequencingOrder": "CREATION_DATE_RECENT",
            "sequencingProperty": "",
        }
        try:
            response = expert_client.get_metadata_element_relationships(
                end1_guid, end2_guid, "TeamMembership", body
            )
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_find_metadata_elements(self, expert_client):
        """Find metadata elements anchored to active-metadata-store."""
        body = {
            "class": "FindRequestBody",
            "matchClassifications": {
                "class": "SearchClassifications",
                "conditions": [
                    {
                        "name": "Anchors",
                        "searchProperties": {
                            "class": "SearchProperties",
                            "conditions": [
                                {
                                    "property": "anchorGUID",
                                    "operator": "EQ",
                                    "value": {
                                        "class": "PrimitiveTypePropertyValue",
                                        "typeName": "string",
                                        "primitiveValue": "a3603c04-3697-49d1-ad79-baf3ea3db61f",
                                    },
                                }
                            ],
                            "matchCriteria": "ALL",
                        },
                    }
                ],
                "matchCriteria": "ANY",
            },
        }
        try:
            response = expert_client.find_metadata_elements(body)
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_find_metadata_elements_party(self, expert_client):
        """Find glossary elements containing 'party'."""
        body = {
            "class": "FindRequestBody",
            "searchProperties": {
                "class": "SearchProperties",
                "conditions": [
                    {
                        "property": "description",
                        "operator": "LIKE",
                        "value": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveValue": "party",
                        },
                    },
                    {
                        "property": "displayName",
                        "operator": "LIKE",
                        "value": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveValue": "party",
                        },
                    },
                    {
                        "property": "summary",
                        "operator": "LIKE",
                        "value": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveValue": "party",
                        },
                    },
                ],
                "matchCriteria": "ANY",
            },
            "matchClassifications": {
                "class": "SearchClassifications",
                "conditions": [
                    {
                        "name": "Anchors",
                        "searchProperties": {
                            "class": "SearchProperties",
                            "conditions": [
                                {
                                    "property": "anchorDomainName",
                                    "operator": "EQ",
                                    "value": {
                                        "class": "PrimitiveTypePropertyValue",
                                        "typeName": "string",
                                        "primitiveValue": "Glossary",
                                    },
                                }
                            ],
                            "matchCriteria": "ALL",
                        },
                    }
                ],
                "matchCriteria": "ALL",
            },
        }
        try:
            response = expert_client.find_metadata_elements(body, page_size=1000)
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_find_metadata_elements_anchored_mdr(self, expert_client):
        """Find metadata elements anchored to the active-metadata-store SoftwareServer entity."""
        active_metadata_store = "929ea364-cead-456d-b9f1-1016202196ed"
        body = {
            "class": "FindRequestBody",
            "matchClassifications": {
                "class": "SearchClassifications",
                "conditions": [
                    {
                        "name": "Anchors",
                        "searchProperties": {
                            "class": "SearchProperties",
                            "conditions": [
                                {
                                    "property": "anchorGUID",
                                    "operator": "EQ",
                                    "value": {
                                        "class": "PrimitiveTypePropertyValue",
                                        "typeName": "string",
                                        "primitiveValue": active_metadata_store,
                                    },
                                }
                            ],
                            "matchCriteria": "ALL",
                        },
                    }
                ],
                "matchCriteria": "ALL",
            },
        }
        try:
            response = expert_client.find_metadata_elements(body)
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_find_glossary_terms_cim(self, expert_client):
        """Find GlossaryTerm elements anchored to the CIM glossary."""
        cim_glossary_guid = "ab84bad2-67f0-4ec8-b0e3-76e638ec9f63"
        body = {
            "class": "FindRequestBody",
            "metadataElementTypeName": "GlossaryTerm",
            "matchClassifications": {
                "class": "SearchClassifications",
                "conditions": [
                    {
                        "name": "Anchors",
                        "searchProperties": {
                            "class": "SearchProperties",
                            "conditions": [
                                {
                                    "property": "anchorGUID",
                                    "operator": "EQ",
                                    "value": {
                                        "class": "PrimitiveTypePropertyValue",
                                        "typeName": "string",
                                        "primitiveValue": cim_glossary_guid,
                                    },
                                }
                            ],
                            "matchCriteria": "ALL",
                        },
                    }
                ],
                "matchCriteria": "ALL",
            },
        }
        try:
            response = expert_client.find_metadata_elements(body, page_size=100)
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_find_relationships_between_elements(self, expert_client):
        """Find ResourceList relationships with a specific resourceUse value."""
        body = {
            "class": "FindRelationshipRequestBody",
            "relationshipTypeName": "ResourceList",
            "searchProperties": {
                "class": "SearchProperties",
                "conditions": [
                    {
                        "property": "resourceUse",
                        "operator": "EQ",
                        "value": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveValue": "Survey Resource",
                        },
                    }
                ],
                "matchCriteria": "ALL",
            },
            "limitResultsByStatus": ["ACTIVE"],
            "sequencingOrder": "CREATION_DATE_RECENT",
            "sequencingProperty": "",
        }
        try:
            response = expert_client.find_relationships_between_elements(body, mermaid_only=False)
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_get_relationship_by_guid(self, expert_client):
        """Get a relationship by its GUID."""
        guid = "dbda2d45-47be-43bd-a5a3-2bde11349cff"
        try:
            response = expert_client.get_relationship_by_guid(guid)
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")

    def test_get_relationship_history(self, expert_client):
        """Get the history of a relationship by its GUID."""
        guid = "dbda2d45-47be-43bd-a5a3-2bde11349cff"
        try:
            response = expert_client.get_relationship_history(guid)
            print(f"\nResponse type: {type(response).__name__}")
            if isinstance(response, (dict, list, str)):
                print(response)
        except PyegeriaConnectionException:
            pytest.skip("No Egeria server running")
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")
