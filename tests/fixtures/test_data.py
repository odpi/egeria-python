"""
Test data management for EgeriaTech testing.

This module provides test data and utilities for different testing scenarios.
"""

from typing import Dict, List, Any, Optional, Union


class TestDataManager:
    """Manage test data for different scenarios."""
    
    @staticmethod
    def get_test_format_sets() -> List[str]:
        """Get list of test format sets."""
        return [
            "Digital-Products",
            "Glossary-Terms", 
            "External-References",
            "Collections",
            "Governance-Definitions",
            "Reference-Data",
            "Valid-Metadata"
        ]
    
    @staticmethod
    def get_test_params() -> Dict[str, Any]:
        """Get standard test parameters."""
        return {
            "search_string": "*",
            "page_size": 10,
            "start_from": 0,
            "starts_with": True,
            "ends_with": False,
            "ignore_case": True
        }
    
    @staticmethod
    def get_test_credentials() -> Dict[str, str]:
        """Get test credentials."""
        return {
            "user_id": "test_user",
            "user_pwd": "test_password",
            "view_server": "test-view-server",
            "platform_url": "https://test-egeria.com:9443"
        }
    
    @staticmethod
    def get_test_output_formats() -> List[str]:
        """Get test output formats."""
        return ["DICT", "JSON", "REPORT", "MERMAID", "HTML"]
    
    @staticmethod
    def get_test_guids() -> List[str]:
        """Get test GUIDs."""
        return [
            "guid-001",
            "guid-002", 
            "guid-003",
            "guid-004",
            "guid-005"
        ]
    
    @staticmethod
    def get_test_search_strings() -> List[str]:
        """Get test search strings."""
        return [
            "*",
            "test*",
            "*product*",
            "Digital*",
            "Asset*"
        ]
    
    @staticmethod
    def get_test_pagination_params() -> List[Dict[str, Any]]:
        """Get test pagination parameters."""
        return [
            {"page_size": 5, "start_from": 0},
            {"page_size": 10, "start_from": 0},
            {"page_size": 20, "start_from": 0},
            {"page_size": 10, "start_from": 10},
            {"page_size": 10, "start_from": 20}
        ]
    
    @staticmethod
    def get_test_error_scenarios() -> List[Dict[str, Any]]:
        """Get test error scenarios."""
        return [
            {
                "name": "invalid_credentials",
                "error_type": "AuthenticationError",
                "message": "Invalid credentials provided"
            },
            {
                "name": "connection_timeout",
                "error_type": "TimeoutError", 
                "message": "Connection timeout"
            },
            {
                "name": "server_error",
                "error_type": "ServerError",
                "message": "Internal server error"
            },
            {
                "name": "not_found",
                "error_type": "NotFoundError",
                "message": "Resource not found"
            }
        ]


class TestScenarioBuilder:
    """Build test scenarios with different combinations of parameters."""
    
    @staticmethod
    def build_format_set_scenarios() -> List[Dict[str, Any]]:
        """Build test scenarios for format set execution."""
        scenarios = []
        format_sets = TestDataManager.get_test_format_sets()
        params = TestDataManager.get_test_params()
        
        for format_set in format_sets:
            scenarios.append({
                "name": f"test_{format_set.lower().replace('-', '_')}",
                "format_set": format_set,
                "params": params,
                "expected_kind": "json"
            })
        
        return scenarios
    
    @staticmethod
    def build_output_format_scenarios() -> List[Dict[str, Any]]:
        """Build test scenarios for different output formats."""
        scenarios = []
        format_sets = ["Digital-Products", "Terms"]
        output_formats = TestDataManager.get_test_output_formats()
        
        for format_set in format_sets:
            for output_format in output_formats:
                scenarios.append({
                    "name": f"test_{format_set.lower().replace('-', '_')}_{output_format.lower()}",
                    "format_set": format_set,
                    "output_format": output_format,
                    "params": TestDataManager.get_test_params()
                })
        
        return scenarios
    
    @staticmethod
    def build_pagination_scenarios() -> List[Dict[str, Any]]:
        """Build test scenarios for pagination."""
        scenarios = []
        format_set = "Digital-Products"
        pagination_params = TestDataManager.get_test_pagination_params()
        
        for i, params in enumerate(pagination_params):
            scenarios.append({
                "name": f"test_pagination_scenario_{i+1}",
                "format_set": format_set,
                "params": params,
                "expected_page_size": params["page_size"],
                "expected_start_from": params["start_from"]
            })
        
        return scenarios
    
    @staticmethod
    def build_search_scenarios() -> List[Dict[str, Any]]:
        """Build test scenarios for search functionality."""
        scenarios = []
        format_set = "Digital-Products"
        search_strings = TestDataManager.get_test_search_strings()
        
        for search_string in search_strings:
            scenarios.append({
                "name": f"test_search_{search_string.replace('*', 'wildcard')}",
                "format_set": format_set,
                "params": {"search_string": search_string},
                "expected_search": search_string
            })
        
        return scenarios


class TestConstants:
    """Constants for testing."""
    
    # Timeouts
    DEFAULT_TIMEOUT = 30
    LONG_TIMEOUT = 60
    SHORT_TIMEOUT = 5
    
    # Test data sizes
    SMALL_DATASET_SIZE = 5
    MEDIUM_DATASET_SIZE = 10
    LARGE_DATASET_SIZE = 50
    
    # Mock response sizes
    DEFAULT_MOCK_COUNT = 5
    EMPTY_MOCK_COUNT = 0
    LARGE_MOCK_COUNT = 100
    
    # Error codes
    AUTH_ERROR_CODE = "AUTH_ERROR"
    TIMEOUT_ERROR_CODE = "TIMEOUT_ERROR"
    SERVER_ERROR_CODE = "SERVER_ERROR"
    NOT_FOUND_ERROR_CODE = "NOT_FOUND_ERROR"
    
    # Test markers
    UNIT_MARKER = "unit"
    INTEGRATION_MARKER = "integration"
    SLOW_MARKER = "slow"
    AUTH_MARKER = "auth"
    FORMAT_SETS_MARKER = "format_sets"
    MCP_MARKER = "mcp"
