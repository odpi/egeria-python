"""
Unit tests for pyegeria core modules.

These tests cover the foundational modules that don't have complex dependencies.
"""

import pytest
import json
from unittest.mock import Mock, patch
from httpx import Response

from pyegeria._globals import (
    is_debug, disable_ssl_warnings, enable_ssl_check, max_paging_size, 
    default_time_out, DEBUG_LEVEL, comment_types, star_ratings,
    TEMPLATE_GUIDS, INTEGRATION_GUIDS, NO_ELEMENTS_FOUND, NO_ASSETS_FOUND,
    NO_SERVERS_FOUND, NO_CATALOGS_FOUND, NO_GLOSSARIES_FOUND, NO_TERMS_FOUND,
    NO_CATEGORIES_FOUND, NO_ELEMENT_FOUND, NO_PROJECTS_FOUND, NO_COLLECTION_FOUND,
    NO_GUID_RETURNED, NO_MEMBERS_FOUND
)

from pyegeria._exceptions_new import (
    PyegeriaErrorCode, PyegeriaException, PyegeriaConnectionException,
    PyegeriaInvalidParameterException, PyegeriaClientException, PyegeriaAPIException,
    PyegeriaUnauthorizedException, PyegeriaNotFoundException, PyegeriaUnknownException,
    print_bullet_list_colored, print_bullet_list, flatten_dict_to_string,
    format_dict_to_string, print_exception_response, print_exception_table,
    print_basic_exception, print_validation_error
)

from pyegeria._validators import (
    validate_user_id, validate_server_name, validate_guid, validate_name,
    validate_search_string, validate_public, validate_url, is_json
)


