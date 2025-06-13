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

from pyegeria import SolutionArchitect
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

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


class TestSolutionArchitect:
    good_view_server_1 = "view-server"
    platform_url = "https://localhost:9443"
    view_server = "qs-view-server"
    user = "erinoverview"
    password = "secret"

    #
    ##
    #


    def test_create_info_supply_chains(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            display_name = "my_first_supply_chain"
            q_name = s_client.__create_qualified_name__("InformationSupplyChain",display_name)
            body = {
                "class": "NewInformationSupplyChainRequestBody",
                "properties": {
                    "class": "InformationSupplyChainProperties",
                    "displayName": display_name,
                    "qualifiedName": q_name
                    }
                }
            start_time = time.perf_counter()
            response = s_client.create_info_supply_chain(body)
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

    def test_update_info_supply_chains(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()

            body = {
              "class" : "UpdateInformationSupplyChainRequestBody",
              "properties": {
                  "class": "InformationSupplyChainProperties",
                  "description": "updated description",
                  "scope": "updated scope"
              }
            }
            start_time = time.perf_counter()
            guid = "ef1ce8f0-41a0-4be1-ac6b-a6febfea125e"
            s_client.update_info_supply_chain(guid,body, False)
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

    def test_delete_info_supply_chains(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            guid = "1f71e403-1187-4f03-a1dd-ae7dc105f06f"
            # body = {
            #     "class": "NewInformationSupplyChainRequestBody",
            #     "properties": {
            #         "displayName": display_name,
            #         "qualifiedName": q_name
            #         }
            #     }
            start_time = time.perf_counter()
            response = s_client.delete_info_supply_chain(guid)
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

    def test_find_information_supply_chains(self):
        filter_string = "*"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.find_information_supply_chains(filter_string, output_format='DICT')
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

    def test_get_information_supply_chain_by_guid(self):
        guid = "a7981a48-bd4a-480d-ba63-6584cddad153"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_info_supply_chain_by_guid(guid, output_format='JSON')
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


    def test_get_information_supply_chain_by_name(self):
        name = "InformationSupplyChain::Clinical Trial Subject Onboarding"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_info_supply_chain_by_name(name)
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


    def test_find_information_supply_chains_body(self):
        filter = "Clinical"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            body = {
                # "effective_time": None,
                # "limitResultsByStatus": ["ACTIVE"],
                "asOfTime": "2025-04-07T07:20:40.038+00:00",
                "sequencingOrder": None,
                "sequencingProperty": None,
                "filter": filter
                }
            start_time = time.perf_counter()
            response = s_client.find_information_supply_chains(filter, body=body)
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

    def test_find_all_information_supply_chains(self):

        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.find_all_information_supply_chains(output_format='DICT')
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

    def test_create_information_supply_chain_segment(self):
        name = "sell to the highest bidder2"
        guid = "39a035f0-3b2b-45fe-adb8-ee8a19581f6a"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            q_name = s_client.__create_qualified_name__("InformationSupplyChainSegment",name)
            body = {
                "class": "InformationSupplyChainSegmentRequestBody",
                "properties": {
                    "class": "InformationSupplyChainSegmentProperties",
                    "qualifiedName": q_name,
                    "displayName": name,
                    "description": "trumpian description",
                    "scope": "worldwide",
                    "integrationStyle": "style"
                    }
                }


            start_time = time.perf_counter()
            response = s_client.create_info_supply_chain_segment(guid, body)
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

    def test_get_information_supply_chain_segment_by_guid(self):
        segment_guid = "242eca0f-cdcf-4df3-b3fc-e485d62fd422"
        supply_chain_guid = "26834888-3ddf-4eb2-a8bb-bbb321579f94"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_info_supply_chain_segment_by_guid(segment_guid,supply_chain_guid)
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

    def test_link_segments(self):
        segment1_guid = "242eca0f-cdcf-4df3-b3fc-e485d62fd422"
        segment2_guid = "db493e08-86ed-4061-b4fe-587b58aa1793"
        body = {
             "class" : "InformationSupplyChainLinkRequestBody",
              # "externalSourceGUID": "add guid here",
              # "externalSourceName": "add qualified name here",
              # "effectiveTime" : "{{$isoTimestamp}}",
              # "forLineage" : false,
              # "forDuplicateProcessing" : false,
              "properties": {
                "class": "InformationSupplyChainLinkProperties",
                # "label": "my segment label"
                # "description": "an arc description",
                # "effectiveFrom": "{{$isoTimestamp}}",
                # "effectiveTo": "{{$isoTimestamp}}"
              }
            }
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()


            s_client.link_info_supply_chain_segments(segment1_guid,segment2_guid, body)
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



    def test_delete_info_supply_chain_segment(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            guid = "a7981a48-bd4a-480d-ba63-6584cddad153"
            # body = {
            #     "class": "NewInformationSupplyChainRequestBody",
            #     "properties": {
            #         "displayName": display_name,
            #         "qualifiedName": q_name
            #         }
            #     }
            start_time = time.perf_counter()
            s_client.delete_info_supply_chain_segment(guid)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, "
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

    def test_link_info_supply_chain_segments(self):
        guid1 = "3433ac3e-7233-48d6-bc20-b88e1846ac33"
        guid2 = "2d2bed59-afdf-4eef-bcb1-f1ac8f21f6ce"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
        #     body = {
        #   "class" : "InformationSupplyChainLinkRequestBody",
        #   "properties": {
        #       "class": "InformationSupplyChainLinkProperties",
        #     "label": "expermimental",
        #     "description": "checking to see it works",
        #   }
        # }
            body = {}

            start_time = time.perf_counter()
            response = s_client.link_info_supply_chain_segments(guid1,guid2,body)
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


    def test_create_solution_blueprint(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            display_name = "my_first_blueprint"
            q_name = s_client.__create_qualified_name__("Blueprint",display_name)
            body = {
                "class": "NewSolutionBlueprintRequestBody",
                "properties": {
                    "class": "SolutionBlueprintProperties",
                    "displayName": display_name,
                    "qualifiedName": q_name,
                    "description": "some description",
                    }
                }
            start_time = time.perf_counter()
            response = s_client.create_solution_blueprint(body)
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

    def test_update_solution_blueprint(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()

            body = {
              "class" : "UpdateSolutionBlueprintRequestBody",
              "effectiveTime" : "{{$isoTimestamp}}",
              "properties": {
                "typeName" : "string",
                "class:": "SolutionBlueprintProperties",
                "qualifiedName": "SolnBlueprint::dr egerias blueprint",
                # "description": "updated description4",
                # "displayName": "dr egerias blueprint",
                # "version": "2"
              }
            }

            start_time = time.perf_counter()
            guid = '8e42075c-4bbe-47fb-9e96-8bd60c41bf6d'
            s_client.update_solution_blueprint(guid,body, False)
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

    def test_delete_solution_blueprint(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            guid = "8e42075c-4bbe-47fb-9e96-8bd60c41bf6d"
            # body = {
            #     "class": "NewInformationSupplyChainRequestBody",
            #     "properties": {
            #         "displayName": display_name,
            #         "qualifiedName": q_name
            #         }
            #     }
            start_time = time.perf_counter()
            s_client.delete_solution_blueprint(guid)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, "
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

    def test_get_solution_blueprint_by_guid(self):
        guid = "ef1ce8f0-41a0-4be1-ac6b-a6febfea125e"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_solution_blueprint_by_guid(guid, output_format='LIST')
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


    def test_get_solution_blueprints_by_name(self):
        name = "dr egerias blueprint"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_solution_blueprints_by_name(name)
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


    def test_find_solution_blueprints(self):
        search_string = "Blueprint::my_first_blueprint"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.find_solution_blueprints(search_string, output_format='MD')
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

    def test_find_all_blueprints(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.find_all_solution_blueprints(output_format="DICT")
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds Type: {type(response) if response  else ''}, "
                f" Element count is {len(response) if response else ''}"
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

    def test_create_solution_roles(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            body = {
                "class": "NewActorRoleRequestBody",
                "properties": {
                    "class" : "ActorRoleProperties",
                    "typeName": "GovernanceRole",
                    "domainIdentifier": 0,
                    "qualifiedName": "role::trial-manager",
                    "displayName": "Trial Manager",
                    "description": "bureaucrat",
                    "roleId": "trial-manager",
                    "scope": "coco",
                    "title": "Demigod"
                    }
                }
            s_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = s_client.create_solution_role(body)
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

    def test_update_solution_role(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()

            body = {
              "class" : "UpdateActorRoleRequestBody",
              "properties": {
                "class:": "ActorRoleProperties",
                "description": "updated description - moo",

              }
            }
            start_time = time.perf_counter()
            guid = "4454aeb9-cfaf-4ea0-afa5-b3af3945f341"
            s_client.update_solution_blueprint(guid,body, False)
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

    def test_delete_solution_role(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            guid = "1f71e403-1187-4f03-a1dd-ae7dc105f06f"
            # body = {
            #     "class": "NewInformationSupplyChainRequestBody",
            #     "properties": {
            #         "displayName": display_name,
            #         "qualifiedName": q_name
            #         }
            #     }
            start_time = time.perf_counter()
            response = s_client.delete_solution_role(guid)
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

    def test_get_solution_role_by_guid(self):
        guid = "09e21ac1-39d0-4df2-969c-e41fb29a067d"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_solution_role_by_guid(guid, output_format='JSON')
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


    def test_get_solution_role_by_name(self):
        name = "Clinical Trial Sponsor"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_solution_roles_by_name(name)
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


    def test_find_solution_roles(self):
        search_string = "ClinicalTrialParticipatingHospital"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.find_solution_roles(search_string, output_format='JSON')
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

    def test_find_all_solution_roles(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.find_all_solution_roles(output_format='DICT')
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


    def test_create_solution_component(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )

            s_client.create_egeria_bearer_token()

            body = {
              "class": "NewSolutionComponentRequestBody",
              "parentAtEnd1": True,
              "properties": {
                "class": "SolutionComponentProperties",
                "qualifiedName": "SolnComponent::Lab Process::1",
                "displayName": "Lab Processes",
                "description": "a description",
                "solutionComponentType": "dan-test",
                "plannedDeployedImplementationType": "something"
              }
            }


            start_time = time.perf_counter()
            response = s_client.create_solution_component(body)
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

    def test_update_solution_component(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()

            body = {
              "class" : "UpdateSolutionComponentRequestBody",
              "properties": {
                "class": "SolutionComponentProperties",
                "description": "Maui's favorite meow store",
                "solutionComponentType": "store",
                "plannedDeployedImplementationType": "movie"
                  }
            }
            start_time = time.perf_counter()
            guid = "0f8fea0d-d6e7-46e4-a32f-486899868bc0"
            s_client.update_solution_component(guid,body, False)
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

    def test_delete_solution_component(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            guid = "2414a0af-0597-48d6-9a40-3967e5b99fdc"

            start_time = time.perf_counter()
            s_client.delete_solution_component(guid)
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

    def test_get_solution_component_by_guid(self):
        guid = "7f5dca65-50b4-4103-9ac7-3a406a09047a"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_solution_component_by_guid(guid, output_format='JSON')
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

    def test_get_solution_components_by_name(self):
        name = "SolutionComponent::Hospital Processes::2"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_solution_components_by_name(name, output_format='DICT')
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

    def test_find_solution_components(self):
        filter = "Hospital Processes"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.find_solution_components(filter, output_format='JSON')
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

    def test_find_all_solution_components(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.find_all_solution_components(output_format = "DICT")
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

    def test_link_subcomponent(self):
        guid1 = "40952607-f0fa-4daa-bde3-f9a89150d156"
        guid2 = "186ab31e-9660-4491-8131-940beee08863"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            body = {
                  # "class": "SolutionComponentLinkRequestBody",
                  # "externalSourceGUID": "add guid here",
                  # "externalSourceName": "add qualified name here",
                  # "effectiveTime": {{isotime}},
                  # "forLineage": false,
                  # "forDuplicateProcessing": false,
                  # "properties": {
                  #   "typeName": "string",
                  #   "description": "add description here",
                  #   "effectiveFrom": {{isotime}},
                  #   "effectiveTo": {{isotime}}
                  # }
                }


            start_time = time.perf_counter()
            s_client.link_subcomponent(guid1,guid2,body)
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
