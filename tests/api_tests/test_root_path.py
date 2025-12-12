#!/usr/bin/env python3
"""
Test script to verify the root path setting in load_config.py.
"""
import os
import json
import tempfile
from pyegeria.load_config import load_app_config, get_app_config

def reset_config():
    """Reset the loaded configuration to force reloading."""
    import pyegeria.load_config
    pyegeria.load_config._app_config = None

def test_root_path_from_env():
    """Test that the root path is set correctly from the environment variable."""
    print("\nTesting root path from environment variable...")
    
    # Set the environment variable
    os.environ["PYEGERIA_ROOT_PATH"] = "/test/env/path"
    
    # Reset the loaded configuration
    reset_config()
    
    # Load the configuration
    config = load_app_config()
    
    # Check that the root path is set correctly
    root_path = config.Environment.pyegeria_root
    print(f"Root path from env: {root_path}")
    assert root_path == "/test/env/path", f"Expected '/test/env/path', got '{root_path}'"
    
    # Clean up
    del os.environ["PYEGERIA_ROOT_PATH"]
    
    print("Root path from environment variable test passed!")

def test_root_path_from_config():
    """Test that the root path is set correctly from the config file."""
    print("\nTesting root path from config file...")
    
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        config_data = {
            "Environment": {
                "Pyegeria Root": "/test/config/path"
            }
        }
        json.dump(config_data, temp_file)
        temp_file_path = temp_file.name
    
    # Set the environment variable to point to the temp file
    os.environ["PYEGERIA_CONFIG_FILE"] = temp_file_path
    
    # Reset the loaded configuration
    reset_config()
    
    # Load the configuration
    config = load_app_config()
    
    # Check that the root path is set correctly
    root_path = config.Environment.pyegeria_root
    print(f"Root path from config: {root_path}")
    assert root_path == "/test/config/path", f"Expected '/test/config/path', got '{root_path}'"
    
    # Clean up
    del os.environ["PYEGERIA_CONFIG_FILE"]
    os.unlink(temp_file_path)
    
    print("Root path from config file test passed!")

def test_root_path_precedence():
    """Test that the environment variable takes precedence over the config file."""
    print("\nTesting root path precedence...")
    
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        config_data = {
            "Environment": {
                "Pyegeria Root": "/test/config/path"
            }
        }
        json.dump(config_data, temp_file)
        temp_file_path = temp_file.name
    
    # Set the environment variables
    os.environ["PYEGERIA_CONFIG_FILE"] = temp_file_path
    os.environ["PYEGERIA_ROOT_PATH"] = "/test/env/path"
    
    # Reset the loaded configuration
    reset_config()
    
    # Load the configuration
    config = load_app_config()
    
    # Check that the root path is set correctly
    root_path = config.Environment.pyegeria_root
    print(f"Root path with both env and config: {root_path}")
    assert root_path == "/test/env/path", f"Expected '/test/env/path', got '{root_path}'"
    
    # Clean up
    del os.environ["PYEGERIA_CONFIG_FILE"]
    del os.environ["PYEGERIA_ROOT_PATH"]
    os.unlink(temp_file_path)
    
    print("Root path precedence test passed!")

def test_root_path_default():
    """Test that the root path is empty when neither env nor config is set."""
    print("\nTesting root path default...")
    
    # Make sure the environment variables are not set
    if "PYEGERIA_ROOT_PATH" in os.environ:
        del os.environ["PYEGERIA_ROOT_PATH"]
    if "PYEGERIA_CONFIG_FILE" in os.environ:
        del os.environ["PYEGERIA_CONFIG_FILE"]
    
    # Reset the loaded configuration
    reset_config()
    
    # Load the configuration
    config = load_app_config()
    
    # Check that the root path is set correctly
    root_path = config.Environment.pyegeria_root
    print(f"Default root path: {root_path}")
    assert root_path == "", f"Expected empty string, got '{root_path}'"
    
    print("Root path default test passed!")

if __name__ == "__main__":
    test_root_path_from_env()
    test_root_path_from_config()
    test_root_path_precedence()
    test_root_path_default()
    print("\nAll root path tests passed!")