@pytest.mark.unit
class TestGlobalsModule:
    """Unit tests for _globals module."""
    
    def test_global_constants(self):
        """Test that global constants are properly defined."""
        # Test boolean flags
        assert isinstance(is_debug, bool)
        assert isinstance(disable_ssl_warnings, bool)
        assert isinstance(enable_ssl_check, bool)
        
        # Test numeric constants
        assert isinstance(max_paging_size, int)
        assert max_paging_size == 500
        assert isinstance(default_time_out, int)
        assert default_time_out == 30
        
        # Test string constants
        assert isinstance(DEBUG_LEVEL, str)
        assert DEBUG_LEVEL == "quiet"
    
    def test_comment_types_tuple(self):
        """Test comment types tuple."""
        assert isinstance(comment_types, tuple)
        assert len(comment_types) == 6
        assert "ANSWER" in comment_types
        assert "OTHER" in comment_types
        assert "QUESTION" in comment_types
        assert "STANDARD_COMMENT" in comment_types
        assert "SUGGESTION" in comment_types
        assert "USAGE_EXPERIENCE" in comment_types
    
    def test_star_ratings_tuple(self):
        """Test star ratings tuple."""
        assert isinstance(star_ratings, tuple)
        assert len(star_ratings) == 6
        assert "FIVE_STARS" in star_ratings
        assert "FOUR_STARS" in star_ratings
        assert "NO_RECOMMENDATION" in star_ratings
        assert "ONE_STAR" in star_ratings
        assert "THREE_STARS" in star_ratings
        assert "TWO_STARS" in star_ratings
    
    def test_template_guids_dict(self):
        """Test template GUIDs dictionary."""
        assert isinstance(TEMPLATE_GUIDS, dict)
        assert len(TEMPLATE_GUIDS) > 0
        
        # Test specific template GUIDs
        assert "File System Directory" in TEMPLATE_GUIDS
        assert "CSV Data File" in TEMPLATE_GUIDS
        assert "Data File" in TEMPLATE_GUIDS
        assert "PostgreSQL Relational Database" in TEMPLATE_GUIDS
        
        # Test GUID format (should be UUID-like)
        for name, guid in TEMPLATE_GUIDS.items():
            assert isinstance(guid, str)
            assert len(guid) == 36  # UUID format
            assert guid.count('-') == 4  # UUID format
    
    def test_integration_guids_dict(self):
        """Test integration GUIDs dictionary."""
        assert isinstance(INTEGRATION_GUIDS, dict)
        assert len(INTEGRATION_GUIDS) > 0
        
        # Test specific integration GUIDs
        assert "GeneralFilesMonitor" in INTEGRATION_GUIDS
        assert "OpenLineageFilePublisher" in INTEGRATION_GUIDS
        assert "JDBC" in INTEGRATION_GUIDS
        assert "PostgreSQLDatabase" in INTEGRATION_GUIDS
        
        # Test GUID format (should be UUID-like)
        for name, guid in INTEGRATION_GUIDS.items():
            assert isinstance(guid, str)
            assert len(guid) == 36  # UUID format
            assert guid.count('-') == 4  # UUID format
    
    def test_no_elements_constants(self):
        """Test NO_ELEMENTS_FOUND and related constants."""
        assert isinstance(NO_ELEMENTS_FOUND, str)
        assert NO_ELEMENTS_FOUND == "No elements found"
        
        assert isinstance(NO_ASSETS_FOUND, str)
        assert NO_ASSETS_FOUND == "No assets found"
        
        assert isinstance(NO_SERVERS_FOUND, str)
        assert NO_SERVERS_FOUND == "No servers found"
        
        assert isinstance(NO_CATALOGS_FOUND, str)
        assert NO_CATALOGS_FOUND == "No catalogs found"
        
        assert isinstance(NO_GLOSSARIES_FOUND, str)
        assert NO_GLOSSARIES_FOUND == "No glossaries found"
        
        assert isinstance(NO_TERMS_FOUND, str)
        assert NO_TERMS_FOUND == "No terms found"
        
        assert isinstance(NO_CATEGORIES_FOUND, str)
        assert NO_CATEGORIES_FOUND == "No categories found"
        
        assert isinstance(NO_ELEMENT_FOUND, str)
        assert NO_ELEMENT_FOUND == "No element found"
        
        assert isinstance(NO_PROJECTS_FOUND, str)
        assert NO_PROJECTS_FOUND == "No projects found"
        
        assert isinstance(NO_COLLECTION_FOUND, str)
        assert NO_COLLECTION_FOUND == "No collection found"
        
        assert isinstance(NO_GUID_RETURNED, str)
        assert NO_GUID_RETURNED == "No guid returned"
        
        assert isinstance(NO_MEMBERS_FOUND, str)
        assert NO_MEMBERS_FOUND == "No members found"


