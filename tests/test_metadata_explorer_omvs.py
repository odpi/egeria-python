"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the classification manager view service class and methods.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import time

import pytest
import asyncio
import json
from rich import print, print_json
from rich.console import Console

from contextlib import nullcontext as does_not_raise

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

from pyegeria.core_omag_server_config import CoreServerConfig

from pyegeria.classification_manager_omvs import ClassificationManager
from pyegeria import MetadataExplorer
from tests.test_classification_manager_omvs import relationship_type

disable_ssl_warnings = True


console = Console()


def jprint(info, comment=None):
    if comment:
        print(comment)
    print(json.dumps(info, indent=2))


def valid_guid(guid):
    if (guid is None) or (type(guid) is not str):
        return False
    else:
        return True


class TestMetadataExplorer:
    good_view_server_1 = "view-server"
    platform_url = "https://localhost:9443"
    view_server = "view-server"
    user = "erinoverview"
    password = "secret"

    #
    ##
    #
    def test_get_metadata_guid_by_unique_name(self):
        name = "active-metadata-store"
        property_name = "name"
        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            response = m_client.get_metadata_guid_by_unique_name(name, property_name)

            if type(response) is list:
                print(f"\n\tElement count is: {len(response)}")
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is" + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_element_by_guid(self):
        # guid = "d11fd82f-49f4-4b81-ad42-d5012863cf39"
        # guid = "dcfd7e32-8074-4cdf-bdc5-9a6f28818a9d"
        guid = "58933d73-7f04-4899-99ce-bbd25826041a"  # a glossary term
        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            response = m_client.get_metadata_element_by_guid(guid)

            if type(response) is dict:
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is" + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_element_by_unique_name(self):
        name = "Metadata Access Server:active-metadata-store"
        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            response = m_client.get_metadata_element_by_unique_name(
                name, "qualifiedName"
            )

            if type(response) is dict:
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_metadata_element_history(self):
        guid = "d11fd82f-49f4-4b81-ad42-d5012863cf39"
        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            response = m_client.get_metadata_element_history(guid)

            if type(response) is list:
                print(f"\n\tElement count is: {len(response)}")
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_find_metadata_elements_with_string(self):
        body = {
            "class": "SearchStringRequestBody",
            "searchString": "ProcessL",
            "typeName": "ValidValueDefinition",
            "effectiveTime": None,
            "limitResultsByStatus": ["ACTIVE"],
            "asOfTime": None,
            "sequencingOrder": "CREATION_DATE_RECENT",
            "sequencingProperty": "",
        }

        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            response = m_client.find_metadata_elements_with_string(body, page_size=1000)

            if type(response) is list:
                print(f"\n\tElement count is: {len(response)}\n")
                print_json(data=response, indent=4)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_all_related_metadata_elements(self):
        # guid = "d11fd82f-49f4-4b81-ad42-d5012863cf39"
        guid = "30bfe79e-adf2-4fda-b9c5-9c86ad6b0d6c"  # sustainability glossary
        guid = "2d86e375-c31b-494d-9e73-a03af1370d81"  # Clinical trials project
        body = {
            "class": "ResultsRequestBody",
            "effectiveTime": None,
            "limitResultsByStatus": ["ACTIVE"],
            "asOfTime": None,
            "sequencingOrder": "CREATION_DATE_RECENT",
            "sequencingProperty": "",
        }

        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            response = m_client.get_all_related_metadata_elements(guid, body)

            if type(response) is list:
                print(f"\n\tElement count is: {len(response)}\n")
                print_json(data=response, indent=4)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_all_related_metadata_elements2(self):
        guid = "d11fd82f-49f4-4b81-ad42-d5012863cf39"

        body = {
            "class": "ResultsRequestBody",
            "effectiveTime": None,
            "limitResultsByStatus": ["ACTIVE"],
            "asOfTime": None,
            "sequencingOrder": "PROPERTY_ASCENDING",
            "sequencingProperty": "fileName",
        }

        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            response = m_client.get_all_related_metadata_elements(guid, body)

            if type(response) is list:
                print(f"\n\tElement count is: {len(response)}\n")
                print_json(data=response, indent=4)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_related_metadata_elements(self):
        guid = "d11fd82f-49f4-4b81-ad42-d5012863cf39"
        relationship_type = "SourcedFrom"
        body = {
            "class": "ResultsRequestBody",
            "effectiveTime": None,
            "limitResultsByStatus": ["ACTIVE"],
            "asOfTime": None,
            "sequencingOrder": "CREATION_DATE_RECENT",
            "sequencingProperty": "",
        }

        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            response = m_client.get_related_metadata_elements(
                guid, relationship_type, body
            )

            if type(response) is list:
                print(f"\n\tElement count is: {len(response)}\n")
                print_json(data=response, indent=4)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_all_metadata_element_relationships(self):
        end1_guid = "81467053-ec51-4b11-9ee7-95168f61b104"
        end2_guid = "3e7a0f56-a656-405a-a349-906b23969d4c"
        relationship_type = "SourcedFrom"
        body = {
            "class": "ResultsRequestBody",
            "effectiveTime": None,
            "limitResultsByStatus": ["ACTIVE"],
            "asOfTime": None,
            "sequencingOrder": "CREATION_DATE_RECENT",
            "sequencingProperty": "",
        }

        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            response = m_client.get_all_metadata_element_relationships(
                end1_guid, end2_guid, body
            )

            if type(response) is list:
                print(f"\n\tElement count is: {len(response)}\n")
                print_json(data=response, indent=4)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_metadata_element_relationships(self):
        end1_guid = "81467053-ec51-4b11-9ee7-95168f61b104"
        end2_guid = "3e7a0f56-a656-405a-a349-906b23969d4c"
        relationship_type = "TeamMembership"
        body = {
            "class": "ResultsRequestBody",
            "effectiveTime": None,
            "limitResultsByStatus": ["ACTIVE"],
            "asOfTime": None,
            "sequencingOrder": "CREATION_DATE_RECENT",
            "sequencingProperty": "",
        }

        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            response = m_client.get_metadata_element_relationships(
                end1_guid, end2_guid, relationship_type, body
            )

            if type(response) is list:
                print(f"\n\tElement count is: {len(response)}\n")
                print_json(data=response, indent=4)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_find_metadata_elements(self):
        """find metadata elements anchored to a specific element (active-metadata-store)"""
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
                                        "primitiveValue": "isd11fd82f-49f4-4b81-ad42-d5012863cf39",
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
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            response = m_client.find_metadata_elements(body)

            if type(response) is list:
                print(f"\n\tElement count is: {len(response)}\n")
                print_json(data=response, indent=4)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_find_metadata_elements_party(self):
        """find glossary elements containing party"""
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
                "matchCriteria": "ANY",
            },
        }

        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            response = m_client.find_metadata_elements(body)

            if type(response) is list:
                print(f"\n\tElement count is: {len(response)}\n")
                print_json(data=response, indent=4)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_find_relationships_between_elements(self):
        body = {
            "class": "FindRelationshipRequestBody",
            "relationshipTypeName": "CommunityMembership",
            "searchProperties": {
                "class": "SearchProperties",
                "conditions": [
                    {
                        "nestedConditions": {
                            "class": "SearchProperties",
                            "conditions": [
                                {
                                    "property": "membershipType",
                                    "operator": "EQ",
                                    "value": {
                                        "class": "PrimitiveTypePropertyValue",
                                        "typeName": "string",
                                        "primitiveValue": "Privacy",
                                    },
                                }
                            ],
                            "matchCriteria": "ALL",
                        }
                    }
                ],
                "matchCriteria": "ANY",
            },
            "effectiveTime": None,
            "limitResultsByStatus": ["ACTIVE"],
            "asOfTime": None,
            "sequencingOrder": "CREATION_DATE_RECENT",
            "sequencingProperty": "",
        }

        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            response = m_client.find_metadata_elements(body)

            if type(response) is list:
                print(f"\n\tElement count is: {len(response)}\n")
                print_json(data=response, indent=4)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_relationship_by_guid(self):
        guid = "c53a5670-08c1-46dc-afd1-bca25fe91e04"
        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            response = m_client.get_relationship_by_guid(guid)

            if type(response) is dict:
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_get_relationship_history(self):
        guid = "c53a5670-08c1-46dc-afd1-bca25fe91e04"
        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            response = m_client.get_relationship_history(guid)

            if type(response) is dict:
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()
