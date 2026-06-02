""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file is a unit test for my_egeria.


"""

import pytest
from ..services.egeria_connection import EgeriaConnectionService


def test_connection_missing_url(monkeypatch):
    monkeypatch.setenv("EGERIA_PLATFORM_URL", "")
    service = EgeriaConnectionService()
    with pytest.raises(ConnectionError):
        service.verify_connection()


def test_connection_success(monkeypatch):
    class MockPlatformServices:
        def get_active_server_list(self):
            return ["server1"]

    monkeypatch.setenv("EGERIA_PLATFORM_URL", "http://localhost:8080")
    monkeypatch.setattr(
        "my_egeria.services.egeria_connection.PlatformServices",
        lambda *a, **k: MockPlatformServices(),
    )

    service = EgeriaConnectionService()
    service.verify_connection()  # Should not raise
