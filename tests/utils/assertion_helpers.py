"""
Assertion helpers for EgeriaTech testing.

This module provides custom assertions for Egeria-specific response validation.
"""

from typing import Dict, List, Any, Optional, Union
import pytest


class EgeriaAssertions:
    """Custom assertions for Egeria-specific response validation."""
    
    @staticmethod
    def assert_valid_format_set_response(response: Dict[str, Any]) -> None:
        """Assert that a format set response has valid structure."""
        assert isinstance(response, dict), "Response must be a dictionary"
        assert "kind" in response, "Response must have 'kind' field"
        assert response["kind"] in ["json", "text", "empty", "unknown"], \
            f"Invalid response kind: {response['kind']}"
        
        if response["kind"] == "json":
            assert "data" in response, "JSON response must have 'data' field"
            assert isinstance(response["data"], (list, dict)), \
                "JSON data must be list or dict"
        
        elif response["kind"] == "text":
            assert "mime" in response, "Text response must have 'mime' field"
            assert "content" in response, "Text response must have 'content' field"
            assert isinstance(response["content"], str), \
                "Text content must be string"
    
    @staticmethod
    def assert_valid_mcp_tool_response(response: Dict[str, Any]) -> None:
        """Assert that an MCP tool response has valid structure."""
        EgeriaAssertions.assert_valid_format_set_response(response)
        
        # Additional MCP-specific validations
        if response["kind"] == "json":
            data = response["data"]
            if isinstance(data, list) and len(data) > 0:
                # Check that list items have expected structure
                item = data[0]
                assert isinstance(item, dict), "List items must be dictionaries"
                # Common fields that should be present
                common_fields = ["guid", "display_name", "qualified_name"]
                for field in common_fields:
                    if field in item:
                        assert isinstance(item[field], str), \
                            f"Field '{field}' must be string"
    
    @staticmethod
    def assert_valid_bearer_token(token: str) -> None:
        """Assert that a bearer token is valid."""
        assert isinstance(token, str), "Bearer token must be string"
        assert len(token) > 0, "Bearer token cannot be empty"
        assert not token.isspace(), "Bearer token cannot be whitespace only"
    
    @staticmethod
    def assert_valid_connection_response(response: str) -> None:
        """Assert that a connection response is valid."""
        assert isinstance(response, str), "Connection response must be string"
        assert len(response) > 0, "Connection response cannot be empty"
        assert not response.isspace(), "Connection response cannot be whitespace only"
    
    @staticmethod
    def assert_valid_pagination_params(params: Dict[str, Any]) -> None:
        """Assert that pagination parameters are valid."""
        if "page_size" in params:
            assert isinstance(params["page_size"], int), \
                "page_size must be integer"
            assert params["page_size"] > 0, "page_size must be positive"
        
        if "start_from" in params:
            assert isinstance(params["start_from"], int), \
                "start_from must be integer"
            assert params["start_from"] >= 0, "start_from must be non-negative"
    
    @staticmethod
    def assert_valid_search_params(params: Dict[str, Any]) -> None:
        """Assert that search parameters are valid."""
        if "search_string" in params:
            assert isinstance(params["search_string"], str), \
                "search_string must be string"
        
        if "starts_with" in params:
            assert isinstance(params["starts_with"], bool), \
                "starts_with must be boolean"
        
        if "ends_with" in params:
            assert isinstance(params["ends_with"], bool), \
                "ends_with must be boolean"
        
        if "ignore_case" in params:
            assert isinstance(params["ignore_case"], bool), \
                "ignore_case must be boolean"
    
    @staticmethod
    def assert_response_contains_expected_fields(
        response: Dict[str, Any], 
        expected_fields: List[str]
    ) -> None:
        """Assert that response contains expected fields."""
        if response["kind"] == "json" and isinstance(response["data"], list):
            if len(response["data"]) > 0:
                item = response["data"][0]
                for field in expected_fields:
                    assert field in item, f"Response missing expected field: {field}"
    
    @staticmethod
    def assert_response_data_type(
        response: Dict[str, Any], 
        expected_type: Union[type, tuple]
    ) -> None:
        """Assert that response data is of expected type."""
        if response["kind"] == "json":
            assert isinstance(response["data"], expected_type), \
                f"Expected data type {expected_type}, got {type(response['data'])}"
    
    @staticmethod
    def assert_response_not_empty(response: Dict[str, Any]) -> None:
        """Assert that response is not empty."""
        assert response["kind"] != "empty", "Response should not be empty"
        
        if response["kind"] == "json":
            if isinstance(response["data"], list):
                assert len(response["data"]) > 0, "JSON list should not be empty"
            elif isinstance(response["data"], dict):
                assert len(response["data"]) > 0, "JSON dict should not be empty"
    
    @staticmethod
    def assert_response_has_guid(response: Dict[str, Any]) -> None:
        """Assert that response contains valid GUIDs."""
        if response["kind"] == "json" and isinstance(response["data"], list):
            for item in response["data"]:
                if "guid" in item:
                    assert isinstance(item["guid"], str), "GUID must be string"
                    assert len(item["guid"]) > 0, "GUID cannot be empty"
    
    @staticmethod
    def assert_response_has_display_name(response: Dict[str, Any]) -> None:
        """Assert that response contains display names."""
        if response["kind"] == "json" and isinstance(response["data"], list):
            for item in response["data"]:
                if "display_name" in item:
                    assert isinstance(item["display_name"], str), \
                        "display_name must be string"
                    assert len(item["display_name"]) > 0, \
                        "display_name cannot be empty"
    
    @staticmethod
    def assert_error_response(response: Dict[str, Any]) -> None:
        """Assert that response indicates an error."""
        assert "kind" in response, "Error response must have 'kind' field"
        assert response["kind"] in ["error", "empty"], \
            f"Expected error response, got: {response['kind']}"
    
    @staticmethod
    def assert_text_response_format(response: Dict[str, Any]) -> None:
        """Assert that text response has proper format."""
        assert response["kind"] == "text", "Response must be text type"
        assert "mime" in response, "Text response must have mime type"
        assert "content" in response, "Text response must have content"
        assert isinstance(response["content"], str), "Content must be string"
    
    @staticmethod
    def assert_html_response(response: Dict[str, Any]) -> None:
        """Assert that response is valid HTML."""
        EgeriaAssertions.assert_text_response_format(response)
        assert response["mime"] == "text/html", "Response must be HTML mime type"
        assert "<" in response["content"], "HTML content should contain tags"
    
    @staticmethod
    def assert_markdown_response(response: Dict[str, Any]) -> None:
        """Assert that response is valid Markdown."""
        EgeriaAssertions.assert_text_response_format(response)
        assert response["mime"] == "text/markdown", "Response must be Markdown mime type"
    
    @staticmethod
    def assert_mermaid_response(response: Dict[str, Any]) -> None:
        """Assert that response contains Mermaid diagram."""
        EgeriaAssertions.assert_markdown_response(response)
        content = response["content"]
        assert "```mermaid" in content or "graph" in content.lower(), \
            "Response should contain Mermaid diagram"