@pytest.mark.unit
class TestExceptionsModule:
    """Unit tests for _exceptions_new module."""
    
    def test_pyegeria_error_code_enum(self):
        """Test PyegeriaErrorCode enum."""
        # Test that all error codes are defined
        assert hasattr(PyegeriaErrorCode, 'CLIENT_ERROR')
        assert hasattr(PyegeriaErrorCode, 'VALIDATION_ERROR')
        assert hasattr(PyegeriaErrorCode, 'AUTHORIZATION_ERROR')
        assert hasattr(PyegeriaErrorCode, 'AUTHENTICATION_ERROR')
        assert hasattr(PyegeriaErrorCode, 'CONNECTION_ERROR')
        assert hasattr(PyegeriaErrorCode, 'EGERIA_ERROR')
        
        # Test error code structure
        client_error = PyegeriaErrorCode.CLIENT_ERROR
        assert isinstance(client_error.value, dict)
        assert 'http_code' in client_error.value
        assert 'message_id' in client_error.value
        assert 'message_template' in client_error.value
        assert 'system_action' in client_error.value
        assert 'user_action' in client_error.value
    
    def test_pyegeria_error_code_str(self):
        """Test PyegeriaErrorCode string representation."""
        error_code = PyegeriaErrorCode.CLIENT_ERROR
        error_str = str(error_code)
        
        assert isinstance(error_str, str)
        assert "http_code=" in error_str
        assert "messageId=" in error_str
        assert "message=" in error_str
        assert "systemAction=" in error_str
        assert "userAction=" in error_str
    
    def test_pyegeria_exception_creation(self):
        """Test PyegeriaException creation."""
        mock_response = Mock(spec=Response)
        mock_response.url = "https://test.com/api"
        mock_response.status_code = 400
        
        context = {"caller_method": "test_method"}
        additional_info = {"reason": "test reason"}
        
        exception = PyegeriaException(
            response=mock_response,
            error_code=PyegeriaErrorCode.CLIENT_ERROR,
            context=context,
            additional_info=additional_info
        )
        
        assert exception.response == mock_response
        assert exception.response_url == "https://test.com/api"
        assert exception.response_code == 400
        assert exception.error_code == PyegeriaErrorCode.CLIENT_ERROR
        assert exception.context == context
        assert exception.additional_info == additional_info
        assert exception.pyegeria_code == "CLIENT_ERROR_400"
    
    def test_pyegeria_exception_without_response(self):
        """Test PyegeriaException creation without response."""
        exception = PyegeriaException(
            error_code=PyegeriaErrorCode.VALIDATION_ERROR,
            context={"caller_method": "test_method"},
            additional_info={"reason": "test reason"}
        )
        
        assert exception.response is None
        assert exception.response_url == ""
        assert exception.response_code == ""
        assert exception.error_code == PyegeriaErrorCode.VALIDATION_ERROR
    
    def test_pyegeria_exception_str(self):
        """Test PyegeriaException string representation."""
        mock_response = Mock(spec=Response)
        mock_response.url = "https://test.com/api"
        mock_response.status_code = 400
        
        context = {"caller_method": "test_method", "param1": "value1"}
        additional_info = {"reason": "test reason"}
        
        exception = PyegeriaException(
            response=mock_response,
            error_code=PyegeriaErrorCode.CLIENT_ERROR,
            context=context,
            additional_info=additional_info
        )
        
        exception_str = str(exception)
        assert isinstance(exception_str, str)
        assert "CLIENT_ERROR_400" in exception_str
        assert "https://test.com/api" in exception_str
        assert "test_method" in exception_str
    
    def test_specific_exception_types(self):
        """Test specific exception types."""
        # Test PyegeriaConnectionException
        conn_exception = PyegeriaConnectionException(
            context={"caller_method": "test_connection"},
            additional_info={"url": "https://test.com"}
        )
        assert isinstance(conn_exception, PyegeriaException)
        assert conn_exception.error_code == PyegeriaErrorCode.CONNECTION_ERROR
        
        # Test PyegeriaInvalidParameterException
        param_exception = PyegeriaInvalidParameterException(
            context={"caller_method": "test_param"},
            additional_info={"reason": "invalid param"}
        )
        assert isinstance(param_exception, PyegeriaException)
        assert param_exception.error_code == PyegeriaErrorCode.VALIDATION_ERROR
        
        # Test PyegeriaClientException
        mock_response = Mock(spec=Response)
        mock_response.url = "https://test.com/api"
        mock_response.status_code = 400
        
        client_exception = PyegeriaClientException(
            response=mock_response,
            context={"caller_method": "test_client"},
            additional_info={"reason": "client error"}
        )
        assert isinstance(client_exception, PyegeriaException)
        assert client_exception.error_code == PyegeriaErrorCode.CLIENT_ERROR
        
        # Test PyegeriaAPIException
        api_exception = PyegeriaAPIException(
            response=mock_response,
            context={"caller_method": "test_api"},
            additional_info={"reason": "api error"}
        )
        assert isinstance(api_exception, PyegeriaException)
        assert api_exception.error_code == PyegeriaErrorCode.EGERIA_ERROR
        
        # Test PyegeriaUnauthorizedException
        auth_exception = PyegeriaUnauthorizedException(
            response=mock_response,
            context={"caller_method": "test_auth"},
            additional_info={"userid": "test_user"}
        )
        assert isinstance(auth_exception, PyegeriaException)
        assert auth_exception.error_code == PyegeriaErrorCode.AUTHORIZATION_ERROR
        
        # Test PyegeriaNotFoundException
        not_found_exception = PyegeriaNotFoundException(
            response=mock_response,
            context={"caller_method": "test_not_found"},
            additional_info={"reason": "not found"}
        )
        assert isinstance(not_found_exception, PyegeriaException)
        assert not_found_exception.error_code == PyegeriaErrorCode.CLIENT_ERROR
        
        # Test PyegeriaUnknownException
        unknown_exception = PyegeriaUnknownException(
            response=mock_response,
            context={"caller_method": "test_unknown"},
            additional_info={"reason": "unknown error"}
        )
        assert isinstance(unknown_exception, PyegeriaException)
        assert unknown_exception.error_code == PyegeriaErrorCode.CLIENT_ERROR
    
    def test_utility_functions(self):
        """Test utility functions in exceptions module."""
        # Test print_bullet_list_colored
        items = ["item1", "item2", "item3"]
        colors = ["red", "green", "blue"]
        result = print_bullet_list_colored(items, colors)
        assert result is not None
        
        # Test print_bullet_list
        items_dict = [("key1", "value1"), ("key2", "value2")]
        result = print_bullet_list(items_dict)
        assert result is not None
        
        # Test flatten_dict_to_string
        test_dict = {"key1": "value1", "key2": "value2"}
        result = flatten_dict_to_string(test_dict)
        assert isinstance(result, str)
        assert "key1" in result
        assert "value1" in result
        
        # Test flatten_dict_to_string with empty dict
        result = flatten_dict_to_string({})
        assert result == ""
        
        # Test flatten_dict_to_string with None
        result = flatten_dict_to_string(None)
        assert result == ""
        
        # Test format_dict_to_string
        test_dict = {"key1": "value1", "key2": "value2"}
        result = format_dict_to_string(test_dict)
        assert isinstance(result, str)
        assert "value1" in result
        assert "value2" in result
        
        # Test format_dict_to_string with non-dict
        result = format_dict_to_string("not a dict")
        assert result == "not a dict"


