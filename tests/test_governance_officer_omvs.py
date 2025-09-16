"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the metadata explorer view service class and methods.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import json
import time

from pydantic import ValidationError
from rich import print, print_json
from rich.console import Console

from pyegeria._exceptions_new import print_validation_error
from pyegeria.models import SearchStringRequestBody

console = Console(width=200)
from unit_test._helpers import PLATFORM_URL, VIEW_SERVER, USER_ID, USER_PWD, require_local_server
import pytest

@pytest.fixture(autouse=True)
def _ensure_server():
    require_local_server()

from pyegeria import GovernanceOfficer, PyegeriaException, print_basic_exception
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.governance_officer import GovernanceOfficer

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
    platform_url = PLATFORM_URL
    view_server = VIEW_SERVER
    user = USER_ID
    password = USER_PWD

    #
    ##
    #


    def test_create_governance_definition(self):
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            display_name = "generic-gov-def-3"
            q_name = s_client.__create_qualified_name__("GovernanceDefinition",display_name)

            body ={
                    "class": "NewElementRequestBody",
                    "properties": {
                        "class": "GovernanceDefinitionProperties",
                        "typeName": "GovernanceDefinition",
                        "domainIdentifier": 0,
                        "qualifiedName": q_name,
                        "displayName": display_name,
                        "summary": "a third threat",
                        "description": "a third threat - but a bit longer",
                        "scope": "UK",
                        "importance": "Mild",
                        "implications": [],
                        "outcomes": [],
                        "results": []
                        },
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
            display_name = "generic-gov-strategy-2"
            q_name = s_client.__create_qualified_name__("GovernanceDefinition",display_name)

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
                    "qualifiedName": q_name,
                    # "description": "Have all the tech companies and governments beholden to me.",
                    # "versionIdentifier": "1.0",
                    # "effectiveFrom": None,
                    # "effectiveTo": None,
                    # "additionalProperties": None,
                    # "extendedProperties": None,
                    "typeName": "BusinessImperative",
                #     "domainIdentifier": 0,
                #     "documentIdentifier": None,
                    "summary": "Hegemony",
                    "scope": "InterGalactic",
                    "importance": "Somewhat",
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
                PyegeriaException
                ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
        finally:
            s_client.close_session()







    def test_update_governance_definition(self):
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            display_name = "Talmudic"
            qualified_name = "GovPrinciple::Talmudic"
            body = {
                      "class" : "UpdateElementRequestBody",
                      # "externalSourceGUID": "add guid here",
                      # "externalSourceName": "add qualified name here",
                      # "effectiveTime" : "{{$isoTimestamp}}",
                      "forLineage" : False,
                      "forDuplicateProcessing" : False,
                      "mergeUpdate" : True,
                      "properties": {
                        "class" : "GovernancePrincipleProperties",
                        "typeName" : "GovernancePrinciple",
                        "qualifiedName": qualified_name,
                        "displayName": display_name,
                        "description": "Somewhat more chaotic"
                      }
                    }

            start_time = time.perf_counter()
            guid = "fd95c9dc-c882-4c3f-8436-aa85e74276fb"
            s_client.update_governance_definition(guid,body)
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
            guid = "7b52707a-2b9b-4592-86c3-304f508b44bf"
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
        filter = "CC"
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            body = {
                "class": "SearchStringRequestBody",
                # "effective_time": None,
                # "limitResultsByStatus": ["ACTIVE"],
                # "asOfTime": "2025-07-06T07:20:40.038+00:00",
                # "metadataElementTypeName": ["BusinessImperative", "Regulation", "LicenseType", "GovernanceResponsibility",
                #                             "GovernanceApproach", "Certification Type", "Governance Principle"],
                # "metadataElementSubtypeNames": ["GovernancePrinciple","GovernanceStrategy","Regulation", "BusinessImperative"],
                "metadataElementSubtypeNames": ["GovernanceDriver"],
                "sequencingOrder": None,
                "sequencingProperty": None,
                "searchString": filter
                }
            body2 = SearchStringRequestBody(
                class_="SearchStringRequestBody",
                metadata_element_subtype_names=["GovernancePolicy", "GovernanceDriver", "BusinessImperative"],
                search_string="*",

                )
            start_time = time.perf_counter()
            response = s_client.find_governance_definitions(search_string=filter, body=body, output_format="DICT", output_format_set="Governance Definitions")
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
            response = s_client.find_governance_definitions(filter, output_format='DICT')
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
        guid = "fdec46ab-cf36-4029-85ee-755b9c2eb165"
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
        guid = "667c6480-a90a-4fd4-9022-8da646e203d2"
        try:
            s_client = GovernanceOfficer(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_gov_def_in_context(guid, output_format='REPORT')
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


