"""
Minimal pytest configuration for framework validation tests.
"""

import pytest
from md_processing.md_processing_utils.md_processing_constants import load_commands

# Ensure command specifications are loaded for all micro-tests
load_commands()


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


