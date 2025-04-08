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
                "isOwnAnchor": True,
                "parentAtEnd1": False,
                "properties": {
                    "qualifiedName": q_name,
                    "displayName": display_name,
                    "description": "my first supply chain",
                    "scope": "just testing"
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
                "description": "updated description",
                "scope": "updated scope"
              }
            }
            start_time = time.perf_counter()
            guid = "1f71e403-1187-4f03-a1dd-ae7dc105f06f"
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

    def test_find_information_supply_chains(self):
        filter_string = "*"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.find_information_supply_chains(filter_string, output_format='REPORT', include_mermaid=True)
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
        guid = "1f71e403-1187-4f03-a1dd-ae7dc105f06f"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.get_info_supply_chain_by_guid(guid)
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
                "effective_time": None,
                "limitResultsByStatus": ["ACTIVE"],
                "asOfTime": "2021-12-19T07:20:40.038+00:00",
                "sequencingOrder": None,
                "sequencingProperty": None,
                "filter": filter,
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
            response = s_client.find_all_information_supply_chains()
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
        search_string = "Clinical"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.find_solution_blueprints(search_string, output_format='FORM', include_mermaid=True)
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
            response = s_client.find_all_solution_blueprints()
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
            response = s_client.find_solution_roles(search_string, output_format='REPORT', include_mermaid=True)
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

    def test_find_all_solution_roles(self):
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.find_all_solution_roles()
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
        filter = "Treatment"
        try:
            s_client = SolutionArchitect(
                self.view_server, self.platform_url, self.user, self.password
            )

            s_client.create_egeria_bearer_token()
            start_time = time.perf_counter()
            response = s_client.find_solution_components(filter)
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
            response = s_client.find_all_solution_components()
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
