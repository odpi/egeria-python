"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


This file contains a set of test routines to test the platform_services of the Egeria python client.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests. A set of platform, server and user variables are
created local to the TestPlatform class to hold the set of values to be used for testing. The default values have
been configured based on running the Egeria Lab Helm chart on a local kubernetes cluster and setting the portmap.
However, the tests are not dependent on this configuration. It should, however, be noted that the tests are currently
order sensitive - in other words if you delete all the servers the subsequent tests that expect the servers to be
available may fail..

"""

import pytest
import requests

from contextlib import nullcontext as does_not_raise
disable_ssl_warnings = True

from pyegeria.util_exp import (
    InvalidParameterException,
    PropertyServerException,
    print_exception_response,
    print_rest_response,
)

from pyegeria.platform_services import Platform

class TestPlatform:
    good_platform1_url = "https://127.0.0.1:9443"
    good_platform2_url = "https://127.0.0.1:9444"
    bad_platform1_url = "https://localhost:9443"

    # good_platform1_url = "https://127.0.0.1:30080"
    # good_platform2_url = "https://127.0.0.1:30081"
    # bad_platform1_url = "https://localhost:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    bad_user_1 = "eviledna"
    bad_user_2 = ""

    good_server_1 = "cocoMDS1"
    good_server_2 = "cocoMDS2"
    good_server_3 = "meow"
    bad_server_1 = "coco"
    bad_server_2 = ""

    @pytest.mark.skip(reason="waiting for Egeria bug fix")
    @pytest.mark.parametrize(
        "server, url, user_id, status_code, expectation",
        [
            (
                    "meow",
                    "https://google.com",
                    "garygeeke",
                    404,
                    pytest.raises(InvalidParameterException),
            ),
            (
                    "cocoMDS2",
                    "https://localhost:9443",
                    "garygeeke",
                    503,
                    pytest.raises(InvalidParameterException),
            ),
            (
                    "cocoMDS1",
                    "https://127.0.0.1:9443",
                    "garygeeke",
                    200,
                    does_not_raise(),
            ),
            (
                    "cocoMDS9",
                    "https://127.0.0.1:9443",
                    "garygeeke",
                    404,
                    pytest.raises(InvalidParameterException),
            ),
            (
                    "cocoMDS2",
                    "https://127.0.0.1:9443",
                    "",
                    404,
                    pytest.raises(InvalidParameterException),
            ),
            (
                    "cocoMDS2",
                    "https://127.0.0.1:9443/open-metadata/admin-services/users/garygeeke/servers/active-metadata-store",
                    "meow",
                    404,
                    pytest.raises(InvalidParameterException),
            ),
            (
                    "cocoMDS2",
                    "https://wolfsonnet.me:9443/open-metadata/admin-services/users/garygeeke/servers/active-metadata-store",
                    "cocoMDS2",
                    503,
                    pytest.raises(InvalidParameterException),
            ),
            ("", "", "", 400, pytest.raises(InvalidParameterException)),
        ],
    )
    def test_shutdown_platform(self, server, url, user_id, status_code, expectation):
        with expectation as excinfo:
            p_client = Platform(
                server, url, user_id
            )
            response = p_client.shutdown_platform()
            if response is not None:
                assert excinfo.value.http_error_code == status_code, "Invalid URL"
                print(excinfo)
            response = p_client.get_platform_origin()
            if response is not None:
                print(response)
                assert excinfo.value.http_error_code == str(200), "Invalid URL"

        if excinfo:
            print_exception_response(excinfo.value)
            assert excinfo.typename == "InvalidParameterException"

    def test_get_platform_origin(self):
        try:
            p_client = Platform(
                "active-metadata-store", self.good_platform1_url, self.good_user_1
            )
            response_text = p_client.get_platform_origin()
            print("\n\n" + response_text)
            assert len(response_text) > 0, "Empty response text"

        except (InvalidParameterException, PropertyServerException) as e:
            print(e)
            assert False, "Invalid URL?"

    def test_get_platform_origin_bad_URL(self):
        try:
            p_client = Platform(
                "active-metadata-store", self.bad_platform1_url, self.good_user_1
            )
            response_text = p_client.get_platform_origin()
            print("\n\n" + response_text)
            assert len(response_text) > 0, "Empty response text"

        except (
            InvalidParameterException,
            PropertyServerException,
        ) as e:
            print(e)
            assert True, "Invalid URL?"

    def test_activate_server_stored_config(self, server: str = 'cocoMDS2'):
        """
        Need to decide if its worth it to broaden out the test cases..for instance
        in this method if there is an exception - such as invalid server name
        then the test case fails because the response is used before set..

        """
        try:
            p_client = Platform(server,self.good_platform1_url, self.good_user_1)
            response = p_client.activate_server_stored_config(server)
            print_rest_response(response)
            assert response.get("relatedHTTPCode") == 200

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code == "200", "Invalid parameters"

    @pytest.mark.skip(reason="sequencing")
    def test_shutdown_server(self, server: str = good_server_2):
        try:
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.shutdown_server(server)
            assert response, "Server not available?"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code == 404, "Invalid parameters"

    def test_list_servers(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.list_servers()
            print(f"\n\n\t response = {response}")
            assert len(response) > 0, "Empty server list"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code == "200", "Invalid parameters"

    # @pytest.mark.skip(reason="waiting for Egeria bug fix")
    def test_shutdown_servers(self):
        try:
            p_client = Platform(
                self.good_server_2, self.good_platform1_url, self.good_user_1
            )
            response = p_client.shutdown_unregister_servers()
            assert response, "Exception?"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code == "200", "Invalid parameters"

    @pytest.mark.parametrize(
        "server, url, user_id, status_code, expectation",
        [
            # (
            #     "meow",
            #     "https://google.com",
            #     "garygeeke",
            #     404,
            #     pytest.raises(InvalidParameterException),
            # ),
            # (
            #     "cocoMDS2",
            #     "https://localhost:9443",
            #     "garygeeke",
            #     503,
            #     pytest.raises(InvalidParameterException),
            # ),
            # (
            #     "cocoMDS1",
            #     "https://127.0.0.1:30081",
            #     "garygeeke",
            #     404,
            #     pytest.raises(InvalidParameterException),
            # ),
            # (
            #     "cocoMDS9",
            #     "https://127.0.0.1:9443",
            #     "garygeeke",
            #     404,
            #     pytest.raises(InvalidParameterException),
            # ),
            (
                "cocoMDS2",
                "https://127.0.0.1:9443",
                "garygeeke",
                200,
                does_not_raise(),
            ),
            (
                "cocoMDS2",
                "https://127.0.0.1:9443/open-metadata/admin-services/users/garygeeke/servers/active-metadata-store",
                "meow",
                404,
                pytest.raises(InvalidParameterException),
            ),
            (
                "cocoMDS2",
                "https://wolfsonnet.me:9443/open-metadata/admin-services/users/garygeeke/servers/active-metadata-store",
                "cocoMDS2",
                503,
                pytest.raises(InvalidParameterException),
            ),
            ("", "", "", 400, pytest.raises(InvalidParameterException)),
        ],
    )
    def test_get_active_configuration(
        self, server, url, user_id, status_code, expectation
    ):
        with expectation as excinfo:
            p_client = Platform(server, url, user_id)
            response = p_client.get_active_configuration(server)
            print_rest_response(response)
            assert response.get("relatedHTTPCode") == status_code, "Invalid URL"

        if excinfo:
            print_exception_response(excinfo.value)
            assert excinfo.typename == "InvalidParameterException"

    @pytest.mark.skip(reason="defer investigation")
    def test_activate_server_supplied_config(self):
        server = self.good_server_1
        config_body = (
            {
                "omagserverConfig": {
                    "class": "OMAGServerConfig",
                    "versionId": "V2.0",
                    "localServerId": "4d310dc6-11ff-4a20-a37c-b21c90c671c2",
                    "localServerName": "cocoMDS2",
                    "localServerType": "Metadata Access Point",
                    "organizationName": "Coco Pharmaceuticals",
                    "localServerURL": "https://localhost:9443",
                    "localServerUserId": "cocoMDS2npa",
                    "localServerPassword": "cocoMDS2passw0rd",
                    "maxPageSize": 600,
                },
            },
        )

        try:
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.activate_server_supplied_config(config_body, server)
            assert response.get("relatedHTTPCode") == 200
        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "404", "Invalid parameters"

    def test_add_archive_files(self):
        # Todo - the base function doesn't seem to validate the file or to actually load? Check
        try:
            server = self.good_server_1
            p_client = Platform(server, self.good_platform2_url, self.good_user_1)
            response = p_client.add_archive_file("/Users/dwolfson/localGit/pdr/pyEgeria/CocoGovernanceEngineDefinitionsArchive.json", server)
            print_rest_response(response)
            assert response.get("relatedHTTPCode") == 200, "Invalid URL or server"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "404", "Invalid parameters"

    def test_get_active_server_status(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_active_server_status(server)
            print_rest_response(response)
            assert response.get("relatedHTTPCode") == 200, "Invalid URL or server"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "404", "Invalid parameters"

    def test_is_server_known(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.is_server_known(server)
            print(f"\n\n\tis_known() reports {response}")
            assert (response is True) or (response is False), "Exception happened?"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code == "200", "Invalid parameters"

    def test_get_active_service_list_for_server(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_active_service_list_for_server(server)
            print(f"\n\n\tActive Service list for server {server} is {response}")
            assert len(response) >= 0, "Exception?"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_get_server_status(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_server_status(server)
            print_rest_response(response)
            assert response.get("relatedHTTPCode") == 200, "Invalid URL"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_get_active_server_list(self):
        try:
            server = self.good_server_1
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_active_server_list()
            print(f"\n\n\tThe active servers are: {response}")
            assert len(response) > 0, "Exception?"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_shutdown_all_servers(self):
        try:
            server = self.good_server_1
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.shutdown_all_servers()
            print_rest_response(response)
            assert response, "Invalid URL"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_check_server_active(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.check_server_active(server)
            print(f"\n\nserver {server} active state is {str(response)}")
            assert response in (True, False), "Bad Response"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_activate_server_if_down_forced_dn(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.shutdown_server(server)
            print(f"\n\n\t The server was forced down with a response of: {response}")
            response = p_client.activate_server_if_down(server)
            print(f"\n\n\t  activation success was {response}")
            assert response, "Server not configured"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_activate_server_if_down_forced_up(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            a_response = p_client.activate_server_stored_config(server)
            response = p_client.activate_server_if_down(server)
            print(f"\n\n\t  activation success was {response}")
            assert response, "Server not configured "

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_activate_servers_on_platform(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            server_list = p_client.list_servers()
            print(f"\n\n\tServers on the platform are: {server_list}")
            assert server_list is not None, "No servers found?"

            response = p_client.activate_servers_on_platform(server_list)
            print(f"\n\n\t activate_servers_on_platform: success = {response}")
            assert response, "Issues encountered "

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_check_server_configured(self):
        try:
            server = self.good_server_1
            p_client = Platform(server, self.good_platform1_url, self.good_user_2)
            configured = p_client.check_server_configured(server)
            print(f"\n\n\t server {server} configured?  {configured}")
            assert configured or not configured, "Server not known?"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"
