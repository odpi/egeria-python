"""
create_egeria_bearer_token must raise when Egeria does not issue a token. A bad user id or
password gets a 401 whose body is error text; that text used to be returned, and installed in
the Authorization headers, as if it were the token.
"""
import httpx
import pytest

import pyegeria.core._base_platform_client as platform_module
from pyegeria.core._base_platform_client import BasePlatformClient
from pyegeria.core._base_server_client import BaseServerClient
from pyegeria.core._exceptions import (
    PyegeriaClientException, PyegeriaConnectionException, PyegeriaInvalidParameterException,
    PyegeriaUnauthorizedException,
)

PLATFORM = "https://localhost:9443"


def _use_transport(monkeypatch, handler):
    # The constructors check the connection; that is not under test here.
    monkeypatch.setattr(BaseServerClient, "check_connection", lambda self: "test")
    monkeypatch.setattr(BasePlatformClient, "check_connection", lambda self: "test")
    real_client = httpx.AsyncClient

    def client(*args, **kwargs):
        kwargs.pop("verify", None)
        return real_client(transport=httpx.MockTransport(handler))

    monkeypatch.setattr(platform_module, "AsyncClient", client)


def _clients():
    return [
        BaseServerClient("qs-view-server", PLATFORM, user_id="erinoverview", user_pwd="wrong"),
        BasePlatformClient("qs-view-server", PLATFORM, user_id="erinoverview", user_pwd="wrong"),
    ]


@pytest.mark.parametrize("status, body, expected", [
    (401, "Unauthorized: invalid user id or password", PyegeriaUnauthorizedException),
    (403, "Forbidden", PyegeriaUnauthorizedException),
    (500, "Internal Server Error", PyegeriaClientException),
    (200, "", PyegeriaInvalidParameterException),
    (200, '{"class": "VoidResponse", "relatedHTTPCode": 401}', PyegeriaInvalidParameterException),
])
def test_no_token_raises(monkeypatch, status, body, expected):
    _use_transport(monkeypatch, lambda request: httpx.Response(status, text=body))
    for client in _clients():
        before = dict(client.headers)
        with pytest.raises(expected):
            client.create_egeria_bearer_token()
        assert client.headers == before


def test_connection_error_raises(monkeypatch):
    def handler(request):
        raise httpx.ConnectError("connection refused", request=request)

    _use_transport(monkeypatch, handler)
    for client in _clients():
        with pytest.raises(PyegeriaConnectionException):
            client.create_egeria_bearer_token()


def test_token_returned_and_installed(monkeypatch):
    _use_transport(monkeypatch, lambda request: httpx.Response(200, text="eyJhbGciOiJIUzI1NiJ9.abc.def\n"))
    for client in _clients():
        assert client.create_egeria_bearer_token() == "eyJhbGciOiJIUzI1NiJ9.abc.def"
        assert client.headers["Authorization"] == "Bearer eyJhbGciOiJIUzI1NiJ9.abc.def"
