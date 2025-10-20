"""
Unit tests for EgeriaTech synchronous methods.

These tests use monkeypatching and mocks to test EgeriaTech functionality
without requiring a live Egeria instance.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from pyegeria.egeria_tech_client import EgeriaTech
from tests.fixtures.mock_responses import MockResponseFactory
from tests.utils.assertion_helpers import EgeriaAssertions
from tests.fixtures.test_data import TestDataManager


@pytest.mark.unit
class TestEgeriaTechUnit:
    """Unit tests for EgeriaTech core functionality."""
    
    def test_egeria_tech_initialization(self, test_credentials):
        """Test EgeriaTech initialization with credentials."""
        client = EgeriaTech(
            view_server=test_credentials["view_server"],
            platform_url=test_credentials["platform_url"],
            user_id=test_credentials["user_id"],
            user_pwd=test_credentials["user_pwd"]
        )
        
        assert client.view_server == test_credentials["view_server"]
        assert client.platform_url == test_credentials["platform_url"]
        assert client.user_id == test_credentials["user_id"]
        assert client.user_pwd == test_credentials["user_pwd"]
        assert hasattr(client, "_subclients")
        assert len(client._subclients) > 0
    
    def test_create_bearer_token_success(self, mock_egeria_tech_client):
        """Test successful bearer token creation."""
        token = mock_egeria_tech_client.create_egeria_bearer_token("user", "pass")
        
        EgeriaAssertions.assert_valid_bearer_token(token)
        assert mock_egeria_tech_client.get_token() == token
        
        # Verify token was set on all sub-clients
        for sub_client in mock_egeria_tech_client._subclients:
            assert sub_client.get_token() == token
    
    def test_create_bearer_token_with_none_credentials(self, mock_egeria_tech_client):
        """Test bearer token creation with None credentials."""
        token = mock_egeria_tech_client.create_egeria_bearer_token(None, None)
        
        EgeriaAssertions.assert_valid_bearer_token(token)
        assert mock_egeria_tech_client.get_token() == token
    
    def test_set_bearer_token(self, mock_egeria_tech_client):
        """Test setting bearer token directly."""
        test_token = "test_token_12345"
        mock_egeria_tech_client.set_bearer_token(test_token)
        
        assert mock_egeria_tech_client.get_token() == test_token
        
        # Verify token was set on all sub-clients
        for sub_client in mock_egeria_tech_client._subclients:
            assert sub_client.get_token() == test_token
    
    def test_get_token(self, mock_egeria_tech_client):
        """Test getting bearer token."""
        # Initially no token
        token = mock_egeria_tech_client.get_token()
        assert token is None
        
        # After creating token
        created_token = mock_egeria_tech_client.create_egeria_bearer_token("user", "pass")
        retrieved_token = mock_egeria_tech_client.get_token()
        
        assert retrieved_token == created_token
        EgeriaAssertions.assert_valid_bearer_token(retrieved_token)
    
    def test_close_session(self, mock_egeria_tech_client):
        """Test closing session."""
        # Create token first
        mock_egeria_tech_client.create_egeria_bearer_token("user", "pass")
        assert mock_egeria_tech_client.get_token() is not None
        
        # Close session
        mock_egeria_tech_client.close_session()
        
        # Verify session was closed on all sub-clients
        for sub_client in mock_egeria_tech_client._subclients:
            assert sub_client.get_token() is None
    
    def test_attribute_delegation(self, mock_egeria_tech_client):
        """Test that attributes are properly delegated to sub-clients."""
        # Test delegation to collection manager
        assert hasattr(mock_egeria_tech_client, "_async_get_digital_products")
        assert hasattr(mock_egeria_tech_client, "_async_get_collections")
        
        # Test delegation to governance officer
        assert hasattr(mock_egeria_tech_client, "_async_get_governance_definitions")
        
        # Test delegation to metadata explorer
        assert hasattr(mock_egeria_tech_client, "_async_get_data_assets")
    
    def test_attribute_error_for_missing_method(self, mock_egeria_tech_client):
        """Test that AttributeError is raised for non-existent methods."""
        with pytest.raises(AttributeError) as exc_info:
            mock_egeria_tech_client.non_existent_method()
        
        assert "MockEgeriaTech" in str(exc_info.value)
        assert "non_existent_method" in str(exc_info.value)


@pytest.mark.unit
class TestEgeriaTechSubClientIntegration:
    """Unit tests for EgeriaTech sub-client integration."""
    
    def test_subclient_token_propagation(self, mock_egeria_tech_client):
        """Test that token operations propagate to all sub-clients."""
        # Create token
        token = mock_egeria_tech_client.create_egeria_bearer_token("user", "pass")
        
        # Verify all sub-clients have the token
        for sub_client in mock_egeria_tech_client._subclients:
            assert sub_client.get_token() == token
        
        # Set new token
        new_token = "new_token_67890"
        mock_egeria_tech_client.set_bearer_token(new_token)
        
        # Verify all sub-clients have the new token
        for sub_client in mock_egeria_tech_client._subclients:
            assert sub_client.get_token() == new_token
        
        # Close session
        mock_egeria_tech_client.close_session()
        
        # Verify all sub-clients have no token
        for sub_client in mock_egeria_tech_client._subclients:
            assert sub_client.get_token() is None
    
    def test_subclient_method_calls(self, mock_egeria_tech_client):
        """Test that method calls are properly delegated to sub-clients."""
        # Test collection manager method
        result = mock_egeria_tech_client._async_get_digital_products()
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
        
        # Test governance officer method
        result = mock_egeria_tech_client._async_get_governance_definitions()
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"
        
        # Test metadata explorer method
        result = mock_egeria_tech_client._async_get_data_assets()
        EgeriaAssertions.assert_valid_format_set_response(result)
        assert result["kind"] == "json"


@pytest.mark.unit
class TestEgeriaTechErrorHandling:
    """Unit tests for EgeriaTech error handling."""
    
    def test_token_creation_with_invalid_credentials(self, mock_egeria_tech_client):
        """Test token creation with invalid credentials."""
        # Mock sub-client to raise exception
        with patch.object(mock_egeria_tech_client._subclients[0], 
                         'create_egeria_bearer_token', 
                         side_effect=Exception("Invalid credentials")):
            with pytest.raises(Exception) as exc_info:
                mock_egeria_tech_client.create_egeria_bearer_token("invalid", "invalid")
            
            assert "Invalid credentials" in str(exc_info.value)
    
    def test_subclient_method_error_propagation(self, mock_egeria_tech_client):
        """Test that errors from sub-clients are properly propagated."""
        # Mock a sub-client method to raise exception
        with patch.object(mock_egeria_tech_client._subclients[0],
                         '_async_get_digital_products',
                         side_effect=Exception("API Error")):
            with pytest.raises(Exception) as exc_info:
                mock_egeria_tech_client._async_get_digital_products()
            
            assert "API Error" in str(exc_info.value)
    
    def test_session_close_with_errors(self, mock_egeria_tech_client):
        """Test session close handles errors gracefully."""
        # Mock sub-client close_session to raise exception
        with patch.object(mock_egeria_tech_client._subclients[0],
                         'close_session',
                         side_effect=Exception("Close error")):
            # Should not raise exception, should handle gracefully
            mock_egeria_tech_client.close_session()
            
            # Verify other sub-clients were still closed
            for i, sub_client in enumerate(mock_egeria_tech_client._subclients):
                if i != 0:  # Skip the one that raised exception
                    assert sub_client.get_token() is None


@pytest.mark.unit
class TestEgeriaTechParameterValidation:
    """Unit tests for EgeriaTech parameter validation."""
    
    def test_initialization_with_minimal_params(self):
        """Test initialization with minimal required parameters."""
        client = EgeriaTech(
            view_server="test-server",
            platform_url="https://test.com",
            user_id="test_user"
        )
        
        assert client.view_server == "test-server"
        assert client.platform_url == "https://test.com"
        assert client.user_id == "test_user"
        assert client.user_pwd is None
    
    def test_initialization_with_token(self):
        """Test initialization with pre-existing token."""
        client = EgeriaTech(
            view_server="test-server",
            platform_url="https://test.com",
            user_id="test_user",
            user_pwd="test_pass",
            token="existing_token"
        )
        
        assert client.view_server == "test-server"
        assert client.platform_url == "https://test.com"
        assert client.user_id == "test_user"
        assert client.user_pwd == "test_pass"
    
    def test_token_operations_with_empty_strings(self, mock_egeria_tech_client):
        """Test token operations with empty string parameters."""
        # Empty user_id and user_pwd should still work
        token = mock_egeria_tech_client.create_egeria_bearer_token("", "")
        EgeriaAssertions.assert_valid_bearer_token(token)
        
        # Empty token should be set
        mock_egeria_tech_client.set_bearer_token("")
        assert mock_egeria_tech_client.get_token() == ""


@pytest.mark.unit
class TestEgeriaTechComposition:
    """Unit tests for EgeriaTech composition pattern."""
    
    def test_subclient_composition(self, mock_egeria_tech_client):
        """Test that all expected sub-clients are composed."""
        expected_subclients = [
            "_collection_manager",
            "_governance_officer", 
            "_metadata_explorer"
        ]
        
        for subclient_name in expected_subclients:
            assert hasattr(mock_egeria_tech_client, subclient_name)
            subclient = getattr(mock_egeria_tech_client, subclient_name)
            assert subclient is not None
    
    def test_subclient_independence(self, mock_egeria_tech_client):
        """Test that sub-clients operate independently."""
        # Set different tokens on different sub-clients
        mock_egeria_tech_client._collection_manager.set_bearer_token("token1")
        mock_egeria_tech_client._governance_officer.set_bearer_token("token2")
        mock_egeria_tech_client._metadata_explorer.set_bearer_token("token3")
        
        # Verify they maintain different tokens
        assert mock_egeria_tech_client._collection_manager.get_token() == "token1"
        assert mock_egeria_tech_client._governance_officer.get_token() == "token2"
        assert mock_egeria_tech_client._metadata_explorer.get_token() == "token3"
    
    def test_subclient_method_resolution_order(self, mock_egeria_tech_client):
        """Test that method resolution follows expected order."""
        # Test that methods are resolved from the first sub-client that has them
        result = mock_egeria_tech_client._async_get_digital_products()
        assert result is not None
        
        # Test that AttributeError is raised if no sub-client has the method
        with pytest.raises(AttributeError):
            mock_egeria_tech_client.non_existent_method()


@pytest.mark.unit
class TestEgeriaTechMockIntegration:
    """Unit tests for EgeriaTech with mock responses."""
    
    def test_mock_response_integration(self, mock_egeria_tech_client):
        """Test integration with mock response factory."""
        # Test digital products response
        result = mock_egeria_tech_client._async_get_digital_products()
        EgeriaAssertions.assert_valid_format_set_response(result)
        EgeriaAssertions.assert_response_contains_expected_fields(
            result, ["guid", "display_name", "qualified_name"]
        )
        
        # Test collections response
        result = mock_egeria_tech_client._async_get_collections()
        EgeriaAssertions.assert_valid_format_set_response(result)
        EgeriaAssertions.assert_response_contains_expected_fields(
            result, ["guid", "display_name", "qualified_name"]
        )
    
    def test_mock_response_data_types(self, mock_egeria_tech_client):
        """Test that mock responses have correct data types."""
        result = mock_egeria_tech_client._async_get_digital_products()
        
        EgeriaAssertions.assert_response_data_type(result, list)
        EgeriaAssertions.assert_response_not_empty(result)
        EgeriaAssertions.assert_response_has_guid(result)
        EgeriaAssertions.assert_response_has_display_name(result)
    
    def test_mock_response_consistency(self, mock_egeria_tech_client):
        """Test that mock responses are consistent across calls."""
        result1 = mock_egeria_tech_client._async_get_digital_products()
        result2 = mock_egeria_tech_client._async_get_digital_products()
        
        # Results should be consistent (same structure)
        assert result1["kind"] == result2["kind"]
        assert len(result1["data"]) == len(result2["data"])
        
        # Data should have same structure
        if len(result1["data"]) > 0:
            item1 = result1["data"][0]
            item2 = result2["data"][0]
            assert set(item1.keys()) == set(item2.keys())


