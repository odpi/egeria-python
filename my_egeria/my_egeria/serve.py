"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Entry points for running the my_egeria Textual apps in a browser.

Local browser mode (textual-serve): each browser connection gets its own app process.
  serve_my_egeria / serve_my_profile
  MY_EGERIA_HOST        (default: 0.0.0.0)   -- shared by all served apps
  MY_EGERIA_PORT        (default: 8021)      -- main MyEgeria app
  MY_PROFILE_PORT       (default: 8020)      -- my_profile demo app
  MY_EGERIA_PUBLIC_URL / MY_PROFILE_PUBLIC_URL (optional) -- the URL browsers use,
                        when it differs from host:port (e.g. behind a reverse proxy);
                        MY_EGERIA_PUBLIC_URL applies to either app if the app's own isn't set

The apps run with the same Python interpreter as this entry point, so this works
wherever pyegeria is installed (no `textual` CLI from textual-dev needed).
"""
import os
import sys

APPS = {
    # name: (module run with `python -m`, port env var, default port, public URL env var)
    "My Egeria": ("my_egeria.main", "MY_EGERIA_PORT", "8021", "MY_EGERIA_PUBLIC_URL"),
    "My Profile": ("my_egeria.DemoCode.My_Profile.my_profile_app", "MY_PROFILE_PORT", "8020", "MY_PROFILE_PUBLIC_URL"),
}


def _command(module: str) -> str:
    return f'"{sys.executable}" -m {module}'


def _serve(name: str) -> None:
    from textual_serve.server import Server

    module, port_env, default_port, public_url_env = APPS[name]
    Server(
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

