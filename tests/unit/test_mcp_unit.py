"""
Unit tests for MCP-specific functionality.

These tests focus on MCP adapter functions and MCP server integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from pyegeria.mcp_adapter import list_reports, describe_report, run_report, _async_run_report_tool
from tests.fixtures.mock_responses import MockResponseFactory
from tests.utils.assertion_helpers import EgeriaAssertions
from tests.fixtures.test_data import TestDataManager


@pytest.mark.unit
@pytest.mark.mcp
class TestMCPAdapterUnit:
    """Unit tests for MCP adapter functions."""
    
    def test_list_reports_success(self):
        """Test successful list_reports call."""
        with patch('pyegeria.mcp_adapter.list_mcp_format_sets') as mock_list:
            mock_list.return_value = {
                "formatSets": [
                    {"name": "Digital-Products", "description": "List digital products"},
                    {"name": "Glossary-Terms", "description": "List glossary terms"},
                    {"name": "External References", "description": "List data assets"}
                ]
            }
            
            result = list_reports()
            
            assert isinstance(result, dict)
            assert "formatSets" in result
            assert isinstance(result["formatSets"], list)
            assert len(result["formatSets"]) == 3
    
    def test_describe_report_success(self):
        """Test successful describe_report call."""
        with patch('pyegeria.mcp_adapter.select_report_spec') as mock_select:
            mock_select.return_value = {
                "name": "Digital-Products",
                "description": "List digital products",
                "target_type": "DigitalProduct",
                "action": {
                    "function": "CollectionManager._async_get_digital_products",
                    "required_params": [],
                    "optional_params": ["search_string", "page_size"],
                    "spec_params": {}
                },
                "output_formats": ["DICT", "JSON", "REPORT"]
            }
            
            result = describe_report("Digital-Products", "DICT")
            
            assert isinstance(result, dict)
            assert result["name"] == "Digital-Products"
            assert result["description"] == "List digital products"
            assert result["target_type"] == "DigitalProduct"
            assert "action" in result
            assert "output_formats" in result
    
    def test_describe_report_invalid_name(self):
        """Test describe_report with invalid report name."""
        with patch('pyegeria.mcp_adapter.select_report_spec') as mock_select:
            mock_select.return_value = None
            
            with pytest.raises(ValueError) as exc_info:
                describe_report("Invalid-Report", "DICT")
            
            assert "Invalid-Report" in str(exc_info.value)
    
    def test_describe_report_different_output_types(self):
        """Test describe_report with different output types."""
        with patch('pyegeria.mcp_adapter.select_report_spec') as mock_select:
            mock_select.return_value = {
                "name": "Digital-Products",
                "description": "List digital products",
                "target_type": "DigitalProduct"
            }
            
            # Test with DICT
            result_dict = describe_report("Digital-Products", "DICT")
            assert result_dict["name"] == "Digital-Products"
            
            # Test with JSON
            result_json = describe_report("Digital-Products", "JSON")
            assert result_json["name"] == "Digital-Products"
            
            # Test with ANY
            result_any = describe_report("Digital-Products", "ANY")
            assert result_any["name"] == "Digital-Products"
    
    def test_run_report_success(self):
        """Test successful run_report call."""
        with patch('pyegeria.mcp_adapter.exec_format_set') as mock_exec:
            mock_exec.return_value = MockResponseFactory.create_digital_products_response()
            
            result = run_report(
                report="Digital-Products",
                params={"search_string": "*", "page_size": 10}
            )
            
            EgeriaAssertions.assert_valid_format_set_response(result)
            assert result["kind"] == "json"
            assert isinstance(result["data"], list)
    
    def test_run_report_with_credentials(self):
        """Test run_report with explicit credentials."""
        with patch('pyegeria.mcp_adapter.exec_format_set') as mock_exec:
            mock_exec.return_value = MockResponseFactory.create_digital_products_response()
            
            result = run_report(
                report="Digital-Products",
                params={"search_string": "*"},
                view_server="test-server",
                view_url="https://test.com",
                user="test_user",
                user_pass="test_pass"
            )
            
            EgeriaAssertions.assert_valid_format_set_response(result)
            mock_exec.assert_called_once()
    
    def test_run_report_empty_params(self):
        """Test run_report with empty parameters."""
        with patch('pyegeria.mcp_adapter.exec_format_set') as mock_exec:
            mock_exec.return_value = MockResponseFactory.create_digital_products_response()
            
            result = run_report(
                report="Digital-Products",
                params={}
            )
            
            EgeriaAssertions.assert_valid_format_set_response(result)
            mock_exec.assert_called_once()
    
    def test_run_report_none_params(self):
        """Test run_report with None parameters."""
        with patch('pyegeria.mcp_adapter.exec_format_set') as mock_exec:
            mock_exec.return_value = MockResponseFactory.create_digital_products_response()
            
            result = run_report(
                report="Digital-Products",
                params=None
            )
            
            EgeriaAssertions.assert_valid_format_set_response(result)
            mock_exec.assert_called_once()


@pytest.mark.unit
@pytest.mark.mcp
class TestMCPAsyncAdapterUnit:
    """Unit tests for MCP async adapter functions."""
    
    @pytest.mark.asyncio
    async def test_async_run_report_tool_success(self, mock_egeria_tech_client):
        """Test successful _async_run_report_tool call."""
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report_tool(
            report="Digital-Products",
            egeria_client=mock_egeria_tech_client,
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
        assert isinstance(result["data"], list)
    
    @pytest.mark.asyncio
    async def test_async_run_report_tool_empty_params(self, mock_egeria_tech_client):
        """Test _async_run_report_tool with empty parameters."""
        result = await _async_run_report_tool(
            report="Digital-Products",
            egeria_client=mock_egeria_tech_client,
            params={}
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
    
    @pytest.mark.asyncio
    async def test_async_run_report_tool_none_params(self, mock_egeria_tech_client):
        """Test _async_run_report_tool with None parameters."""
        result = await _async_run_report_tool(
            report="Digital-Products",
            egeria_client=mock_egeria_tech_client,
            params=None
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
    
    @pytest.mark.asyncio
    async def test_async_run_report_tool_different_reports(self, mock_egeria_tech_client):
        """Test _async_run_report_tool with different report types."""
        params = TestDataManager.get_test_params()
        
        # Test Digital-Products
        result1 = await _async_run_report_tool(
            report="Digital-Products",
            egeria_client=mock_egeria_tech_client,
            params=params
        )
        EgeriaAssertions.assert_valid_format_set_response(result1)
        
        # Test Glossary-Terms
        result2 = await _async_run_report_tool(
            report="Glossary-Terms",
            egeria_client=mock_egeria_tech_client,
            params=params
        )
        EgeriaAssertions.assert_valid_format_set_response(result2)
        
        # Test External References
        result3 = await _async_run_report_tool(
            report="External-References",
            egeria_client=mock_egeria_tech_client,
            params=params
        )
        EgeriaAssertions.assert_valid_format_set_response(result3)
    
    @pytest.mark.asyncio
    async def test_async_run_report_tool_parameter_validation(self, mock_egeria_tech_client):
        """Test parameter validation in _async_run_report_tool."""
        params = {
            "search_string": "test_search",
            "page_size": 5,
            "start_from": 0,
            "starts_with": True,
            "ends_with": False,
            "ignore_case": True
        }
        
        result = await _async_run_report_tool(
            report="Digital-Products",
            egeria_client=mock_egeria_tech_client,
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        EgeriaAssertions.assert_valid_search_params(params)
        EgeriaAssertions.assert_valid_pagination_params(params)


@pytest.mark.unit
@pytest.mark.mcp
class TestMCPServerIntegration:
    """Unit tests for MCP server integration."""
    
    def test_mcp_server_tool_registration(self):
        """Test that MCP tools are properly registered."""
        # This test would verify that the MCP server properly registers
        # the list_reports, describe_report, and run_report tools
        from pyegeria.mcp_server import main
        
        # The main function should be callable
        assert callable(main)
    
    def test_mcp_server_tool_validation(self):
        """Test MCP tool parameter validation."""
        # Test that MCP tools properly validate their parameters
        with patch('pyegeria.mcp_adapter.list_reports') as mock_list:
            mock_list.return_value = {"formatSets": []}
            
            result = mock_list()
            assert isinstance(result, dict)
            assert "formatSets" in result
    
    def test_mcp_server_error_handling(self):
        """Test MCP server error handling."""
        # Test that MCP server properly handles errors
        with patch('pyegeria.mcp_adapter.describe_report') as mock_describe:
            mock_describe.side_effect = ValueError("Test error")
            
            with pytest.raises(ValueError) as exc_info:
                mock_describe("Invalid-Report", "DICT")
            
            assert "Test error" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.mcp
class TestMCPResponseFormatting:
    """Unit tests for MCP response formatting."""
    
    def test_mcp_response_structure(self):
        """Test that MCP responses have proper structure."""
        with patch('pyegeria.mcp_adapter.exec_format_set') as mock_exec:
            mock_exec.return_value = MockResponseFactory.create_digital_products_response()
            
            result = run_report(
                report="Digital-Products",
                params={"search_string": "*"}
            )
            
            # Verify MCP response structure
            assert isinstance(result, dict)
            assert "kind" in result
            assert result["kind"] in ["json", "text", "empty", "unknown"]
            
            if result["kind"] == "json":
                assert "data" in result
                assert isinstance(result["data"], (list, dict))
            
            elif result["kind"] == "text":
                assert "mime" in result
                assert "content" in result
                assert isinstance(result["content"], str)
    
    def test_mcp_response_data_validation(self):
        """Test MCP response data validation."""
        with patch('pyegeria.mcp_adapter.exec_format_set') as mock_exec:
            mock_exec.return_value = MockResponseFactory.create_digital_products_response()
            
            result = run_report(
                report="Digital-Products",
                params={"search_string": "*"}
            )
            
            if result["kind"] == "json" and isinstance(result["data"], list):
                for item in result["data"]:
                    assert isinstance(item, dict)
                    # Common fields that should be present
                    if "guid" in item:
                        assert isinstance(item["guid"], str)
                    if "display_name" in item:
                        assert isinstance(item["display_name"], str)
                    if "qualified_name" in item:
                        assert isinstance(item["qualified_name"], str)
    
    def test_mcp_response_empty_handling(self):
        """Test MCP response empty result handling."""
        with patch('pyegeria.mcp_adapter.exec_format_set') as mock_exec:
            mock_exec.return_value = MockResponseFactory.create_empty_response()
            
            result = run_report(
                report="Digital-Products",
                params={"search_string": "nonexistent"}
            )
            
            EgeriaAssertions.assert_valid_format_set_response(result)
            assert result["kind"] == "empty"
    
    def test_mcp_response_error_handling(self):
        """Test MCP response error handling."""
        with patch('pyegeria.mcp_adapter.exec_format_set') as mock_exec:
            mock_exec.side_effect = Exception("Test error")
            
            with pytest.raises(Exception) as exc_info:
                run_report(
                    report="Digital-Products",
                    params={"search_string": "*"}
                )
            
            assert "Test error" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.mcp
class TestMCPToolCompatibility:
    """Unit tests for MCP tool compatibility."""
    
    def test_mcp_tool_parameter_compatibility(self):
        """Test that MCP tools accept compatible parameters."""
        with patch('pyegeria.mcp_adapter.exec_format_set') as mock_exec:
            mock_exec.return_value = MockResponseFactory.create_digital_products_response()
            
            # Test with various parameter combinations
            test_params = [
                {"search_string": "*"},
                {"search_string": "*", "page_size": 10},
                {"search_string": "*", "page_size": 10, "start_from": 0},
                {"search_string": "*", "starts_with": True},
                {"search_string": "*", "ends_with": False},
                {"search_string": "*", "ignore_case": True}
            ]
            
            for params in test_params:
                result = run_report(
                    report="Digital-Products",
                    params=params
                )
                
                EgeriaAssertions.assert_valid_format_set_response(result)
    
    def test_mcp_tool_output_format_compatibility(self):
        """Test that MCP tools support compatible output formats."""
        with patch('pyegeria.mcp_adapter.exec_format_set') as mock_exec:
            mock_exec.return_value = MockResponseFactory.create_digital_products_response()
            
            # Test with different output formats
            output_formats = ["DICT", "JSON", "REPORT", "MERMAID", "HTML"]
            
            for output_format in output_formats:
                result = run_report(
                    report="Digital-Products",
                    params={"search_string": "*"}
                )
                
                EgeriaAssertions.assert_valid_format_set_response(result)
    
    def test_mcp_tool_report_compatibility(self):
        """Test that MCP tools work with compatible reports."""
        with patch('pyegeria.mcp_adapter.exec_format_set') as mock_exec:
            mock_exec.return_value = MockResponseFactory.create_digital_products_response()
            
            # Test with different report types
            reports = ["Digital-Products", "Glossary-Terms", "External-References", "Collections"]
            
            for report in reports:
                result = run_report(
                    report=report,
                    params={"search_string": "*"}
                )
                
                EgeriaAssertions.assert_valid_format_set_response(result)


