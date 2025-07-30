"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.

"""

import json
from contextlib import nullcontext as does_not_raise

import pytest
from loguru import logger

from pyegeria._client_new import Client2
from pyegeria._exceptions_new import (
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
            client = Client2(server, url, user_id)
            response = client.get_platform_origin()
            if response:
                assert response, "Successfully called get_platform_origin()"
            else:
                assert response, "Failed to call get_platform_origin()"
        # if excinfo:
        #     logger.error(excinfo.value)


    def test_make_get_request(self, url, user_id, status_code, expectation):
        server = "None"
        user_pwd = "nonesuch"
        response = ""
        with expectation as excinfo:
            t_client = Client2(server, url, user_id, user_pwd)
            endpoint = (
                    url
                    + "/open-metadata/admin-services/users/"
                    + user_id
                    + "/stores/connection"
            )
            if t_client is not None:
                response = t_client.make_request("GET", endpoint, None)
                assert response is not None, "There was only an exception response"
        if excinfo:
            logger.error(excinfo.value)
        else:
            if (response is not None) & (response.status_code is None):
                assert excinfo.value.http_error_code == str(status_code), "Invalid URL"

            else:
                assert response.status_code == status_code, "Invalid URL"

    def test_refresh_egeria_bearer_token(self):
        c = Client2(
            "active-metadata-store", "https://localhost:9443", "erinoverview", "secret"
            )
        token = c.create_egeria_bearer_token()
        token2 = c.refresh_egeria_bearer_token()
        if type(token2) == str:
            print(f"The token returned is \n{token}")
        elif type(token2) is dict:
            print(f"The returned token is dict:\n{json.dumps(token2, indent=2)}")

    def test_get_guid(self):
        """This doesn't work since the method needs to be called from an omvs based class"""
        c = Client2(
            "active-metadata-store", "https://localhost:9443", "erinoverview", "secret"
            )
        display_name = "Coco Pharmaceuticals Governance Domains"
        qname = None
        guid = None
        property_name = "displayName"
        response = c.__get_guid__(guid, display_name, property_name, qname)
        if type(response) == str:
            print(f"The response returned is \n{response}")


if __name__ == "__main__":
    print("something")
