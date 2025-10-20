"""
Unit tests for pyegeria configuration module.

These tests cover configuration loading and management.
"""

import pytest
import os
import json
import tempfile
from unittest.mock import Mock, patch, mock_open

from pyegeria.config import (
    PyegeriaSettings, EnvironmentConfig, UserProfileConfig, 
    load_app_config, get_app_config, settings
)


@pytest.mark.unit
class TestConfigModule:
    """Unit tests for config module."""
    
    def test_pyegeria_settings_defaults(self):
        """Test PyegeriaSettings default values."""
        settings = PyegeriaSettings()
        
        assert settings.pyegeria_root_path == ""
        assert settings.pyegeria_config_directory == ""
        assert settings.pyegeria_config_file == "config.json"
        assert settings.pyegeria_console_width == 200
        assert settings.pyegeria_user_format_sets_dir == "~/.pyegeria/format_sets"
        assert settings.egeria_user_name == ""
        assert settings.egeria_user_password == ""
    
    def test_pyegeria_settings_with_env_file(self):
        """Test PyegeriaSettings with custom env file."""
        # Create a temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("PYEGERIA_ROOT_PATH=/test/path\n")
            f.write("PYEGERIA_CONFIG_FILE=test_config.json\n")
            f.write("EGERIA_USER_NAME=test_user\n")
            f.write("EGERIA_USER_PASSWORD=test_pass\n")
            env_file_path = f.name
        
        try:
            custom_settings = PyegeriaSettings.with_env_file(env_file_path)
            
            assert custom_settings.pyegeria_root_path == "/test/path"
            assert custom_settings.pyegeria_config_file == "test_config.json"
            assert custom_settings.egeria_user_name == "test_user"
            assert custom_settings.egeria_user_password == "test_pass"
        finally:
            os.unlink(env_file_path)
    
    def test_environment_config_defaults(self):
        """Test EnvironmentConfig default values."""
        env_config = EnvironmentConfig()
        
        assert env_config.egeria_view_server == "qs-view-server"
        assert env_config.egeria_view_server_url == "https://localhost:9443"
        assert env_config.egeria_local_qualifier == "qs"
        assert env_config.egeria_server_timeout == 30
        assert env_config.egeria_max_paging_size == 500
        assert env_config.egeria_enable_ssl_check is False
        assert env_config.egeria_disable_ssl_warnings is True
        assert env_config.egeria_debug_level == "quiet"
    
    def test_user_profile_config_defaults(self):
        """Test UserProfileConfig default values."""
        user_config = UserProfileConfig()
        
        assert user_config.user_name == ""
        assert user_config.user_pwd == ""
        assert user_config.egeria_local_qualifier == "qs"
    
    def test_environment_config_validation(self):
        """Test EnvironmentConfig validation."""
        # Test valid configuration
        valid_config = EnvironmentConfig(
            egeria_view_server="test-server",
            egeria_view_server_url="https://test.com:9443",
            egeria_server_timeout=60,
            egeria_max_paging_size=1000
        )
        
        assert valid_config.egeria_view_server == "test-server"
        assert valid_config.egeria_view_server_url == "https://test.com:9443"
        assert valid_config.egeria_server_timeout == 60
        assert valid_config.egeria_max_paging_size == 1000
    
    def test_user_profile_config_validation(self):
        """Test UserProfileConfig validation."""
        # Test valid configuration
        valid_config = UserProfileConfig(
            user_name="test_user",
            user_pwd="test_password",
            egeria_local_qualifier="test"
        )
        
        assert valid_config.user_name == "test_user"
        assert valid_config.user_pwd == "test_password"
        assert valid_config.egeria_local_qualifier == "test"
    
    @patch('pyegeria.config.os.path.exists')
    @patch('pyegeria.config.json.load')
    def test_load_app_config_with_file(self, mock_json_load, mock_exists):
        """Test load_app_config with configuration file."""
        # Mock file existence
        mock_exists.return_value = True
        
        # Mock JSON content
        mock_config = {
            "Environment": {
                "egeria_view_server": "test-server",
                "egeria_view_server_url": "https://test.com:9443"
            },
            "User_Profile": {
                "user_name": "test_user",
                "user_pwd": "test_password"
            }
        }
        mock_json_load.return_value = mock_config
        
        # Mock file opening
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_config))):
            config = load_app_config()
        
        assert config is not None
        assert hasattr(config, 'Environment')
        assert hasattr(config, 'User_Profile')
    
    @patch('pyegeria.config.os.path.exists')
    def test_load_app_config_without_file(self, mock_exists):
        """Test load_app_config without configuration file."""
        # Mock file not existing
        mock_exists.return_value = False
        
        config = load_app_config()
        
        assert config is not None
        assert hasattr(config, 'Environment')
        assert hasattr(config, 'User_Profile')
    
    def test_get_app_config(self):
        """Test get_app_config function."""
        config = get_app_config()
        
        assert config is not None
        assert hasattr(config, 'Environment')
        assert hasattr(config, 'User_Profile')
    
    def test_settings_global_instance(self):
        """Test global settings instance."""
        # Test that settings is available and has expected attributes
        assert settings is not None
        assert hasattr(settings, 'Environment')
        assert hasattr(settings, 'User_Profile')
        
        # Test that we can access configuration values
        assert hasattr(settings.Environment, 'egeria_view_server')
        assert hasattr(settings.Environment, 'egeria_view_server_url')
        assert hasattr(settings.User_Profile, 'user_name')
        assert hasattr(settings.User_Profile, 'user_pwd')
    
    def test_config_model_structure(self):
        """Test configuration model structure."""
        config = get_app_config()
        
        # Test Environment section
        env = config.Environment
        assert isinstance(env.egeria_view_server, str)
        assert isinstance(env.egeria_view_server_url, str)
        assert isinstance(env.egeria_local_qualifier, str)
        assert isinstance(env.egeria_server_timeout, int)
        assert isinstance(env.egeria_max_paging_size, int)
        assert isinstance(env.egeria_enable_ssl_check, bool)
        assert isinstance(env.egeria_disable_ssl_warnings, bool)
        assert isinstance(env.egeria_debug_level, str)
        
        # Test User_Profile section
        user = config.User_Profile
        assert isinstance(user.user_name, str)
        assert isinstance(user.user_pwd, str)
        assert isinstance(user.egeria_local_qualifier, str)
    
    def test_config_immutability(self):
        """Test that configuration values are properly typed."""
        config = get_app_config()
        
        # Test that boolean values are actually booleans
        assert isinstance(config.Environment.egeria_enable_ssl_check, bool)
        assert isinstance(config.Environment.egeria_disable_ssl_warnings, bool)
        
        # Test that numeric values are actually numbers
        assert isinstance(config.Environment.egeria_server_timeout, int)
        assert isinstance(config.Environment.egeria_max_paging_size, int)
        
        # Test that string values are actually strings
        assert isinstance(config.Environment.egeria_view_server, str)
        assert isinstance(config.Environment.egeria_view_server_url, str)
        assert isinstance(config.User_Profile.user_name, str)
        assert isinstance(config.User_Profile.user_pwd, str)
    
    @patch.dict(os.environ, {
        'PYEGERIA_ROOT_PATH': '/test/path',
        'PYEGERIA_CONFIG_FILE': 'test_config.json',
        'EGERIA_USER_NAME': 'env_user',
        'EGERIA_USER_PASSWORD': 'env_pass'
    })
    def test_environment_variable_override(self):
        """Test that environment variables can override configuration."""
        # This test verifies that environment variables are properly loaded
        # The exact behavior depends on the configuration loading order
        settings = PyegeriaSettings()
        
        # These should be loaded from environment variables
        assert settings.pyegeria_root_path == "/test/path"
        assert settings.pyegeria_config_file == "test_config.json"
        assert settings.egeria_user_name == "env_user"
        assert settings.egeria_user_password == "env_pass"
    
    def test_config_file_path_construction(self):
        """Test configuration file path construction."""
        settings = PyegeriaSettings()
        
        # Test default path construction
        assert settings.pyegeria_config_file == "config.json"
        
        # Test with custom values
        settings.pyegeria_root_path = "/custom/path"
        settings.pyegeria_config_file = "custom_config.json"
        
        # The path construction logic would be tested here
        # This depends on the actual implementation in the config module
