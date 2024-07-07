"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


This file contains a set of test routines to test the server operations services of the Egeria python client.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests. A set of platform, server and user variables are
created local to the TestPlatform class to hold the set of values to be used for testing.  It should, however, be noted that the tests are currently
order sensitive - in other words if you delete all the servers the subsequent tests that expect the servers to be
available may fail..

"""

import json

import pytest
from rich import print, print_json

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    print_exception_response,
)
from pyegeria.server_operations import ServerOps

disable_ssl_warnings = True


class TestServerOperations:
    good_platform1_url = "https://127.0.0.1:9443"
    good_platform2_url = "https://localhost:9446"
    bad_platform1_url = "https://localhost:9443"

    # good_platform1_url = "https://127.0.0.1:30080"
    # good_platform2_url = "https://127.0.0.1:30081"
    # bad_platform1_url = "https://localhost:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    bad_user_1 = "eviledna"
    bad_user_2 = ""

    good_server_1 = "active-metadata-store"
    good_server_2 = "integration-daemon"
    good_server_3 = "engine-host"
    bad_server_1 = "coco"
    bad_server_2 = ""

    def test_get_active_configuration(self, server: str = good_server_1):
        server_name = server
        try:
            s_client = ServerOps(server_name, self.good_platform1_url, self.good_user_1)
            response = s_client.get_active_configuration(server)
            print(f"\n\n\tThe active configuration of {server} is \n{response}")
            assert True

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "404", "Invalid parameters"

    def test_add_archive_files(self):
        # Todo - the base function doesn't seem to validate the file or to actually load? Check
        try:
            server = self.good_server_1
            p_client = ServerOps(server, self.good_platform1_url, self.good_user_1)
            p_client.add_archive_file(
                "content-packs/CocoComboArchive.omarchive",
                server)
            assert True, "Should have raised an exception"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "404", "Invalid parameters"

    @pytest.mark.skip(reason="Need to find a good archive connection body")
    def test_add_archive(self):
        # Todo - the base function doesn't seem to validate the file or to actually load? Check
        try:
            server = self.good_server_1
            p_client = ServerOps(server, self.good_platform2_url, self.good_user_1)
            p_client.add_archive("./cocoGovernanceEngineDefinition.json", server)

            assert True, "Should have raised an exception"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "404", "Invalid parameters"

    def test_get_active_server_status(self, server: str= good_server_1):
        try:
            p_client = ServerOps(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_active_server_status(server)
            print(response)
            assert response.get("relatedHTTPCode") == 200, "Invalid URL or server"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "404", "Invalid parameters"

    def test_get_active_service_list_for_server(self):
        try:
            server = self.good_server_1
            p_client = ServerOps(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_active_service_list_for_server(server)
            print(f"\n\n\tActive Service list for server {server} is {response}")
            assert True, "Invalid URL or server"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_get_governance_engine_summaries(self, server:str = good_server_3):
        try:
            server_name = server
            s_client = ServerOps(server_name, self.good_platform1_url, self.good_user_1)
            response = s_client.get_governance_engine_summaries(server)
            print(f"\n\n\tGovernance Engine Summary for server {server} is {json.dumps(response, indent=4)}")

            assert True, "Invalid URL or server"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    #
    #   Integration Daemon Ops
    #

    def test_get_integration_daemon_status(self, server:str = good_server_2):
        try:
            server_name = server
            s_client = ServerOps(server_name, self.good_platform1_url, self.good_user_1)
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


    def test_get_connector_config(self, server:str = good_server_2):
        try:
            server_name = server
            connector = "JDBCDatabaseCataloguer"
            s_client = ServerOps(server_name, self.good_platform1_url, self.good_user_1)
            response = s_client.get_connector_config(connector,server)
            print(f"\n\n\tConnector configuration for connector {connector} is \n{json.dumps(response, indent=4)}")

            assert True, "Invalid URL or server"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

# todo - review with Mandy?
    def test_restart_integration_connector(self, server:str = good_server_2):
        try:
            server_name = "integration-daemon"
            # connector = "FilesMonitor"
            # connector = "DataFilesMonitorIntegrationConnector"

            connector = None
            s_client = ServerOps(server_name, self.good_platform1_url, self.good_user_1)
            # response = s_client.restart_integration_connector(connector,server)
            s_client.restart_integration_connector(connector, server_name)

            assert True, "Invalid URL or server"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_refresh_integration_connectors(self, server:str = good_server_2):
        try:
            server_name = "integration-daemon"
            connector = "FilesMonitor"
            s_client = ServerOps(server_name, self.good_platform1_url, self.good_user_1)

            s_client.refresh_integration_connectors(None, server_name)

            assert True, "Invalid URL or server"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"
