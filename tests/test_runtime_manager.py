"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the Runtime Manager View Service module.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""
import json
import time

from rich import print, print_json
from rich.console import Console
from rich.pretty import pprint

from pyegeria import AutomatedCuration, RuntimeManager, EgeriaTech
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True
console = Console()


class TestRuntimeManager:
    good_platform1_url = "https://localhost:9443"
    good_platform2_url = "https://localhost:9444"

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
    good_view_server_2 = "cocoView1"
    bad_server_1 = "coco"
    bad_server_2 = ""

    # def test_get_config_properties(self):
    #     try:
    #         r_client = RuntimeManager(
    #             self.good_view_server_1,
    #             self.good_platform1_url,
    #             user_id=self.good_user_2,
    #             user_pwd="secret",
    #         )
    #         token = r_client.create_egeria_bearer_token()
    #         server_guid = "dd646e7a-e325-441f-a4cd-2b04d53ffe4e"
    #         connector_name = "UnityCatalogServerSynchronizer"
    #         start_time = time.perf_counter()
    #         response = r_client.get_config_properties(server_guid, connector_name)
    #
    #         duration = time.perf_counter() - start_time
    #         print(f"Type of response: {type(response)}")
    #         print(f"\n\tDuration was {duration} seconds")
    #         if type(response) is dict:
    #             print(f"Config Properties:\n{json.dumps(response, indent=4)}")
    #         elif type(response) is str:
    #             print(f"String response was {response}")
    #         assert True
    #
    #     except (
    #         InvalidParameterException,
    #         PropertyServerException,
    #         UserNotAuthorizedException,
    #     ) as e:
    #         print_exception_response(e)
    #         assert False, "Invalid request"
    #
    #     finally:
    #         r_client.close_session()
    def test_get_guid(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()
            # server_guid = "dd646e7a-e325-441f-a4cd-2b04d53ffe4e"
            server_guid = None
            # name = "PostgreSQL Server:LocalPostgreSQL1"
            # name = "LocalPostgreSQL1"
            name = "OMAG Server Platform:Default Local OMAG Server Platform"
            p_name = "qualifiedName"
            start_time = time.perf_counter()
            response = r_client.__get_guid__(server_guid, name, p_name)

            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print(f"Config Properties:\n{json.dumps(response, indent=4)}")
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

    def test_get_platforms_by_name(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = r_client.get_platforms_by_name()
            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Platform Report:\n{json.dumps(response, indent=4)}")
            else:
                print(f"--> response was {response}")
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

    def test_get_platforms_by_type(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = r_client.get_platforms_by_type()
            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Platform Report:\n{json.dumps(response, indent=4)}")
            else:
                print(f"--> response was {response}")
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

    def test_get_platform_by_guid(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
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

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_platform_report(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()
            # platform_guid = "44bf319f-1e41-4da1-b771-2753b92b631a"
            platform_name = "Default Local OMAG Server \nPlatform"
            platform_guid = None
            start_time = time.perf_counter()
            response = r_client.get_platform_report(
                platform_guid, "Default Local OMAG Server Platform"
            )

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

    def test_get_servers_by_name(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            # filter = "Survey Engine Host"
            filter = "active-metadata-store"
            response = r_client.get_servers_by_name(filter)

            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Servers:\n{json.dumps(response, indent=4)}")
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

    def test_get_integ_connector_config_properties(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            connector_name = "UnityCatalogServerSynchronizer"
            server_guid = None
            server_name = "integration-daemon"
            response = r_client.get_integ_connector_config_properties(
                connector_name, server_guid, server_name
            )

            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print(f"Servers:\n{json.dumps(response, indent=4)}")
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

    def test_get_server_by_guid(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()
            server_guid = "7c6e733e-c35c-471b-83f7-c853c593a4c3"
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

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_server_report(self):
        try:
            r_client = EgeriaTech(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()
            name = "integration-daemon"
            start_time = time.perf_counter()
            server_guid = None
            print(f"\n\tServer GUID is {server_guid}")
            response = r_client.get_server_report(server_guid, name)
            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print(f"Server Report:\n{json.dumps(response, indent=4)}")
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

    def test_restart_integ_daemon_connectors(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()
            server_guid = None
            server_name = "integration-daemon"
            start_time = time.perf_counter()
            response = r_client.restart_integration_connectors(
                "integration-daemon", server_guid, server_name
            )

            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print(f"Platform Report:\n{json.dumps(response, indent=4)}")
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

    def test_shutdown_server(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()
            server_guid = "3601a8cd-2325-4992-915e-d454716b155c"  # integ_daemon
            archive_file = "content-packs/CocoComboArchive.omarchive"
            start_time = time.perf_counter()
            response = r_client.shutdown_server(server_guid)

            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print(f"Platform Report:\n{json.dumps(response, indent=4)}")
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

    def test_activate_server_with_stored_config(self):
        try:
            r_client = EgeriaTech(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()
            # server_guid = "df7d0bf1-e763-447e-89d0-167b9f567d9e"  # integ_daemon
            server_guid = None
            server_name = "active-metadata-store"
            start_time = time.perf_counter()
            response = r_client.activate_server_with_stored_config(
                server_guid, server_name
            )

            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print(f"Platform Report:\n{json.dumps(response, indent=4)}")
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

    def test_add_archive_file(self):
        try:
            r_client = EgeriaTech(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()
            # server_guid = "df7d0bf1-e763-447e-89d0-167b9f567d9e"
            server_guid = r_client.get_guid_for_name("active-metadata-store")
            archive_file = "content-packs/CocoComboArchive.omarchive"
            server_name = "active-metadata-store"
            # archive_file = "content-packs/CoreContentPack.omarchive"

            start_time = time.perf_counter()
            r_client.add_archive_file(archive_file, None, server_name)

            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")

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
