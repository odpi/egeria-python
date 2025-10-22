"""
Minimal pytest configuration for framework validation tests.
"""

import pytest
from .conftest_full import mock_egeria_tech_client  # NEW: exposes the missing fixture


@pytest.fixture
def test_credentials():
    """Provide test credentials."""
    return {
        "user_id": "test_user",
        "user_pwd": "test_password", 
        "view_server": "test-view-server",
        "platform_url": "https://test-egeria.com:9443"
    }


@pytest.fixture
def test_params():
    """Provide standard test parameters."""
    return {
        "search_string": "*",
        "page_size": 10,
        "start_from": 0,
        "starts_with": True,
        "ends_with": False,
        "ignore_case": True
    }


