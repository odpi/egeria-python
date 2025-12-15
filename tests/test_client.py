"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.

"""

import json
from contextlib import nullcontext as does_not_raise

import pytest
import asyncio
from loguru import logger

from pyegeria import print_basic_exception
from pyegeria._server_client import ServerClient
from pyegeria._exceptions import (
     PyegeriaException, PyegeriaConnectionException,  PyegeriaInvalidParameterException,
     PyegeriaAPIException, PyegeriaUnknownException, PyegeriaClientException, PyegeriaNotFoundException,
    PyegeriaUnauthorizedException,
    )


@pytest.fixture()
def basic_server():
    platform = "https://127.0.0.1:9443"


class TestClient:
    # @pytest.mark.xfail
    @pytest.mark.parametrize(
        "url, user_id, status_code, expectation",
        [
            (
                "https://google.com",
                "garygeeke",
                404,
                pytest.raises(PyegeriaClientException),
            ),
            (
                    "https://localhost:9443",
                    "garygeeke",
                    200,
                    does_not_raise(),
                    ),
            (
                "https://127.0.0.1:30081",
                "garygeeke",
                404,
                pytest.raises(PyegeriaConnectionException),
            ),
            (
                "https://127.0.0.1:9443",
                "garygeeke",
                200,
                does_not_raise(),
            ),
            (
                "https://127.0.0.1:9443/open-metadata/admin-services/users/meow/servers/active-metadata-store",
                "meow",
                401,
                pytest.raises(PyegeriaClientException),
            ),
            (
                "https://cray.local:9443/open-metadata/admin-services/users/woof/servers/active-metadata-store",
                "garygeeke",
                404,
                pytest.raises(PyegeriaConnectionException),
            ),
            ("", "", 400, pytest.raises(PyegeriaInvalidParameterException)),
            ],
        )
    def test_get_origin(self, url, user_id, status_code, expectation):
        server = 'qs-view-server'
        with expectation as excinfo:
            client = ServerClient(server, url, user_id)
            response = client.get_platform_origin()
            if response:
                assert response, "Successfully called get_platform_origin()"
            else:
                assert response, "Failed to call get_platform_origin()"
        # if excinfo:
        #     logger.error(excinfo.value)


    def test_get_platform_origin(self):
        server = 'qs-view-server'
        client = ServerClient(server, 'https://localhost:9443', 'erinoverview', 'secret')
        response = client.get_platform_origin()
        print(f"\n{response}")
        assert response, "Successfully called get_platform_origin()"


    def test_refresh_egeria_bearer_token(self):
        c = ServerClient(
            "qs-metadata-store", "https://localhost:9443", "erinoverview", "secret"
            )
        token = c.create_egeria_bearer_token()
        token2 = c.refresh_egeria_bearer_token()
        if type(token2) == str:
            print(f"The token returned is \n{token}")
        elif type(token2) is dict:
            print(f"The returned token is dict:\n{json.dumps(token2, indent=2)}")

    def test_get_guid(self):
        """This doesn't work since the method needs to be called from an omvs based class"""
        c = ServerClient(
            "qs-view-server", "https://localhost:9443", "erinoverview", "secret"
            )
        try:
            c.create_egeria_bearer_token()
            display_name = "PostgreSQL Server"
            qname = None
            guid = None
            property_name = "displayName"
            response = c.__get_guid__(guid, display_name, property_name, qname)
            if type(response) == str:
                print(f"The response returned is \n{response}")
        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"

    def test_get_guid(self):
        c = ServerClient(
            "qs-view-server", "https://localhost:9443", "erinoverview", "secret"
        )
        try:
            c.create_egeria_bearer_token()
            display_name = "PostgreSQL Server"
            type_name = "ValidMetadataValue"
            property_name = ["displayName"]
            response = c.get_guid_for_name( display_name, property_name, type_name)
            # response = c.get_elements_by_property_value(display_name, property_name, type_name)
            if type(response) == str:
                print(f"The response returned is \n{response}")
            if isinstance(response, list | dict):
                print(json.dumps(response, indent=2))
        except PyegeriaException as e:
            print_basic_exception(e)
            assert False, "Invalid request"


if __name__ == "__main__":
    print("something")
