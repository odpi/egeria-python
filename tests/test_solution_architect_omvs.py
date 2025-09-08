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

from pyegeria import SolutionArchitect, PyegeriaException
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria._exceptions_new import PyegeriaException, print_basic_exception

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
            display_name = "puddys_supply_chain"
            q_name = s_client.__create_qualified_name__("InformationSupplyChain",display_name)
            # body = {
            #     "class": "NewElementRequestBody",
            #     "isOwnAnchor": True,
            #     "properties": {
            #         "class": "InformationSupplyChainProperties",
            #         "displayName": display_name,
            #         "qualifiedName": q_name
            #         }
            #     }
            body ={
                'class': 'NewElementRequestBody',
                'anchorGUID': None,
                'anchorScopeGUID': None,
                'effectiveTime': None,
                'externalSourceGUID': None,
                'externalSourceName': None,
                'forDuplicateProcessing': False,
                'forLineage': False,
                'isOwnAnchor': True,
                'parentAtEnd1': True,
                'parentGUID': None,
                'parentRelationshipTypeName': None,
                'properties': {
                    'class': 'InformationSupplyChainProperties',
                    'additionalProperties': None,
                    'description': 'My own personal supply chain',
                    'displayName': display_name,
                    'effectiveFrom': None,
                    'effectiveTo': None,
                    'extendedProperties': None,
                    'purposes': ['hegemony', 'betterment of mankind', 'pranks'],
                    'qualifiedName': q_name,
                    'scope': 'universal',
                    'version': None
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
              "class" : "UpdateElementRequestBody",
              "properties": {
                  "class": "InformationSupplyChainProperties",
                  "description": "updated description",
                  "scope": "updated scope"
              }
            }
            start_time = time.perf_counter()
            guid = "261171b5-9742-41d8-af6d-d68e98f05141"
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
            guid = "261171b5-9742-41d8-af6d-d68e98f05141"
            # body = {
            #     "class": "NewInformationSupplyChainRequestBody",
            #     "properties": {
            #         "displayName": display_name,
            #         "qualifiedName": q_name
            #         }
            #     }
            start_time = time.perf_counter()
            s_client.delete_info_supply_chain(guid)
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
            # if e.exception_error_message_id == 'OMAG-REPOSITORY-HANDLER-404-007':
            #     print("The GUID does not exist")
            #     assert True
            #     return
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
        guid = "9fff0cfc-874b-4b01-b80f-75770c66b876"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_info_supply_chain_by_guid(guid, output_format='DICT')
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


    def test_create_complex_chain(self):
        top_chain1 = 'top1'
        top_chain2 = 'top2'
        sub_chain1 = 'sub1'
        sub_chain2 = 'sub2'

        # create chain1 composed of the two sub chains
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            q_name = s_client.__create_qualified_name__("InformationSupplyChain", top_chain1)
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "InformationSupplyChainProperties",
                    "displayName": top_chain1,
                    "qualifiedName": q_name
                    }
                }
            guid1 = s_client.create_info_supply_chain(body)

            q_name = s_client.__create_qualified_name__("InformationSupplyChain", top_chain2)
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "InformationSupplyChainProperties",
                    "displayName": top_chain2,
                    "qualifiedName": q_name
                    }
                }
            guid2 = s_client.create_info_supply_chain(body)

            print(f"Top1: {guid1}, Top2: {guid2}")


        ## put in links

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
        name = "InformationSupplyChain::Personalized Treatment Ordering"
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
        filter = "Co"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            body = {
                "class": "SearchStringRequestBody",
                # "effective_time": None,
                # "limitResultsByStatus": ["ACTIVE"],
                "sequencingOrder": None,
                "sequencingProperty": None,
                "searchString": filter
                }
            start_time = time.perf_counter()
            response = s_client.find_information_supply_chains(filter,
                                                               body=body, output_format="REPORT")
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
            PyegeriaException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            s_client.close_session()

    def test_link_peer_supply_chains(self):
        name = "sell to the highest bidder2"
        guid = "fdbedd27-2332-4fe5-b50c-9007238fd527"
        guid2 = "70e1ae07-fc8d-49c1-89de-582f671d2b65"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            q_name = s_client.__create_qualified_name__("InformationSupplyChainSegment",name)
            body = {
                "class": "RelationshipRequestBody",
                "properties": {
                    "class": "InformationSupplyChainLinkProperties",
                    "label": "a first label",
                    "description": "label description"
                    }
                }


            start_time = time.perf_counter()
            s_client.link_peer_info_supply_chain(guid, guid2, body)
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


    def test_unlink_peer_supply_chains(self):
        segment1_guid = "fdbedd27-2332-4fe5-b50c-9007238fd527"
        segment2_guid = "fdbedd27-2332-4fe5-b50c-9007238fd527"
        body = {
             "class" : "MetadataSourceRequestBody",
              # "externalSourceGUID": "add guid here",
              # "externalSourceName": "add qualified name here",
              # "effectiveTime" : "{{$isoTimestamp}}",
              # "forLineage" : false,
              # "forDuplicateProcessing" : false,

            }
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()


            s_client.unlink_peer_info_supply_chains(segment1_guid,segment2_guid)
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

    def test_compose_info_supply_chain(self):
        guid1 = "8d7c39bc-f2c5-48df-8f34-c76dbe22b376"
        guid2 = "65ef0367-e69b-40e1-b6e8-4a00c12c06fc"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            body = {
          "class" : "RelationshipRequestBody",
          "properties": {
              "class": "InformationSupplyChainLinkProperties",
            "label": "sub1",
            # "description": "checking to see it works",
          }
        }

            start_time = time.perf_counter()
            s_client.compose_info_supply_chains(guid1,guid2)
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

    def test_decompose_info_supply_chain(self):
        guid1 = "8d7c39bc-f2c5-48df-8f34-c76dbe22b376"
        guid2 = "65ef0367-e69b-40e1-b6e8-4a00c12c06fc"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            body = {
          "class" : "MetadataSourceRequestBody",
            }


            start_time = time.perf_counter()
            s_client.decompose_info_supply_chains(guid1,guid2)
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


    def test_create_solution_blueprint(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            display_name = "my_second_blueprint"
            q_name = s_client.__create_qualified_name__("Blueprint",display_name)
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "SolutionBlueprintProperties",
                    "displayName": display_name,
                    "qualifiedName": q_name,
                    "description": "some description"
                    },
                "initialStatus": "ACTIVE"
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
                PyegeriaException
                ) as e:
            print_basic_exception(e)
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
        guid = "423d0074-6b8a-40f5-8116-8540220bd1c2"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_solution_blueprint_by_guid(guid, output_format='DICT')
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
        search_string = "Co"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.find_solution_blueprints(search_string, output_format='DICT')
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
              "class": "NewElementRequestBody",
              "parentAtEnd1": True,
              "properties": {
                "class": "SolutionComponentProperties",
                "qualifiedName": "SolnComponent::Lab Process::2",
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
            guid = "9e0ed1ce-00da-45ab-8bb2-a9f47d9598a3"

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

    def test_link_solution_component_to_blueprint(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            blueprint = "8a222c5d-b206-454f-b861-2b803cfe3cbd"
            comp = "d026fbd6-709b-45d4-beec-f7a08764b5e2"


            start_time = time.perf_counter()
            guid = "0f8fea0d-d6e7-46e4-a32f-486899868bc0"
            s_client.link_solution_component_to_blueprint(blueprint,comp,None)
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

    def test_link_solution_components(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )
            s_client.create_egeria_bearer_token()
            comp1 = "d026fbd6-709b-45d4-beec-f7a08764b5e2"
            comp2 = "060dfadd-bab3-43de-b70c-4eee51038226"
            body = {
                "class": "RelationshipRequestBody",
                "properties": {
                    "class": "SolutionLinkingWireProperties",
                    "label": "wire 1",
                    "description": "some wiring"
                    },
                }

            start_time = time.perf_counter()

            s_client.link_solution_linking_wire(comp1,comp2,None)
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
        guid = "d026fbd6-709b-45d4-beec-f7a08764b5e2"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_solution_component_by_guid(guid, output_format='REPORT')
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

    def test_get_solution_component_implementations(self):
        guid = "2a5763d0-c540-4a59-8268-db7c88342269"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
                )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_solution_component_implementations(guid, output_format='DICT')
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
        filter = "*"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.find_solution_components(filter, output_format='DICT')
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
