"""
Live tests for connecting to a local Egeria instance.

These tests only run when live mode is enabled via:
  - pytest --live-egeria
  - or env var PYEG_LIVE_EGERIA=1

Connection defaults (overridable via env):
  server_name = "qs-view-server"
  platform_url = "https://localhost:9443"
  user_id = "peterprofile"
  user_pwd = "secret"
"""
from __future__ import annotations

import pytest


@pytest.mark.live
def test_live_connection_check(live_client):
    # BaseServerClient.__init__ already calls check_connection(), but call explicitly too
    origin = live_client.check_connection()
    assert isinstance(origin, str)
    assert origin.strip() != ""
    # Frequently contains the product name; do not hard-require to avoid flakiness
    # assert "Egeria" in origin
