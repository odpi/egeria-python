"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.

"""
from contextlib import nullcontext as does_not_raise

import pytest

from pyegeria import Client
from pyegeria._exceptions import (
    InvalidParameterException,
    print_exception_response, UserNotAuthorizedException,
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
                pytest.raises(InvalidParameterException),
            ),
            (
                "https://localhost:9443",
                "garygeeke",
                200,
                does_not_raise(),
            ),
            # (
            #     "https://127.0.0.1:30081",
            #     "garygeeke",
            #     400,
            #     pytest.raises(InvalidParameterException),
            # ),
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
                pytest.raises(UserNotAuthorizedException)
            ),
            (
                "https://cray.local:9443/open-metadata/admin-services/users/woof/servers/active-metadata-store",
                "garygeeke",
                401,
                pytest.raises(UserNotAuthorizedException),
            ),
            ("", "", 400, pytest.raises(InvalidParameterException)),
        ],
    )
    def test_make_get_request(self, url, user_id, status_code, expectation):
        server = "None"
        user_pwd = "nonesuch"
        response = ""
        with expectation as excinfo:
            t_client = Client(
                server, url, user_id, user_pwd, False, async_mode=True
            )
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
            print_exception_response(excinfo.value)
        else:
            if (response is not None) & (response.status_code is None):
                assert excinfo.value.http_error_code == str(status_code), "Invalid URL"

            else:
                assert response.status_code == status_code, "Invalid URL"


if __name__ == "__main__":
    print("something")
