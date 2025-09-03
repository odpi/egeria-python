"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the Runtime Manager View Service module.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import json
import time
from contextlib import nullcontext as does_not_raise
from json import JSONDecodeError

import pytest
from rich import print, print_json
from rich.console import Console
from rich.traceback import Traceback, install

from pyegeria import AutomatedCuration, EgeriaTech, RuntimeManager
from pyegeria._exceptions_new import (
    PyegeriaInvalidParameterException,
    PyegeriaAPIException,
    PyegeriaUnauthorizedException,
    print_exception_response, print_basic_exception,
    )

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True
install()
console = Console(width=200)


class TestRuntimeManager:
    good_platform1_url = "https://localhost:9443"
    good_platform2_url = "https://localhost:8443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    good_user_3 = "peterprofile"
    bad_user_1 = "eviledna"
    bad_user_2 = ""

    good_server_1 = "simple-metadata-store"
    good_server_2 = "qs-metadata-store"
    good_server_3 = "active-metadata-store"
    good_server_4 = "qs-integration-daemon"

    good_engine_host_1 = "governDL01"
    good_view_server_1 = "view-server"
    good_view_server_2 = "qs-view-server"
    bad_server_1 = "coco"
    bad_server_2 = ""

    @pytest.mark.parametrize(
        "display_name, qualified_name, parameter_name, guid, tech_type, expectation",
        [
            # (
            #     "integration-daemon",
            #     None,
            #     "qualifiedName",
            #     None,
            #     "Integration Daemon",
            #     does_not_raise(),
            # ),
            # (
            #     "integration-daemon",
            #     "integration-daemon",
            #     "qualifiedName",
            #     None,
            #     "Integration Daemon",
            #     does_not_raise(),
            # ),
            (
                None,
                "Integration Daemon:qs-integration-daemon",
                "qualifiedName",
                None,
                "Integration Daemon",
                does_not_raise(),
            ),
            # (
            #     None,
            #     None,
            #     "qualifiedName",
            #     "da9844c2-4e1a-4712-9f41-462fa156df43",
            #     "Integration Daemon",
            #     does_not_raise(),
            # ),
            (
                "qs-metadata-store",
                None,
                "displayName",
                None,
                "Metadata Store",
                does_not_raise(),
            ),
            (
                "qs-view-server",
                None,
                "displayName",
                None,
                "View Server",
                does_not_raise(),
            ),
        ],
    )
    def test_get_guid(
        self, display_name, qualified_name, parameter_name, guid, tech_type, expectation
    ):
        install()
        console = Console()
        with expectation as excinfo:
            r_client = RuntimeManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()
            print(
                f"\ndisplay_name: {display_name} qualified_name: {qualified_name} parameter_name: {parameter_name}"
                f" guid: {guid} tech_type: {tech_type}\n"
            )
            start_time = time.perf_counter()
            response = r_client.__get_guid__(
                guid,
                display_name,
                parameter_name,
                tech_type=tech_type,
                qualified_name=qualified_name,
            )

            duration = time.perf_counter() - start_time

            if type(response) is dict:
                print(f"Config Properties:\n{json.dumps(response, indent=4)}")
            elif type(response) is str:
                print(f"String response was {response} duration was {duration} seconds")
            assert True

        if excinfo:
            console.print(excinfo.value)
            assert False, "Invalid request"

    def test_refresh_gov_eng_config(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()
            display_name = "engine-host"
            start_time = time.perf_counter()
            response = r_client.refresh_gov_eng_config(display_name=display_name)
            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Platform Report:\n{json.dumps(response, indent=4)}")
            else:
                print(f"--> response was {response}")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_platforms_by_name(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_2,
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
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_platforms_by_type(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_2,
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
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_platform_templates_by_type(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            response = r_client.get_platform_templates_by_type()
            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Platform template Report:\n{json.dumps(response, indent=4)}")
            else:
                print(f"--> response was {response}")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_platform_by_guid(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_2,
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
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_platform_report(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_2,
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
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_servers_by_name(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            filter = "qs-view-server"
            # filter = "simple-metadata-store"

            response = r_client.get_servers_by_name(filter)
            if type(response) is list:
                print(f"Servers:\n{json.dumps(response, indent=4)}")
            else:
                print(f"--> response was {response}")

            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Servers:\n{json.dumps(response, indent=4)}")
            elif type(response) is str:
                print(f"String response was {response}")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_server_by_guid(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()
            server_guid = "61b8ba29-4312-43c8-b518-1695749c7c3c"
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
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_server_report(self):
        try:
            r_client = EgeriaTech(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_2,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()
            name = "qs-integration-daemon"

            start_time = time.perf_counter()
            server_guid = None
            print(f"\n\tServer GUID is {server_guid}")
            response = r_client.get_server_report(server_guid, name)
            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is dict:
                print(f"Server Report:\n{json.dumps(response, indent=2)}")
            elif type(response) is str:
                print(f"String response was {response}")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_servers_by_dep_imp_type(self):
        try:
            r_client = EgeriaTech(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            filter = "*"
            response = r_client.get_servers_by_dep_impl_type(filter)
            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Server Report:\n{json.dumps(response, indent=4)}")
            elif type(response) is str:
                print(f"String response was {response}")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_get_server_templates_by_dep_imp_type(self):
        try:
            r_client = EgeriaTech(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()

            start_time = time.perf_counter()
            filter = "*"
            response = r_client.get_server_templates_by_dep_impl_type(filter)
            duration = time.perf_counter() - start_time
            print(f"Type of response: {type(response)}")
            print(f"\n\tDuration was {duration} seconds")
            if type(response) is list:
                print(f"Server Report:\n{json.dumps(response, indent=4)}")
            elif type(response) is str:
                print(f"String response was {response}")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
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
                connector_name, display_name=server_name
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
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_update_integ_connector_config(self):
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
            # connector_name = None
            server_guid = None
            display_name = "integration-daemon"
            qualified_name = None
            merge_update = True
            body = {"refreshTimeInterval": 10}

            response = r_client.update_connector_configuration(
                connector_name,
                server_guid,
                display_name,
                qualified_name,
                merge_update,
                body,
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
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_refresh_integ_integration_connectors(self):
        try:
            r_client = RuntimeManager(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()
            server_guid = None
            server_name = "integration-daemon"
            connector_name = "UnityCatalogServerSynchronizer"
            start_time = time.perf_counter()
            r_client.refresh_integration_connectors(
                connector_name, server_guid, server_name
            )

            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print("Connector {connector_name} restarted")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
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
            # connector_name = "UnityCatalogServerSynchronizer"
            connector_name = None
            start_time = time.perf_counter()
            r_client.restart_integration_connectors(
                connector_name, server_guid, server_name
            )

            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            print("Connector {connector_name} restarted")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
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
            server_guid = "da9844c2-4e1a-4712-9f41-462fa156df43"  # simple

            start_time = time.perf_counter()
            r_client.shutdown_server(server_guid)

            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")
            print(f" Server {server_guid} shut down")
            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
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
            server_guid = "da9844c2-4e1a-4712-9f41-462fa156df43"  # simple
            # server_guid = None
            server_name = None
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
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()

    def test_add_archive_file(self):
        try:
            r_client = EgeriaTech(
                self.good_view_server_2,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            token = r_client.create_egeria_bearer_token()
            # server_guid = "df7d0bf1-e763-447e-89d0-167b9f567d9e"
            server_guid = r_client.get_guid_for_name("qs-metadata-store")
            print("server_guid", server_guid)
            archive_file = "content-packs/CocoComboArchive.omarchive"
            server_name = "qs-metadata-store"
            # archive_file = "content-packs/CoreContentPack.omarchive"

            start_time = time.perf_counter()
            r_client.add_archive_file(archive_file, server_guid, server_name)

            duration = time.perf_counter() - start_time

            print(f"\n\tDuration was {duration} seconds")

            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaAPIException,
            PyegeriaUnauthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            r_client.close_session()
