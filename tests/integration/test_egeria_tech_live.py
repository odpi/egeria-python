"""
Integration tests for EgeriaTech with live Egeria instance.

These tests run against a live Egeria instance and test real API interactions.
They are marked with @pytest.mark.integration and require --live-egeria flag.
"""

import pytest
import asyncio
from typing import Dict, Any

from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.format_set_executor import _async_run_report
from tests.utils.assertion_helpers import EgeriaAssertions
from tests.fixtures.test_data import TestDataManager


@pytest.mark.integration
@pytest.mark.slow
class TestEgeriaTechLive:
    """Integration tests for EgeriaTech with live Egeria instance."""
    
    def test_live_egeria_tech_initialization(self, live_egeria_tech_client):
        """Test EgeriaTech initialization with live Egeria."""
        client = live_egeria_tech_client
        
        assert client.view_server is not None
        assert client.platform_url is not None
        assert client.user_id is not None
        assert client.user_pwd is not None
        assert hasattr(client, "_subclients")
        assert len(client._subclients) > 0
    
    def test_live_bearer_token_creation(self, live_egeria_tech_client):
        """Test bearer token creation with live Egeria."""
        client = live_egeria_tech_client
        
        # Token should already be created during fixture setup
        token = client.get_token()
        EgeriaAssertions.assert_valid_bearer_token(token)
        
        # Test creating a new token
        new_token = client.create_egeria_bearer_token(client.user_id, client.user_pwd)
        EgeriaAssertions.assert_valid_bearer_token(new_token)
        assert client.get_token() == new_token
    
    def test_live_token_operations(self, live_egeria_tech_client):
        """Test token operations with live Egeria."""
        client = live_egeria_tech_client
        
        # Test setting token
        test_token = "test_token_live"
        client.set_bearer_token(test_token)
        assert client.get_token() == test_token
        
        # Test getting token
        retrieved_token = client.get_token()
        assert retrieved_token == test_token
        
        # Restore original token
        original_token = client.create_egeria_bearer_token(client.user_id, client.user_pwd)
        EgeriaAssertions.assert_valid_bearer_token(original_token)
    
    def test_live_session_management(self, live_egeria_tech_client):
        """Test session management with live Egeria."""
        client = live_egeria_tech_client
        
        # Verify session is active
        token = client.get_token()
        assert token is not None
        
        # Close session
        client.close_session()
        
        # Verify session is closed
        assert client.get_token() is None
        
        # Recreate session
        new_token = client.create_egeria_bearer_token(client.user_id, client.user_pwd)
        EgeriaAssertions.assert_valid_bearer_token(new_token)
        assert client.get_token() == new_token


