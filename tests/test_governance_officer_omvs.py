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

console = Console(width=200)

from pyegeria import GovernanceOfficer
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.governance_officer_omvs import GovernanceOfficer

disable_ssl_warnings = True


def jprint(info, comment=None):
    if comment:
        print(comment)
    print(json.dumps(info, indent=2))


def valid_guid(guid):
    if (guid is None) or (type(guid) is not str):
        return False
    else:
        return True


class TestGovernanceOfficer:
    platform_url = "https://localhost:9443"
    view_server = "qs-view-server"
    user = "erinoverview"
    password = "secret"

    #
    ##
    #


    def test_create_governance_definition(self):
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            title = "generic-gov-def-3"
            q_name = s_client.__create_qualified_name__("GovernanceDefinition",title)

            body ={
                    "class": "NewElementRequestBody",
                    "properties": {
                        "class": "GovernanceDefinitionProperties",
                        "typeName": "GovernanceDefinition",
                        "domainIdentifier": 0,
                        "documentIdentifier": q_name,
                        "title": title,
                        "summary": "a third threat",
                        "description": "a third threat - but a bit longer",
                        "scope": "UK",
                        "importance": "Mild",
                        "implications": [],
                        "outcomes": [],
                        "results": []
                        },
                    "initialStatus": "DRAFT"
                }

            start_time = time.perf_counter()
            response = s_client.create_governance_definition(body)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
                )
            if isinstance(response, (list, dict)):
                print_json(data=response)

            elif type(response) is str:
                print("\n\n\t Response is: " + response)

            assert True
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException,
                ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            s_client.close_session()

    def test_create_governance_strategy_definition(self):
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            title = "generic-gov-strategy-1"
            q_name = s_client.__create_qualified_name__("GovernanceDefinition",title)

            body ={
                "class": "NewElementRequestBody",
                # "externalSourceGUID": None,
                # "externalSourceName": None,
                # "effectiveTime": None,
                # "forLineage": False,
                # "forDuplicateProcessing": False,
                # "anchorGUID": None,
                # "isOwnAnchor": True,
                # "parentGUID": None,
                # "parentRelationshipTypeName": None,
                # "parentRelationshipProperties": None,
                # "parentAtEnd1": True,
                "properties": {
                    "class": "BusinessImperativeProperties",
                    "displayName": "World Domination",
                    "title": "sir junk",
                    "qualifiedName": "BusinessImperative::World Domination2",
                    # "description": "Have all the tech companies and governments beholden to me.",
                    # "versionIdentifier": "1.0",
                    # "effectiveFrom": None,
                    # "effectiveTo": None,
                    # "additionalProperties": None,
                    # "extendedProperties": None,
                    "typeName": "BusinessImperative"
                #     "domainIdentifier": 0,
                #     "documentIdentifier": None,
                #     "summary": "Hegemony",
                #     "scope": "InterGalactic",
                #     "importance": "Somewhat",
                #     "implications": [],
                #     "outcomes": [
                #         "Happiness"
                #     ],
                #     "results": [
                #         "Unknown"
                #     ]
                }
                # "initialStatus": "DRAFT"
            }


            start_time = time.perf_counter()
            response = s_client.create_governance_definition(body)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
                )
            if isinstance(response, (list, dict)):
                print_json(data=response)

            elif type(response) is str:
                print("\n\n\t Response is: " + response)

            assert True
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException,
                ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            s_client.close_session()







    def test_update_governance_definition(self):
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            display_name = "generic-gov-def-3"
            qualified_name = "GovernanceDefinition::generic-gov-def-3"
            body = {
                      "class" : "UpdateElementRequestBody",
                      # "externalSourceGUID": "add guid here",
                      # "externalSourceName": "add qualified name here",
                      # "effectiveTime" : "{{$isoTimestamp}}",
                      "forLineage" : False,
                      "forDuplicateProcessing" : False,
                      "properties": {
                        "class" : "GovernanceDefinitionProperties",
                        "typeName" : "GovernanceDefinition",
                        "documentIdentifier": qualified_name,
                        "title": display_name,
                        "description": "updated description"
                      }
                    }

            start_time = time.perf_counter()
            guid = "5964f9fe-6564-495e-a353-0f238b6a9828"
            s_client.update_governance_definition(guid,body, False)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds"
                )

            assert True
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException,
                ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            s_client.close_session()

    def test_delete_governance_definition(self):
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            guid = "794edf2a-f803-43d6-9292-6500b543cc85"
            # body = {
            #     "class": "MetadataSourceRequestBody",
            #     "externalSourceGUID": "add guid here",
            #     "externalSourceName": "add qualified name here",
            #     "effectiveTime": "{{$isoTimestamp}}",
            #     "forLineage": False,
            #     "forDuplicateProcessing": False
            #     }
            start_time = time.perf_counter()
            s_client.delete_governance_definition(guid)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds"
                )


            assert True
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException,
                ) as e:
            print_exception_response(e)

            assert False, "Invalid request"

        finally:
            s_client.close_session()

    def test_create_payload(self):
        body = {
                "class": "NewGovernanceDefinitionRequestBody",
                "externalSourceGUID": None,
                "externalSourceName": None,
                "effectiveTime": None,
                "forLineage": False,
                "forDuplicateProcessing": False,
                "anchorGUID": None,
                "isOwnAnchor": True,
                "parentGUID": None,
                "parentRelationshipTypeName": None,
                "parentRelationshipProperties": None,
                "parentAtEnd1": True,
                "properties": {
                    "class": "BusinessImperativeProperties",
                    "displayName": "World Domination",
                    "qualifiedName": "BusinessImperative::World Domination",
                    "description": "Have all the tech companies and governments beholden to me.",
                    "versionIdentifier": "1.0",
                    "effectiveFrom": None,
                    "effectiveTo": None,
                    "additionalProperties": None,
                    "extendedProperties": None,
                    "typeName": "BusinessImperative",
                    "domainIdentifier": 0,
                    "documentIdentifier": None,
                    "summary": "Hegemony",
                    "scope": "InterGalactic",
                    "importance": "Somewhat",
                    "implications": [],
                    "outcomes": [
                        "Happiness"
                    ],
                    "results": [
                        "Unknown"
                    ]
                },
                "initialStatus": "PROPOSED"
            }

    def test_delete_all_defs(self):
        s_client = GovernanceOfficer(
            self.view_server, self.platform_url, self.user, self.password
            )
        filter = "*"
        s_client.create_egeria_bearer_token()
        start_time = time.perf_counter()
        response = s_client.find_governance_definitions(filter, output_format='DICT')
        for item in response:
            s_client.delete_governance_definition(item['GUID'])
            print(f"Deleted {item['GUID']}")

    def test_find_governance_definitions(self):
        filter = "Approach"
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            body = {
                "class": "FilterRequestBody",
                # "effective_time": None,
                # "limitResultsByStatus": ["ACTIVE"],
                # "asOfTime": "2025-07-06T07:20:40.038+00:00",
                "sequencingOrder": None,
                "sequencingProperty": None,
                "filter": filter
                }
            start_time = time.perf_counter()
            response = s_client.find_governance_definitions(filter, output_format="JSON")
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
            )
            if isinstance(response, (list, dict)):
                print_json(data=response)

            elif type(response) is str:
                print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            s_client.close_session()

    def test_find_all_governance_definitions(self):

        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
            )
            filter = "*"
            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.find_governance_definitions(filter, output_format='LIST')
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
            )
            if isinstance(response, (list, dict)):
                print_json(data=response)

            elif type(response) is str:
                print("\n\n\t Response is: \n" + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            s_client.close_session()

    def test_get_gov_def_by_guid(self):
        guid = "e0b6721f-80dc-4342-ab83-ea556d4beff8"
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_governance_definition_by_guid(guid, output_format='JSON')
            duration = time.perf_counter() - start_time
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
            )
            if isinstance(response, (list, dict)):
                print_json(data=response)

            elif type(response) is str:
                print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            s_client.close_session()


    def test_get_gov_def_by_name(self):
        name = "A Regulation"
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_governance_definitions_by_name(name, output_format='DICT')
            duration = time.perf_counter() - start_time
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
            )
            if isinstance(response, (list, dict)):
                print_json(data=response)

            elif type(response) is str:
                print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            s_client.close_session()


    def test_get_gov_def_in_context(self):
        guid = "e0b6721f-80dc-4342-ab83-ea556d4beff8"
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_gov_def_in_context(guid, output_format='JSON')
            duration = time.perf_counter() - start_time
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
            )
            if isinstance(response, (list, dict)):
                print_json(data=response)

            elif type(response) is str:
                print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            s_client.close_session()



    def test_link_peer_definitions(self):
        rel_type_name = "GovernanceDriverLink"
        guid = "fdbedd27-2332-4fe5-b50c-9007238fd527"
        guid2 = "70e1ae07-fc8d-49c1-89de-582f671d2b65"
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            body = {
                "class": "RelationshipRequestBody",
                "properties": {
                    "class": "InformationSupplyChainLinkProperties",
                    "label": "a first label",
                    "description": "label description"
                    }
                }


            start_time = time.perf_counter()
            s_client.link_peer_definitions(guid, guid2, body)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds,"
            )

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            s_client.close_session()


    def test_unlink_peer_definitions(self):
        rel_type_name = "GovernanceDriverLink"
        guid = "fdbedd27-2332-4fe5-b50c-9007238fd527"
        guid2 = "70e1ae07-fc8d-49c1-89de-582f671d2b65"
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            body = {
                "class": "RelationshipRequestBody",
                "properties": {
                    "class": "InformationSupplyChainLinkProperties",
                    "label": "a first label",
                    "description": "label description"
                    }
                }


            start_time = time.perf_counter()
            s_client.detach_peer_definitions(guid, guid2, body)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds,"
            )

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            s_client.close_session()

    def test_link_design_to_implementation(self):
        guid1 = "5165e718-4a39-4aa4-98cb-8eb1d972cf3f"
        guid2 = "d026fbd6-709b-45d4-beec-f7a08764b5e2"
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            body = {
              "class" : "RelationshipRequestBody",
              "properties": {
                "class": "ImplementedByProperties",
                 "description": "checking to see it works"
              }
            }

            start_time = time.perf_counter()
            s_client.link_design_to_implementation(guid1,guid2, body)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds"
            )

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            s_client.close_session()

    def test_detach_design_to_implementation(self):
        guid1 = "5d552e92-0466-47f0-b609-ef45a7a3cef9"
        guid2 = "65ef0367-e69b-40e1-b6e8-4a00c12c06fc"
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            body = {
          "class" : "RelationshipRequestBody",
          "properties": {
              "class": "ImplementedByProperties",
             "designStep": "imp1",
             "description": "checking to see it works"
          }
        }

            start_time = time.perf_counter()
            s_client.detach_design_from_implementation(guid1,guid2, body)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds"
            )

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            s_client.close_session()


