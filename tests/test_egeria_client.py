"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the core OMAG config class and methods
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import json
import time

from rich import print, print_json
from rich.console import Console

from pyegeria import (
    Egeria,
    EgeriaCat,
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

disable_ssl_warnings = True

console = Console(width=150)


class TestEgeriaCat:
    good_platform1_url = "https://127.0.0.1:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    good_user_3 = "peterprofile"
    bad_user_1 = "eviledna"
    bad_user_2 = ""
    good_server_1 = "simple-metadata-store"
    good_server_2 = "integration-daemon"
    good_server_3 = "active-metadata-store"
    good_engine_host_1 = "governDL01"
    good_view_server_1 = "view-server"

    def test_get_my_profile(self):
        try:
            m_client = Egeria(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")

            response = m_client.get_my_profile()

            id_list = []
            if type(response) is dict:
                print_json(data=response)
            elif type(response) is str:
                print("\n\n" + response)
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

    def test_find_projects(self):
        try:
            m_client = Egeria(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
            )

            token = m_client.create_egeria_bearer_token(self.good_user_2, "secret")

            response = m_client.find_projects("*")
            print(f"\nType of response is {type(response)}")
            id_list = []
            if type(response) is list:
                print_json(data=response)
            elif type(response) is str:
                print("\n\n" + response)
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

    def test_get_integration_daemon_status(self, server: str = good_server_2):
        try:
            server_name = server
            s_client = Egeria(
                server_name, self.good_platform1_url, self.good_user_1, "secret"
            )
            token = s_client.create_egeria_bearer_token()
            response = s_client.get_integration_daemon_status(server)

            if type(response) is dict:
                # print(f"\n\n\tIntegration Daemon Status for server {server} is {json.dumps(response, indent=4)}")
                print(f"\n\n\tIntegration Daemon Status for server {server} is:")
                print_json(json.dumps(response))
            else:
                print(f"\n\n\tIntegration Daemon Status response was: {response}")
            assert True, "Invalid URL or server"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_get_platform_report(self):
        try:
            r_client = Egeria(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()
            platform_guid = "44bf319f-1e41-4da1-b771-2753b92b631a"
            start_time = time.perf_counter()
            response = r_client.get_platform_report(platform_guid)

            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print(f"Platform Report:\n{json.dumps(response, indent=4)}")
                platform_url = response.get("platformURLRoot", " ")
                print(f"URL is {platform_url}")
            elif type(response) is str:
                print(f"String response was {response}")
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_guid_for_name(self):
        open_metadata_type_name = None
        property_value = "Teddy Bear Drop Foot Clinical Trial"

        c_client = Egeria(
            self.good_view_server_1, self.good_platform1_url, self.good_user_1, "secret"
        )

        bearer_token = c_client.create_egeria_bearer_token()
        result = c_client.get_guid_for_name(property_value)

        if type(result) is list:
            print(f"\n\tElement count is: {len(result)}")
            print_json(data=result)
        elif type(result) is str:
            console.print("\n\n\t Response is " + result)

        assert True