@pytest.mark.integration
@pytest.mark.slow
class TestEgeriaTechLiveFormatSets:
    """Integration tests for format set execution with live Egeria."""
    
    @pytest.mark.asyncio
    async def test_live_digital_products_report(self, live_egeria_tech_client):
        """Test Digital-Products report against live Egeria."""
        client = live_egeria_tech_client
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Digital-Products",
            client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
        assert isinstance(result["data"], list)
        
        # If data is returned, validate structure
        if len(result["data"]) > 0:
            EgeriaAssertions.assert_response_contains_expected_fields(
                result, ["guid", "display_name", "qualified_name"]
            )
    
    @pytest.mark.asyncio
    async def test_live_glossary_terms_report(self, live_egeria_tech_client):
        """Test Glossary-Terms report against live Egeria."""
        client = live_egeria_tech_client
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Glossary-Terms",
            client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
        assert isinstance(result["data"], list)
        
        # If data is returned, validate structure
        if len(result["data"]) > 0:
            EgeriaAssertions.assert_response_contains_expected_fields(
                result, ["guid", "display_name", "qualified_name"]
            )
    
    @pytest.mark.asyncio
    async def test_live_data_assets_report(self, live_egeria_tech_client):
        """Test Data-Assets report against live Egeria."""
        client = live_egeria_tech_client
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Data-Assets",
            client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
        assert isinstance(result["data"], list)
        
        # If data is returned, validate structure
        if len(result["data"]) > 0:
            EgeriaAssertions.assert_response_contains_expected_fields(
                result, ["guid", "display_name", "qualified_name"]
            )
    
    @pytest.mark.asyncio
    async def test_live_collections_report(self, live_egeria_tech_client):
        """Test Collections report against live Egeria."""
        client = live_egeria_tech_client
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Collections",
            client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
        assert isinstance(result["data"], list)
        
        # If data is returned, validate structure
        if len(result["data"]) > 0:
            EgeriaAssertions.assert_response_contains_expected_fields(
                result, ["guid", "display_name", "qualified_name"]
            )
    
    @pytest.mark.asyncio
    async def test_live_empty_response_handling(self, live_egeria_tech_client):
        """Test handling of empty responses from live Egeria."""
        client = live_egeria_tech_client
        
        # Test with a search that should return no results
        params = {"search_string": "nonexistent_search_term_12345"}
        
        result = await _async_run_report(
            "Digital-Products",
            client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        # Should be either empty or have no data
        if result["kind"] == "json":
            assert len(result["data"]) == 0
        elif result["kind"] == "empty":
            assert result["kind"] == "empty"


@pytest.mark.integration
@pytest.mark.slow
class TestEgeriaTechLiveOutputFormats:
    """Integration tests for different output formats with live Egeria."""
    
    @pytest.mark.asyncio
    async def test_live_dict_output_format(self, live_egeria_tech_client):
        """Test DICT output format with live Egeria."""
        client = live_egeria_tech_client
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Digital-Products",
            client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
        EgeriaAssertions.assert_response_data_type(result, list)
    
    @pytest.mark.asyncio
    async def test_live_json_output_format(self, live_egeria_tech_client):
        """Test JSON output format with live Egeria."""
        client = live_egeria_tech_client
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Digital-Products",
            client,
            output_format="JSON",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
        EgeriaAssertions.assert_response_data_type(result, list)
    
    @pytest.mark.asyncio
    async def test_live_report_output_format(self, live_egeria_tech_client):
        """Test REPORT output format with live Egeria."""
        client = live_egeria_tech_client
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Digital-Products",
            client,
            output_format="REPORT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "text"
        EgeriaAssertions.assert_markdown_response(result)
    
    @pytest.mark.asyncio
    async def test_live_mermaid_output_format(self, live_egeria_tech_client):
        """Test MERMAID output format with live Egeria."""
        client = live_egeria_tech_client
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Digital-Products",
            client,
            output_format="MERMAID",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "text"
        EgeriaAssertions.assert_mermaid_response(result)
    
    @pytest.mark.asyncio
    async def test_live_html_output_format(self, live_egeria_tech_client):
        """Test HTML output format with live Egeria."""
        client = live_egeria_tech_client
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Digital-Products",
            client,
            output_format="HTML",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "text"
        EgeriaAssertions.assert_html_response(result)


@pytest.mark.integration
@pytest.mark.slow
class TestEgeriaTechLivePagination:
    """Integration tests for pagination with live Egeria."""
    
    @pytest.mark.asyncio
    async def test_live_pagination_small_page(self, live_egeria_tech_client):
        """Test pagination with small page size."""
        client = live_egeria_tech_client
        params = {"page_size": 5, "start_from": 0}
        
        result = await _async_run_report(
            "Digital-Products",
            client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        if result["kind"] == "json":
            assert len(result["data"]) <= 5
    
    @pytest.mark.asyncio
    async def test_live_pagination_large_page(self, live_egeria_tech_client):
        """Test pagination with large page size."""
        client = live_egeria_tech_client
        params = {"page_size": 50, "start_from": 0}
        
        result = await _async_run_report(
            "Digital-Products",
            client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        if result["kind"] == "json":
            assert len(result["data"]) <= 50
    
    @pytest.mark.asyncio
    async def test_live_pagination_offset(self, live_egeria_tech_client):
        """Test pagination with offset."""
        client = live_egeria_tech_client
        params = {"page_size": 10, "start_from": 10}
        
        result = await _async_run_report(
            "Digital-Products",
            client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        if result["kind"] == "json":
            assert len(result["data"]) <= 10


@pytest.mark.integration
@pytest.mark.slow
class TestEgeriaTechLiveSearch:
    """Integration tests for search functionality with live Egeria."""
    
    @pytest.mark.asyncio
    async def test_live_search_wildcard(self, live_egeria_tech_client):
        """Test search with wildcard."""
        client = live_egeria_tech_client
        params = {"search_string": "*"}
        
        result = await _async_run_report(
            "Digital-Products",
            client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
    
    @pytest.mark.asyncio
    async def test_live_search_specific_term(self, live_egeria_tech_client):
        """Test search with specific term."""
        client = live_egeria_tech_client
        params = {"search_string": "Digital"}
        
        result = await _async_run_report(
            "Digital-Products",
            client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
    
    @pytest.mark.asyncio
    async def test_live_search_case_sensitivity(self, live_egeria_tech_client):
        """Test search case sensitivity options."""
        client = live_egeria_tech_client
        
        # Test with ignore_case=True
        params = {"search_string": "digital", "ignore_case": True}
        result1 = await _async_run_report(
            "Digital-Products",
            client,
            output_format="DICT",
            params=params
        )
        
        # Test with ignore_case=False
        params = {"search_string": "digital", "ignore_case": False}
        result2 = await _async_run_report(
            "Digital-Products",
            client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result1)
        EgeriaAssertions.assert_valid_format_set_response(result2)


@pytest.mark.integration
@pytest.mark.slow
class TestEgeriaTechLiveErrorHandling:
    """Integration tests for error handling with live Egeria."""
    
    @pytest.mark.asyncio
    async def test_live_invalid_format_set(self, live_egeria_tech_client):
        """Test handling of invalid format set."""
        client = live_egeria_tech_client
        params = TestDataManager.get_test_params()
        
        with pytest.raises(ValueError) as exc_info:
            await _async_run_report(
                "Invalid-Format-Set-12345",
                client,
                output_format="DICT",
                params=params
            )
        
        assert "Invalid-Format-Set-12345" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_live_invalid_output_format(self, live_egeria_tech_client):
        """Test handling of invalid output format."""
        client = live_egeria_tech_client
        params = TestDataManager.get_test_params()
        
        with pytest.raises(ValueError) as exc_info:
            await _async_run_report(
                "Digital-Products",
                client,
                output_format="INVALID_FORMAT",
                params=params
            )
        
        assert "INVALID_FORMAT" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_live_connection_loss_recovery(self, live_egeria_tech_client):
        """Test recovery from connection loss."""
        client = live_egeria_tech_client
        
        # Close session to simulate connection loss
        client.close_session()
        
        # Verify session is closed
        assert client.get_token() is None
        
        # Recreate session
        new_token = client.create_egeria_bearer_token(client.user_id, client.user_pwd)
        EgeriaAssertions.assert_valid_bearer_token(new_token)
        
        # Test that operations work again
        params = TestDataManager.get_test_params()
        result = await _async_run_report(
            "Digital-Products",
            client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)