class PerformanceAssertions:
    """Assertions for performance testing."""
    
    @staticmethod
    def assert_response_time_within_limit(
        response_time: float, 
        max_time: float
    ) -> None:
        """Assert that response time is within acceptable limits."""
        assert response_time <= max_time, \
            f"Response time {response_time}s exceeds limit {max_time}s"
    
    @staticmethod
    def assert_memory_usage_reasonable(
        memory_usage: float, 
        max_memory: float
    ) -> None:
        """Assert that memory usage is reasonable."""
        assert memory_usage <= max_memory, \
            f"Memory usage {memory_usage}MB exceeds limit {max_memory}MB"


class ContractAssertions:
    """Assertions for API contract validation."""
    
    @staticmethod
    def assert_api_contract_compliance(
        response: Dict[str, Any], 
        expected_schema: Dict[str, Any]
    ) -> None:
        """Assert that response complies with API contract."""
        # Basic structure validation
        for required_field in expected_schema.get("required_fields", []):
            assert required_field in response, \
                f"Missing required field: {required_field}"
        
        # Type validation
        for field, expected_type in expected_schema.get("field_types", {}).items():
            if field in response:
                assert isinstance(response[field], expected_type), \
                    f"Field '{field}' must be {expected_type}"
    
    @staticmethod
    def assert_backward_compatibility(
        old_response: Dict[str, Any], 
        new_response: Dict[str, Any]
    ) -> None:
        """Assert that new response is backward compatible."""
        # Check that all fields from old response exist in new response
        for field in old_response:
            assert field in new_response, \
                f"Backward compatibility broken: missing field '{field}'"