@pytest.mark.unit
class TestValidatorsModule:
    """Unit tests for _validators module."""
    
    def test_validate_user_id_valid(self):
        """Test validate_user_id with valid input."""
        result = validate_user_id("test_user")
        assert result is True
    
    def test_validate_user_id_none(self):
        """Test validate_user_id with None input."""
        with pytest.raises(PyegeriaInvalidParameterException) as exc_info:
            validate_user_id(None)
        
        assert "Invalid user name - its empty" in str(exc_info.value)
    
    def test_validate_user_id_empty(self):
        """Test validate_user_id with empty string."""
        with pytest.raises(PyegeriaInvalidParameterException) as exc_info:
            validate_user_id("")
        
        assert "Invalid user name - its empty" in str(exc_info.value)
    
    def test_validate_server_name_valid(self):
        """Test validate_server_name with valid input."""
        result = validate_server_name("test_server")
        assert result is True
    
    def test_validate_server_name_none(self):
        """Test validate_server_name with None input."""
        with pytest.raises(PyegeriaInvalidParameterException) as exc_info:
            validate_server_name(None)
        
        assert "Invalid server name - its empty" in str(exc_info.value)
    
    def test_validate_server_name_empty(self):
        """Test validate_server_name with empty string."""
        with pytest.raises(PyegeriaInvalidParameterException) as exc_info:
            validate_server_name("")
        
        assert "Invalid server name - its empty" in str(exc_info.value)
    
    def test_validate_guid_valid(self):
        """Test validate_guid with valid input."""
        result = validate_guid("123e4567-e89b-12d3-a456-426614174000")
        assert result is True
    
    def test_validate_guid_none(self):
        """Test validate_guid with None input."""
        with pytest.raises(PyegeriaInvalidParameterException) as exc_info:
            validate_guid(None)
        
        assert "Invalid GUID" in str(exc_info.value)
    
    def test_validate_guid_empty(self):
        """Test validate_guid with empty string."""
        with pytest.raises(PyegeriaInvalidParameterException) as exc_info:
            validate_guid("")
        
        assert "Invalid GUID" in str(exc_info.value)
    
    def test_validate_guid_non_string(self):
        """Test validate_guid with non-string input."""
        with pytest.raises(PyegeriaInvalidParameterException) as exc_info:
            validate_guid(123)
        
        assert "Invalid GUID" in str(exc_info.value)
    
    def test_validate_name_valid(self):
        """Test validate_name with valid input."""
        result = validate_name("test_name")
        assert result is True
    
    def test_validate_name_none(self):
        """Test validate_name with None input."""
        with pytest.raises(PyegeriaInvalidParameterException) as exc_info:
            validate_name(None)
        
        assert "Invalid `name`" in str(exc_info.value)
    
    def test_validate_name_empty(self):
        """Test validate_name with empty string."""
        with pytest.raises(PyegeriaInvalidParameterException) as exc_info:
            validate_name("")
        
        assert "Invalid `name`" in str(exc_info.value)
    
    def test_validate_search_string_valid(self):
        """Test validate_search_string with valid input."""
        result = validate_search_string("test search")
        assert result is True
    
    def test_validate_search_string_none(self):
        """Test validate_search_string with None input."""
        with pytest.raises(PyegeriaInvalidParameterException) as exc_info:
            validate_search_string(None)
        
        assert "Invalid `name`" in str(exc_info.value)
    
    def test_validate_search_string_empty(self):
        """Test validate_search_string with empty string."""
        with pytest.raises(PyegeriaInvalidParameterException) as exc_info:
            validate_search_string("")
        
        assert "Invalid `name`" in str(exc_info.value)
    
    def test_validate_public_valid(self):
        """Test validate_public with valid input."""
        result = validate_public(True)
        assert result is True
        
        result = validate_public(False)
        assert result is True
    
    def test_validate_public_none(self):
        """Test validate_public with None input."""
        with pytest.raises(PyegeriaInvalidParameterException) as exc_info:
            validate_public(None)
        
        assert "Invalid `name`" in str(exc_info.value)
    
    def test_validate_url_valid(self):
        """Test validate_url with valid input."""
        result = validate_url("https://example.com")
        assert result is True
        
        result = validate_url("http://localhost:8080")
        assert result is True
    
    def test_validate_url_none(self):
        """Test validate_url with None input."""
        with pytest.raises(PyegeriaInvalidParameterException) as exc_info:
            validate_url(None)
        
        assert "The provided URL is invalid - it is empty" in str(exc_info.value)
    
    def test_validate_url_empty(self):
        """Test validate_url with empty string."""
        with pytest.raises(PyegeriaInvalidParameterException) as exc_info:
            validate_url("")
        
        assert "The provided URL is invalid - it is empty" in str(exc_info.value)
    
    def test_validate_url_invalid(self):
        """Test validate_url with invalid URL."""
        with pytest.raises(PyegeriaInvalidParameterException) as exc_info:
            validate_url("not-a-url")
        
        assert "The provided URL is invalid" in str(exc_info.value)
    
    def test_validate_url_localhost_hack(self):
        """Test validate_url localhost to 127.0.0.1 conversion."""
        # This should work due to the localhost hack
        result = validate_url("http://localhost:8080")
        assert result is True
    
    def test_is_json_valid(self):
        """Test is_json with valid JSON."""
        result = is_json('{"key": "value"}')
        assert result is True
        
        result = is_json('[1, 2, 3]')
        assert result is True
        
        result = is_json('"string"')
        assert result is True
    
    def test_is_json_invalid(self):
        """Test is_json with invalid JSON."""
        result = is_json('{"key": "value"')  # Missing closing brace
        assert result is False
        
        result = is_json('not json')
        assert result is False
        
        result = is_json('')
        assert result is False
    
    def test_is_json_none(self):
        """Test is_json with None input."""
        result = is_json(None)
        assert result is False
