"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Entry points for running my_egeria Textual apps via `textual serve` (browser mode).
Host and port are controlled by environment variables:
  MY_EGERIA_HOST   (default: 0.0.0.0)   -- shared by all served apps
  MY_PROFILE_PORT  (default: 8020)      -- my_profile demo app
  MY_EGERIA_PORT   (default: 8021)      -- main MyEgeria app
"""
import importlib.util
import os
import subprocess
import sys


def _serve(app_module: str, port_env: str, default_port: str) -> None:
    spec = importlib.util.find_spec(app_module)
    if spec is None or spec.origin is None:
        print(f"Cannot locate module {app_module}", file=sys.stderr)
        sys.exit(1)
    host = os.getenv("MY_EGERIA_HOST", "0.0.0.0")
    port = os.getenv(port_env, default_port)
    subprocess.run(
        ["textual", "serve", "--host", host, "--port", port, spec.origin],
        check=False,
    )


def serve_my_profile() -> None:
    _serve("my_egeria.DemoCode.My_Profile.my_profile_app", "MY_PROFILE_PORT", "8020")


def serve_my_egeria() -> None:
    _serve("my_egeria.my_egeria_app", "MY_EGERIA_PORT", "8021")
