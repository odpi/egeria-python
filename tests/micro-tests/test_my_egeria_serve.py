"""
serve_my_profile / serve_my_egeria: the page's asset and WebSocket URLs follow the
address each browser used, so one container works whatever hostname it is reached by.

textual-serve builds every URL in the page from one fixed public_url. When the portal
was reached as https://localhost:8843 while the container was configured for
https://laz.local:8843/my-egeria, the page pointed the browser at another origin, its
CSP blocked the script, and the page showed only its title.
"""
import pytest
from aiohttp.test_utils import TestClient, TestServer

from my_egeria.serve import _server_class, public_url_for_request

CONFIGURED = "https://laz.local:8843/my-egeria"


@pytest.mark.parametrize("headers, expected", [
    ({"X-Forwarded-Host": "localhost:8843"}, "https://localhost:8843/my-egeria"),
    ({"X-Forwarded-Host": "laz.local:8843"}, "https://laz.local:8843/my-egeria"),
    ({"X-Forwarded-Host": "demo.example.org", "X-Forwarded-Proto": "https"}, "https://demo.example.org/my-egeria"),
    ({"X-Forwarded-Host": "a.example, b.internal", "X-Forwarded-Proto": "http, https"}, "http://a.example/my-egeria"),
    # egeria-workspaces' Apache really sends this (junk first, real host appended by mod_proxy)
    ({"X-Forwarded-Host": "i=99, localhost:8843", "X-Forwarded-Proto": "https"}, "https://localhost:8843/my-egeria"),
    ({"X-Forwarded-Host": "i=99"}, "https://127.0.0.1:8820/my-egeria"),  # no valid entry: fall back to Host
    ({"X-Forwarded-For": "10.0.0.1"}, "https://127.0.0.1:8820/my-egeria"),  # proxied without X-Forwarded-Host
    ({"X-Forwarded-Host": "[::1]:8843"}, "https://[::1]:8843/my-egeria"),
    ({}, "http://127.0.0.1:8820"),  # direct connection: the request's own address, no prefix
])
def test_public_url_for_request(headers, expected):
    assert public_url_for_request("http", "127.0.0.1:8820", headers, CONFIGURED) == expected


def test_no_configured_url_behind_proxy_uses_request_scheme():
    assert public_url_for_request("http", "x:1", {"X-Forwarded-Host": "h:2"}, None) == "http://h:2"


@pytest.mark.asyncio
@pytest.mark.parametrize("headers, base", [
    ({"X-Forwarded-Host": "localhost:8843"}, "localhost:8843/my-egeria"),
    ({"X-Forwarded-Host": "laz.local:8843"}, "laz.local:8843/my-egeria"),
    ({"X-Forwarded-Host": "i=99, localhost:8843", "X-Forwarded-Proto": "https"}, "localhost:8843/my-egeria"),
])
async def test_served_page_uses_the_browsers_host(headers, base):
    server = _server_class()("true", host="127.0.0.1", port=0, title="My Profile", public_url=CONFIGURED)
    async with TestClient(TestServer(await server._make_app())) as client:
        page = await (await client.get("/", headers=headers)).text()
    assert f'src="https://{base}/static/js/textual.js"' in page
    assert f'data-session-websocket-url="wss://{base}/ws"' in page
    assert server.public_url == CONFIGURED  # restored after the request


@pytest.mark.asyncio
async def test_direct_connection_uses_its_own_address():
    server = _server_class()("true", host="127.0.0.1", port=0, title="My Profile", public_url=CONFIGURED)
    async with TestClient(TestServer(await server._make_app())) as client:
        response = await client.get("/")
        page = await response.text()
        host = f"{client.host}:{client.port}"
    assert f'src="http://{host}/static/js/textual.js"' in page
    assert f'data-session-websocket-url="ws://{host}/ws"' in page
