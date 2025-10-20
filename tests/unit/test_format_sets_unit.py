"""
Unit tests for format set execution functionality.

These tests focus on the format set execution logic using mocks and monkeypatching.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock

from pyegeria.format_set_executor import _async_run_report, exec_format_set
from tests.fixtures.mock_responses import MockResponseFactory
from tests.utils.assertion_helpers import EgeriaAssertions
from tests.fixtures.test_data import TestDataManager, TestScenarioBuilder


@pytest.mark.unit
@pytest.mark.format_sets
class TestFormatSetExecutionUnit:
    """Unit tests for format set execution."""
    
    @pytest.mark.asyncio
    async def test_async_run_report_success(self, mock_egeria_tech_client):
        """Test successful async format set execution."""
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Digital-Products",
            mock_egeria_tech_client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
        assert isinstance(result["data"], list)
    
    @pytest.mark.asyncio
    async def test_async_run_report_empty_params(self, mock_egeria_tech_client):
        """Test async format set execution with empty parameters."""
        result = await _async_run_report(
            "Digital-Products",
            mock_egeria_tech_client,
            output_format="DICT",
            params={}
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
    
    @pytest.mark.asyncio
    async def test_async_run_report_none_params(self, mock_egeria_tech_client):
        """Test async format set execution with None parameters."""
        result = await _async_run_report(
            "Digital-Products",
            mock_egeria_tech_client,
            output_format="DICT",
            params=None
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
    
    @pytest.mark.asyncio
    async def test_async_run_report_invalid_format_set(self, mock_egeria_tech_client):
        """Test async format set execution with invalid format set."""
        params = TestDataManager.get_test_params()
        
        with pytest.raises(ValueError) as exc_info:
            await _async_run_report(
                "Invalid-Format-Set",
                mock_egeria_tech_client,
                output_format="DICT",
                params=params
            )
        
        assert "Invalid-Format-Set" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_async_run_report_invalid_output_format(self, mock_egeria_tech_client):
        """Test async format set execution with invalid output format."""
        params = TestDataManager.get_test_params()
        
        with pytest.raises(ValueError) as exc_info:
            await _async_run_report(
                "Digital-Products",
                mock_egeria_tech_client,
                output_format="INVALID_FORMAT",
                params=params
            )
        
        assert "INVALID_FORMAT" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_async_run_report_token_handling(self, mock_egeria_tech_client):
        """Test token handling in async format set execution."""
        params = TestDataManager.get_test_params()
        
        # Test with no existing token
        mock_egeria_tech_client.token = None
        result = await _async_run_report(
            "Digital-Products",
            mock_egeria_tech_client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        
        # Test with existing token
        mock_egeria_tech_client.token = "existing_token"
        result = await _async_run_report(
            "Digital-Products",
            mock_egeria_tech_client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
    
    @pytest.mark.asyncio
    async def test_async_run_report_function_resolution(self, mock_egeria_tech_client):
        """Test function resolution in async format set execution."""
        params = TestDataManager.get_test_params()
        
        # Test with valid function declaration
        result = await _async_run_report(
            "Digital-Products",
            mock_egeria_tech_client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
    
    @pytest.mark.asyncio
    async def test_async_run_report_parameter_passing(self, mock_egeria_tech_client):
        """Test parameter passing in async format set execution."""
        params = {
            "search_string": "test_search",
            "page_size": 5,
            "start_from": 0,
            "starts_with": True,
            "ends_with": False,
            "ignore_case": True
        }
        
        result = await _async_run_report(
            "Digital-Products",
            mock_egeria_tech_client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        EgeriaAssertions.assert_valid_search_params(params)
        EgeriaAssertions.assert_valid_pagination_params(params)


@pytest.mark.unit
@pytest.mark.format_sets
class TestFormatSetExecutionOutputFormats:
    """Unit tests for different output formats in format set execution."""
    
    @pytest.mark.asyncio
    async def test_dict_output_format(self, mock_egeria_tech_client):
        """Test DICT output format."""
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Digital-Products",
            mock_egeria_tech_client,
            output_format="DICT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
        EgeriaAssertions.assert_response_data_type(result, list)
    
    @pytest.mark.asyncio
    async def test_json_output_format(self, mock_egeria_tech_client):
        """Test JSON output format."""
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Digital-Products",
            mock_egeria_tech_client,
            output_format="JSON",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
        EgeriaAssertions.assert_response_data_type(result, list)
    
    @pytest.mark.asyncio
    async def test_report_output_format(self, mock_egeria_tech_client):
        """Test REPORT output format."""
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Digital-Products",
            mock_egeria_tech_client,
            output_format="REPORT",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "text"
        EgeriaAssertions.assert_markdown_response(result)
    
    @pytest.mark.asyncio
    async def test_mermaid_output_format(self, mock_egeria_tech_client):
        """Test MERMAID output format."""
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Digital-Products",
            mock_egeria_tech_client,
            output_format="MERMAID",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "text"
        EgeriaAssertions.assert_mermaid_response(result)
    
    @pytest.mark.asyncio
    async def test_html_output_format(self, mock_egeria_tech_client):
        """Test HTML output format."""
        params = TestDataManager.get_test_params()
        
        result = await _async_run_report(
            "Digital-Products",
            mock_egeria_tech_client,
            output_format="HTML",
            params=params
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "text"
        EgeriaAssertions.assert_html_response(result)


@pytest.mark.unit
@pytest.mark.format_sets
class TestFormatSetExecutionSync:
    """Unit tests for synchronous format set execution."""
    
    def test_exec_format_set_success(self):
        """Test successful synchronous format set execution."""
        with patch('pyegeria.format_set_executor.select_report_spec') as mock_select, \
             patch('pyegeria.format_set_executor._resolve_client_and_method') as mock_resolve, \
             patch('pyegeria.format_set_executor.settings') as mock_settings:
            
            # Mock the format set selection
            mock_select.return_value = {
                "action": {
                    "function": "CollectionManager._async_get_digital_products",
                    "required_params": [],
                    "optional_params": ["search_string"],
                    "spec_params": {}
                }
            }
            
            # Mock client resolution
            mock_client_class = Mock()
            mock_client_instance = Mock()
            mock_client_instance.create_egeria_bearer_token.return_value = "token"
            mock_client_instance._async_get_digital_products.return_value = MockResponseFactory.create_digital_products_response()
            mock_client_class.return_value = mock_client_instance
            mock_resolve.return_value = (mock_client_class, "_async_get_digital_products")
            
            # Mock settings
            mock_settings.Environment.egeria_view_server = "test-server"
            mock_settings.Environment.egeria_view_server_url = "https://test.com"
            mock_settings.User_Profile.user_name = "test_user"
            mock_settings.User_Profile.user_pwd = "test_pass"
            
            result = exec_format_set(
                "Digital-Products",
                output_format="DICT",
                params={"search_string": "*"}
            )
            
            EgeriaAssertions.assert_valid_format_set_response(result)
            assert result["kind"] == "json"
    
    def test_exec_format_set_invalid_format_set(self):
        """Test synchronous format set execution with invalid format set."""
        with patch('pyegeria.format_set_executor.select_report_spec') as mock_select:
            mock_select.return_value = None
            
            with pytest.raises(ValueError) as exc_info:
                exec_format_set(
                    "Invalid-Format-Set",
                    output_format="DICT",
                    params={}
                )
            
            assert "Invalid-Format-Set" in str(exc_info.value)
    
    def test_exec_format_set_missing_action(self):
        """Test synchronous format set execution with missing action."""
        with patch('pyegeria.format_set_executor.select_report_spec') as mock_select:
            mock_select.return_value = {"name": "test"}  # Missing action
            
            with pytest.raises(ValueError) as exc_info:
                exec_format_set(
                    "Digital-Products",
                    output_format="DICT",
                    params={}
                )
            
            assert "action property" in str(exc_info.value)
    
    def test_exec_format_set_missing_function(self):
        """Test synchronous format set execution with missing function."""
        with patch('pyegeria.format_set_executor.select_report_spec') as mock_select:
            mock_select.return_value = {
                "action": {
                    "required_params": [],
                    "optional_params": [],
                    "spec_params": {}
                }
            }
            
            with pytest.raises(ValueError) as exc_info:
                exec_format_set(
                    "Digital-Products",
                    output_format="DICT",
                    params={}
                )
            
            assert "function" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.format_sets
class TestFormatSetExecutionScenarios:
    """Unit tests for various format set execution scenarios."""
    
    @pytest.mark.asyncio
    async def test_scenario_digital_products(self, mock_egeria_tech_client):
        """Test Digital-Products execution scenario."""
        scenarios = TestScenarioBuilder.build_format_set_scenarios()
        digital_products_scenario = next(
            (s for s in scenarios if s["format_set"] == "Digital-Products"), 
            None
        )
        
        assert digital_products_scenario is not None
        
        result = await _async_run_report(
            digital_products_scenario["format_set"],
            mock_egeria_tech_client,
            output_format="DICT",
            params=digital_products_scenario["params"]
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == digital_products_scenario["expected_kind"]
    
    @pytest.mark.asyncio
    async def test_scenario_glossary_terms(self, mock_egeria_tech_client):
        """Test Glossary-Terms execution scenario."""
        scenarios = TestScenarioBuilder.build_format_set_scenarios()
        glossary_terms_scenario = next(
            (s for s in scenarios if s["format_set"] == "Glossary-Terms"), 
            None
        )
        
        assert glossary_terms_scenario is not None
        
        result = await _async_run_report(
            glossary_terms_scenario["format_set"],
            mock_egeria_tech_client,
            output_format="DICT",
            params=glossary_terms_scenario["params"]
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == glossary_terms_scenario["expected_kind"]
    
    @pytest.mark.asyncio
    async def test_scenario_data_assets(self, mock_egeria_tech_client):
        """Test Data-Assets execution scenario."""
        scenarios = TestScenarioBuilder.build_format_set_scenarios()
        data_assets_scenario = next(
            (s for s in scenarios if s["format_set"] == "Data-Assets"), 
            None
        )
        
        assert data_assets_scenario is not None
        
        result = await _async_run_report(
            data_assets_scenario["format_set"],
            mock_egeria_tech_client,
            output_format="DICT",
            params=data_assets_scenario["params"]
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == data_assets_scenario["expected_kind"]
    
    @pytest.mark.asyncio
    async def test_scenario_collections(self, mock_egeria_tech_client):
        """Test Collections execution scenario."""
        scenarios = TestScenarioBuilder.build_format_set_scenarios()
        collections_scenario = next(
            (s for s in scenarios if s["format_set"] == "Collections"), 
            None
        )
        
        assert collections_scenario is not None
        
        result = await _async_run_report(
            collections_scenario["format_set"],
            mock_egeria_tech_client,
            output_format="DICT",
            params=collections_scenario["params"]
        )
        
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == collections_scenario["expected_kind"]


@pytest.mark.unit
@pytest.mark.format_sets
class TestFormatSetExecutionErrorHandling:
    """Unit tests for error handling in format set execution."""
    
    @pytest.mark.asyncio
    async def test_async_run_report_function_not_found(self, mock_egeria_tech_client):
        """Test handling when function is not found."""
        with patch('pyegeria.format_set_executor.select_report_spec') as mock_select:
            mock_select.return_value = {
                "action": {
                    "function": "NonExistentManager.non_existent_method",
                    "required_params": [],
                    "optional_params": [],
                    "spec_params": {}
                }
            }
            
            with pytest.raises(TypeError) as exc_info:
                await _async_run_report(
                    "Digital-Products",
                    mock_egeria_tech_client,
                    output_format="DICT",
                    params={}
                )
            
            assert "not found" in str(exc_info.value) or "not callable" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_async_run_report_function_call_error(self, mock_egeria_tech_client):
        """Test handling when function call raises an error."""
        with patch.object(mock_egeria_tech_client, '_async_get_digital_products', 
                         side_effect=Exception("API Error")):
            with pytest.raises(Exception) as exc_info:
                await _async_run_report(
                    "Digital-Products",
                    mock_egeria_tech_client,
                    output_format="DICT",
                    params={}
                )
            
            assert "API Error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_async_run_report_token_creation_error(self, mock_egeria_tech_client):
        """Test handling when token creation fails."""
        with patch.object(mock_egeria_tech_client, '_async_create_egeria_bearer_token',
                         side_effect=Exception("Token creation failed")):
            # Should not fail the entire call, should handle gracefully
            result = await _async_run_report(
                "Digital-Products",
                mock_egeria_tech_client,
                output_format="DICT",
                params={}
            )
            
            EgeriaAssertions.assert_valid_format_set_response(result)
    
    @pytest.mark.asyncio
    async def test_async_run_report_empty_result(self, mock_egeria_tech_client):
        """Test handling of empty results."""
        with patch.object(mock_egeria_tech_client, '_async_get_digital_products',
                         return_value=None):
            result = await _async_run_report(
                "Digital-Products",
                mock_egeria_tech_client,
                output_format="DICT",
                params={}
            )
            
            EgeriaAssertions.assert_valid_format_set_response(result)
            assert result["kind"] == "empty"
    
    @pytest.mark.asyncio
    async def test_async_run_report_no_elements_found(self, mock_egeria_tech_client):
        """Test handling of NO_ELEMENTS_FOUND result."""
        from pyegeria._globals import NO_ELEMENTS_FOUND
        
        with patch.object(mock_egeria_tech_client, '_async_get_digital_products',
                         return_value=NO_ELEMENTS_FOUND):
            result = await _async_run_report(
                "Digital-Products",
                mock_egeria_tech_client,
                output_format="DICT",
                params={}
            )
            
            EgeriaAssertions.assert_valid_format_set_response(result)
            assert result["kind"] == "empty"


