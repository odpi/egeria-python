#!/usr/bin/env python3
"""
Test script to verify loading environment variables from the .env file using pydantic-settings.
"""
import os
import tempfile
import shutil
from pathlib import Path
from pyegeria.load_config import load_app_config, PyegeriaSettings

def reset_config():
    """Reset the loaded configuration to force reloading."""
    import pyegeria.load_config
    pyegeria.load_config._app_config = None

def test_env_settings():
    """Test that environment variables are correctly loaded and used in the configuration."""
    print("\nTesting loading and using environment variables...")
    
    # Save the original environment variables
    original_env = {}
    for var in ["PYEGERIA_ROOT_PATH", "PYEGERIA_CONFIG_FILE", "PYEGERIA_CONSOLE_WIDTH", "EGERIA_USER_NAME", "EGERIA_USER_PASSWORD"]:
        if var in os.environ:
            original_env[var] = os.environ[var]
    
    try:
        # Set environment variables directly
        os.environ["PYEGERIA_ROOT_PATH"] = "/test/env/path"
        os.environ["PYEGERIA_CONFIG_FILE"] = "test_config.json"
        os.environ["PYEGERIA_CONSOLE_WIDTH"] = "300"
        os.environ["EGERIA_USER_NAME"] = "test_user"
        os.environ["EGERIA_USER_PASSWORD"] = "test_password"
        
        # Create a temporary directory for the config file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temporary config file
            config_file = Path(temp_dir) / "test_config.json"
            with open(config_file, 'w') as f:
                f.write('{"Environment": {}, "Debug": {}, "Logging": {}, "User Profile": {}}')
            
            # Save the original working directory
            original_dir = os.getcwd()
            
            try:
                # Change to the temporary directory
                os.chdir(temp_dir)
                
                # Reset the loaded configuration
                reset_config()
                
                # Create a PyegeriaSettings instance
                settings = PyegeriaSettings()
                
                # Check that the settings were loaded correctly from environment variables
                print(f"Root path from env: {settings.pyegeria_root_path}")
                print(f"Config file from env: {settings.pyegeria_config_file}")
                print(f"Console width from env: {settings.pyegeria_console_width}")
                print(f"User name from env: {settings.egeria_user_name}")
                print(f"User password from env: {settings.egeria_user_password}")
                
                assert settings.pyegeria_root_path == "/test/env/path", f"Expected '/test/env/path', got '{settings.pyegeria_root_path}'"
                assert settings.pyegeria_config_file == "test_config.json", f"Expected 'test_config.json', got '{settings.pyegeria_config_file}'"
                assert settings.pyegeria_console_width == 300, f"Expected 300, got '{settings.pyegeria_console_width}'"
                assert settings.egeria_user_name == "test_user", f"Expected 'test_user', got '{settings.egeria_user_name}'"
                assert settings.egeria_user_password == "test_password", f"Expected 'test_password', got '{settings.egeria_user_password}'"
                
                # Now test that load_app_config() uses these settings
                config = load_app_config()
                
                # Check that the configuration was loaded correctly
                print(f"Root path in config: {config.Environment.pyegeria_root}")
                print(f"Console width in config: {config.Environment.console_width}")
                print(f"User name in config: {config.User_Profile.user_name}")
                print(f"User password in config: {config.User_Profile.user_pwd}")
                
                assert config.Environment.pyegeria_root == "/test/env/path", f"Expected '/test/env/path', got '{config.Environment.pyegeria_root}'"
                assert config.Environment.console_width == 300, f"Expected 300, got '{config.Environment.console_width}'"
                assert config.User_Profile.user_name == "test_user", f"Expected 'test_user', got '{config.User_Profile.user_name}'"
                assert config.User_Profile.user_pwd == "test_password", f"Expected 'test_password', got '{config.User_Profile.user_pwd}'"
                
            finally:
                # Change back to the original directory
                os.chdir(original_dir)
        
    finally:
        # Restore the original environment variables
        for var in ["PYEGERIA_ROOT_PATH", "PYEGERIA_CONFIG_FILE", "PYEGERIA_CONSOLE_WIDTH", "EGERIA_USER_NAME", "EGERIA_USER_PASSWORD"]:
            if var in original_env:
                os.environ[var] = original_env[var]
            elif var in os.environ:
                del os.environ[var]
    
    print("Loading and using environment variables test passed!")


if __name__ == "__main__":
    test_env_settings()
    print("\nAll environment settings tests passed!")