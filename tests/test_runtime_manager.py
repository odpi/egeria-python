"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the Automated Curation View Service module.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""
import json
import time

from rich import print, print_json
from rich.console import Console
from rich.pretty import pprint

from pyegeria import AutomatedCuration, RuntimeManager
from pyegeria._exceptions import (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,
                                  print_exception_response, )

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True
console = Console()


class TestAutomatedCuration:
    good_platform1_url = "https://localhost:9443"


    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    good_user_3 = "peterprofile"
    bad_user_1 = "eviledna"
    bad_user_2 = ""

    good_server_1 = "simple-metadata-store"
    good_server_2 = "laz_kv"
    good_server_3 = "active-metadata-store"
    good_server_4 = "integration-daemon"

    good_engine_host_1 = "governDL01"
    good_view_server_1 = "view-server"
    good_view_server_2 = "fluffy_view"
    bad_server_1 = "coco"
    bad_server_2 = ""

    def test_get_platforms_by_name(self):
        try:
            r_client = RuntimeManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = r_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = r_client.get_platforms_by_name()
            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Platform Report:\n{json.dumps(response, indent=4)}")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_platforms_by_type(self):
        try:
            r_client = RuntimeManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = r_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = r_client.get_platforms_by_type()
            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Platform Report:\n{json.dumps(response, indent=4)}")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_platform_by_guid(self):
        try:
            r_client = RuntimeManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = r_client.create_egeria_bearer_token()
            platform_guid = "44bf319f-1e41-4da1-b771-2753b92b631a"
            start_time = time.perf_counter()
            response = r_client.get_platform_by_guid(platform_guid)

            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print(f"Platform Report:\n{json.dumps(response, indent=4)}")
            elif type(response) is str:
                print(f"String response was {response}")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_platform_report(self):
        try:
            r_client = RuntimeManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = r_client.create_egeria_bearer_token()
            platform_guid = "44bf319f-1e41-4da1-b771-2753b92b631a"
            start_time = time.perf_counter()
            response = r_client.get_platform_report(platform_guid)

            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print(f"Platform Report:\n{json.dumps(response, indent=4)}")
                platform_url = response.get('platformURLRoot'," ")
                print(f"URL is {platform_url}")
            elif type(response) is str:
                print(f"String response was {response}")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_servers_by_name(self):
        try:
            r_client = RuntimeManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = r_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            filter = "Survey Engine Host"
            response = r_client.get_servers_by_name(filter)

            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Platform Report:\n{json.dumps(response, indent=4)}")
            elif type(response) is str:
                print(f"String response was {response}")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_server_by_guid(self):
        try:
            r_client = RuntimeManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = r_client.create_egeria_bearer_token()
            server_guid = "6f45a1cd-4864-425f-9c4d-63ce55d49152"
            start_time = time.perf_counter()
            response = r_client.get_server_by_guid(server_guid)

            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print(f"Server Report:\n{json.dumps(response, indent=4)}")
            elif type(response) is str:
                print(f"String response was {response}")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_server_report(self):
        try:
            r_client = RuntimeManager(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2,
                                         user_pwd="secret")
            token = r_client.create_egeria_bearer_token()
            server_guid = "6f45a1cd-4864-425f-9c4d-63ce55d49152"
            start_time = time.perf_counter()
            response = r_client.get_server_report(server_guid)

            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print(f"Platform Report:\n{json.dumps(response, indent=4)}")
            elif type(response) is str:
                print(f"String response was {response}")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()


