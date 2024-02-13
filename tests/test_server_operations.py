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

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    print_exception_response,
    print_rest_response,
)

from pyegeria.server_operations import ServerOps

class TestServerOperations():
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
                    "https://127.0.0.1:30081",
                    "garygeeke",
                    404,
                    pytest.raises(InvalidParameterException),
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
            p_client = ServerOps(server, url, user_id)
            response = p_client.get_active_configuration(server)
            print_rest_response(response)
            assert response.get("relatedHTTPCode") == status_code, "Invalid URL"

        if excinfo:
            print_exception_response(excinfo.value)
            assert excinfo.typename == "InvalidParameterException"

    def test_add_archive_files(self):
        # Todo - the base function doesn't seem to validate the file or to actually load? Check
        try:
            server = self.good_server_1
            p_client = ServerOps(server, self.good_platform2_url, self.good_user_1)
            response = p_client.add_archive_file(
                "/Users/dwolfson/localGit/pdr/pyegeria/CocoGovernanceEngineDefinitionsArchive.json",
                server)
            print_rest_response(response)
            assert response.get("relatedHTTPCode") == 200, "Invalid URL or server"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "404", "Invalid parameters"
    @pytest.mark.skip(reason="Need to find a good archive connection body")
    def test_add_archive(self):
        # Todo - the base function doesn't seem to validate the file or to actually load? Check
        try:
            server = self.good_server_1
            p_client = ServerOps(server, self.good_platform2_url, self.good_user_1)
            response = p_client.add_archive("./cocoGovernanceEngineDefinition.json", server)
            print_rest_response(response)
            assert response.get("relatedHTTPCode") == 200, "Invalid URL or server"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "404", "Invalid parameters"

    def test_get_active_server_status(self):
        try:
            server = self.good_server_2
            p_client = ServerOps(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_active_server_status(server)
            print_rest_response(response)
            assert response.get("relatedHTTPCode") == 200, "Invalid URL or server"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "404", "Invalid parameters"

    @pytest.mark.skip(reason="Needs to be implemented")
    def test_get_active_service_list_for_server(self):
        try:
            server = self.good_server_2
            p_client = ServerOps(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_active_service_list_for_server(server)
            print(f"\n\n\tActive Service list for server {server} is {response}")
            assert len(response) >= 0, "Exception?"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_get_server_status(self):
        try:
            server = self.good_server_2
            p_client = ServerOps(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_server_status(server)
            print_rest_response(response)
            assert response.get("relatedHTTPCode") == 200, "Invalid URL"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

