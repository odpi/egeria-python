"""
Simple test to verify the testing framework works.
"""

import pytest
from tests.fixtures.mock_responses import MockResponseFactory
from tests.utils.assertion_helpers import EgeriaAssertions
from tests.fixtures.test_data import TestDataManager


@pytest.mark.unit
def test_mock_response_factory():
    """Test that mock response factory works correctly."""
    # Test digital products response
    response = MockResponseFactory.create_digital_products_response(count=3)
    EgeriaAssertions.assert_valid_format_set_response(response)
    assert response["kind"] == "json"
    assert len(response["data"]) == 3
    
    # Test empty response
    empty_response = MockResponseFactory.create_empty_response()
    assert empty_response["kind"] == "empty"
    
    # Test error response
    error_response = MockResponseFactory.create_error_response("Test error")
    assert error_response["kind"] == "error"
    assert error_response["error"] == "Test error"


@pytest.mark.unit
def test_assertion_helpers():
    """Test that assertion helpers work correctly."""
    # Test valid format set response
    response = MockResponseFactory.create_digital_products_response()
    EgeriaAssertions.assert_valid_format_set_response(response)
    EgeriaAssertions.assert_response_not_empty(response)
    EgeriaAssertions.assert_response_has_guid(response)
    EgeriaAssertions.assert_response_has_display_name(response)
    
    # Test bearer token validation
    token = MockResponseFactory.create_bearer_token_response()
    EgeriaAssertions.assert_valid_bearer_token(token)
    
    # Test connection response validation
    connection_response = MockResponseFactory.create_connection_check_response()
    EgeriaAssertions.assert_valid_connection_response(connection_response)


@pytest.mark.unit
def test_test_data_manager():
    """Test that test data manager works correctly."""
    # Test format sets
    format_sets = TestDataManager.get_test_format_sets()
    assert isinstance(format_sets, list)
    assert len(format_sets) > 0
    assert "Digital-Products" in format_sets
    
    # Test parameters
    params = TestDataManager.get_test_params()
    assert isinstance(params, dict)
    assert "search_string" in params
    assert "page_size" in params
    
    # Test credentials
    credentials = TestDataManager.get_test_credentials()
    assert isinstance(credentials, dict)
    assert "user_id" in credentials
    assert "user_pwd" in credentials
    
    # Test output formats
    output_formats = TestDataManager.get_test_output_formats()
    assert isinstance(output_formats, list)
    assert "DICT" in output_formats
    assert "JSON" in output_formats


@pytest.mark.unit
def test_mock_subclient_factory():
    """Test that mock subclient factory works correctly."""
    from tests.fixtures.mock_responses import MockSubClientFactory
    
    # Test collection manager
    collection_manager = MockSubClientFactory.create_mock_collection_manager()()
    assert collection_manager.view_server == "test-server"
    assert collection_manager.platform_url == "https://test.com"
    
    # Test token operations
    token = collection_manager.create_egeria_bearer_token("user", "pass")
    EgeriaAssertions.assert_valid_bearer_token(token)
    assert collection_manager.get_token() == token
    
    # Test method calls
    result = collection_manager._async_get_digital_products()
    EgeriaAssertions.assert_valid_format_set_response(result)
    assert result["kind"] == "json"


@pytest.mark.unit
def test_test_scenario_builder():
    """Test that test scenario builder works correctly."""
    from tests.fixtures.test_data import TestScenarioBuilder
    
    # Test format set scenarios
    scenarios = TestScenarioBuilder.build_format_set_scenarios()
    assert isinstance(scenarios, list)
    assert len(scenarios) > 0
    
    # Find Digital-Products scenario
    digital_products_scenario = next(
        (s for s in scenarios if s["format_set"] == "Digital-Products"), 
        None
    )
    assert digital_products_scenario is not None
    assert digital_products_scenario["expected_kind"] == "json"
    
    # Test output format scenarios
    output_scenarios = TestScenarioBuilder.build_output_format_scenarios()
    assert isinstance(output_scenarios, list)
    assert len(output_scenarios) > 0
    
    # Test pagination scenarios
    pagination_scenarios = TestScenarioBuilder.build_pagination_scenarios()
    assert isinstance(pagination_scenarios, list)
    assert len(pagination_scenarios) > 0
    
    # Test search scenarios
    search_scenarios = TestScenarioBuilder.build_search_scenarios()
    assert isinstance(search_scenarios, list)
    assert len(search_scenarios) > 0


