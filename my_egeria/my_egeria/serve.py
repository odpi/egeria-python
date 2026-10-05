"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Entry points for running the my_egeria Textual apps in a browser.

Local browser mode (textual-serve): each browser connection gets its own app process.
  serve_my_egeria / serve_my_profile
  MY_EGERIA_HOST        (default: 0.0.0.0)   -- shared by all served apps
  MY_EGERIA_PORT        (default: 8021)      -- main MyEgeria app
  MY_PROFILE_PORT       (default: 8020)      -- my_profile demo app
  MY_EGERIA_PUBLIC_URL / MY_PROFILE_PUBLIC_URL (optional) -- where the app is published
                        behind a reverse proxy, e.g. https://example.com/my-egeria;
                        MY_EGERIA_PUBLIC_URL applies to either app if the app's own isn't set

The page's asset and WebSocket URLs follow the address each browser actually used, so
the same container works whatever hostname it is reached by (localhost, the machine's
name, a demo site). Behind a proxy (X-Forwarded-Host present) only the *path* and the
default scheme come from the public URL; the host comes from the request.

The apps run with the same Python interpreter as this entry point, so this works
wherever pyegeria is installed (no `textual` CLI from textual-dev needed).
"""
import os
import re
import sys
from urllib.parse import urlsplit

# host[:port] or [ipv6][:port]
_VALID_HOST = re.compile(r"^(\[[0-9A-Fa-f:.]+\]|[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?)(:\d{1,5})?$")

APPS = {
    # name: (module run with `python -m`, port env var, default port, public URL env var)
    "My Egeria": ("my_egeria.main", "MY_EGERIA_PORT", "8021", "MY_EGERIA_PUBLIC_URL"),
    "My Profile": ("my_egeria.DemoCode.My_Profile.my_profile_app", "MY_PROFILE_PORT", "8020", "MY_PROFILE_PUBLIC_URL"),
}


def _command(module: str) -> str:
    return f'"{sys.executable}" -m {module}'


def public_url_for_request(scheme: str, host: str, headers, configured_public_url: str | None) -> str:
    """The base URL a browser should use for this page's assets and WebSocket.

    textual-serve builds every URL in the page from one fixed public_url, so a page
    reached by a different hostname than the configured one points the browser at
    another origin, which the page's CSP blocks: the page then shows only its title.
    Behind a proxy (X-Forwarded-Host), keep the configured path and default scheme
    but use the host the browser used; on a direct connection use the request's own
    scheme and host, with no path prefix.
    """
    forwarded_host = headers.get("X-Forwarded-Host")
    if forwarded_host or headers.get("X-Forwarded-For"):
        # Use the first X-Forwarded-Host entry that is a real host name: proxies append
        # entries, and a misconfigured one can add junk (egeria-workspaces' Apache sends
        # "i=99, localhost:8843" from `RequestHeader set X-Forwarded-Host "%{Host}i"`).
        # Fall back to Host, which is the browser's host under ProxyPreserveHost On.
        candidates = [h.strip() for h in (forwarded_host or "").split(",")]
        public_host = next((h for h in candidates if _VALID_HOST.match(h)), host)
        configured = urlsplit(configured_public_url) if configured_public_url else None
        forwarded_proto = headers.get("X-Forwarded-Proto")
        base_scheme = (forwarded_proto.split(",")[0].strip() if forwarded_proto else None) \
            or (configured.scheme if configured and configured.scheme else None) or scheme
        path = configured.path.rstrip("/") if configured else ""
        return f"{base_scheme}://{public_host}{path}"
    return f"{scheme}://{host}"


def _server_class():
    from textual_serve.server import Server

    class _RequestAwareServer(Server):
        """textual-serve Server whose page URLs follow the address the browser used."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._configured_public_url = kwargs.get("public_url")

        async def handle_index(self, request):
            # Server.handle_index builds every URL from self.public_url synchronously
            # (no await while building), so swapping it per request can't interleave
            # with another request.
            configured = self.public_url
            self.public_url = public_url_for_request(
                request.scheme, request.host, request.headers, self._configured_public_url)
            try:
                return await super().handle_index(request)
            finally:
                self.public_url = configured

    return _RequestAwareServer


def _serve(name: str) -> None:
    module, port_env, default_port, public_url_env = APPS[name]
    _server_class()(
        _command(module),
        host=os.getenv("MY_EGERIA_HOST", "0.0.0.0"),
        port=int(os.getenv(port_env, default_port)),
        title=name,
        # MY_EGERIA_PUBLIC_URL is what egeria-workspaces' my-profile container sets
        # (one app per container), so honour it for either app.
        public_url=os.getenv(public_url_env) or os.getenv("MY_EGERIA_PUBLIC_URL") or None,
    ).serve()


def serve_my_profile() -> None:
    _serve("My Profile")


def serve_my_egeria() -> None:
    _serve("My Egeria")
