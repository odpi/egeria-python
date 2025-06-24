"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the metadata explorer view service class and methods.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import json
import time

from rich import print, print_json
from rich.console import Console

from pyegeria import MetadataExplorer
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

disable_ssl_warnings = True

active_metadata_store = "929ea364-cead-456d-b9f1-1016202196ed"

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
    view_server = "qs-view-server"
    user = "erinoverview"
    password = "secret"

    #
    ##
    #
    def test_get_metadata_guid_by_unique_name(self):
        name = "Command"
        property_name = "displayName"
        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_metadata_guid_by_unique_name(name, property_name)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
            )
            if type(response) is list:
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

    # active-metadata-store is a3603c04-3697-49d1-ad79-baf3ea3db61f
    def test_get_element_by_guid(self):
        # guid = "d11fd82f-49f4-4b81-ad42-d5012863cf39"
        # guid = "dcfd7e32-8074-4cdf-bdc5-9a6f28818a9d"
        guid = '5539a643-875b-450c-adc1-aba38912d822'  # a glossary term
        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_metadata_element_by_guid(guid)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
            )

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

    def test_get_element_graph(self):
        guid = "43e630ec-2afb-40fb-a0ba-c08e0c6215dc"
        # guid = "58933d73-7f04-4899-99ce-bbd25826041a"  # a glossary term
        # guid = "dcfd7e32-8074-4cdf-bdc5-9a6f28818a9d"
        # guid = "58933d73-7f04-4899-99ce-bbd25826041a"  # a glossary term
        # guid = "f28a154b-ecdc-49b1-bfac-29da9d44fb99"
        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_anchored_metadata_element_graph(
                guid, mermaid_only=False
            )
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
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

    def test_get_element_mermaid_graph(self):
        guid = "58933d73-7f04-4899-99ce-bbd25826041a"  # a glossary term
        # guid = "d11fd82f-49f4-4b81-ad42-d5012863cf39"
        # guid = "dcfd7e32-8074-4cdf-bdc5-9a6f28818a9d"
        # guid = "58933d73-7f04-4899-99ce-bbd25826041a"  # a glossary term
        # guid = "f28a154b-ecdc-49b1-bfac-29da9d44fb99"
        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            # response = m_client.get_metadata_element_mermaid_graph(guid)
            response = m_client.get_metadata_element_graph(guid, mermaid_only=True)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
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

    def test_get_element_by_unique_name(self):
        name = "Metadata Access Server:active-metadata-store"
        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_metadata_element_by_unique_name(
                name, "qualifiedName"
            )
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
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
        guid = "929ea364-cead-456d-b9f1-1016202196ed"  # active-metadata-store
        # guid = "a3603c04-3697-49d1-ad79-baf3ea3db61f"  # kv - active-metadata-store
        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_metadata_element_history(guid)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
            )

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
            "searchString": None,
            "typeName": "DataStructure",
            "effectiveTime": None,
            "limitResultsByStatus": [],
            "asOfTime": None,
            "sequencingOrder": "CREATION_DATE_RECENT",
            "sequencingProperty": "",
        }

        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.find_metadata_elements_with_string(body, page_size=1000)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
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

    def test_get_all_related_metadata_elements(self):
        guid = "43e630ec-2afb-40fb-a0ba-c08e0c6215dc"
        # guid = "d11fd82f-49f4-4b81-ad42-d5012863cf39"
        # guid = "30bfe79e-adf2-4fda-b9c5-9c86ad6b0d6c"  # sustainability glossary
        # guid = "2d86e375-c31b-494d-9e73-a03af1370d81"  # Clinical trials project
        body = {
            "class": "ResultsRequestBody",
            "effectiveTime": None,
            "limitResultsByStatus": ["ACTIVE"],
            "asOfTime": None,
            "sequencingOrder": "CREATION_DATE_RECENT",
            "sequencingProperty": "",
            "mermaidOnly": False
        }

        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_all_related_metadata_elements(
                guid, body, mermaid_only=False
            )
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
            )

            if isinstance(response, (dict, list)):
                print(f"\n\tElement count is: {len(response)}\n")
                print_json(data=response, indent=4)
            elif type(response) is str:
                console.print("\n\n\t Response is:\n " + response)

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
        guid = "1f71e403-1187-4f03-a1dd-ae7dc105f06f"
        # guid = "a3603c04-3697-49d1-ad79-baf3ea3db61f"  # kv - active-metadata-store
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
            start_time = time.perf_counter()
            response = m_client.get_all_related_metadata_elements(
                guid, body, mermaid_only=True
            )
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
            )

            if isinstance(response, (dict, list)):
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
        guid = "a2c7378b-289d-49e2-92eb-cf5e72822d1f"
        # guid = "a3603c04-3697-49d1-ad79-baf3ea3db61f"  # kv - active-metadata-store
        relationship_type = "EngineActionRequestSource"
        body = {
            "class": "ResultsRequestBody",
            "effectiveTime": None,
            "limitResultsByStatus": ["ACTIVE"],
            "asOfTime": None,
            "sequencingOrder": "CREATION_DATE_RECENT",
            "sequencingProperty": ""
        }

        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_related_metadata_elements(
                guid, relationship_type, body, mermaid_only=False
            )
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
            )

            if isinstance(response, (list, dict)):
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
            start_time = time.perf_counter()
            response = m_client.get_all_metadata_element_relationships(
                end1_guid, end2_guid, body
            )
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
            )

            if isinstance(response, (list, dict)):
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
            start_time = time.perf_counter()
            response = m_client.get_metadata_element_relationships(
                end1_guid, end2_guid, relationship_type, body
            )
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
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
                                        # "primitiveValue": "d11fd82f-49f4-4b81-ad42-d5012863cf39",
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
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.find_metadata_elements(body)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
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

    def test_find_metadata_elements_party(self):
        """find glossary elements containing party"""
        page_size = 1000
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
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.find_metadata_elements(body, page_size=page_size)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Page Size {page_size}, Element count is {len(response)}"
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

    def test_find_metadata_elements_anchored_mdr(self):
        """findMetadataElements anchored to the SoftwareServer entity for active-metadata-store"""
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
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.find_metadata_elements(body)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
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

    def test_find_glossary_terms_cim(self):
        """findMetadataElements anchored to the SoftwareServer entity for active-metadata-store"""
        page_size = 100
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
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.find_metadata_elements(body, page_size=page_size)
            duration = time.perf_counter() - start_time

            console.print(
                f"\nDuration was {duration:.2f} seconds,  Page Size {page_size}, Element count is {len(response)}\n"
            )

            if type(response) is list:
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
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.find_relationships_between_elements(
                body, mermaid_only=False
            )
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
            )

            if isinstance(response, dict):
                print(f"\n\tElement count is: {len(response)}\n")
                print_json(data=response["elementList"], indent=4)
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
        guid = "dbda2d45-47be-43bd-a5a3-2bde11349cff"
        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_relationship_by_guid(guid)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
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

    def test_get_relationship_history(self):
        guid = "dbda2d45-47be-43bd-a5a3-2bde11349cff"
        try:
            m_client = MetadataExplorer(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_relationship_history(guid)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
            )

            if isinstance(response, (list, dict)):
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
