#!/usr/bin/env python3
"""
Simple test script to verify the refactored load_config.py implementation.
"""
import os
from pyegeria.load_config import load_app_config, get_app_config

def test_config_loading():
    """Test that configuration loading works correctly."""
    print("Testing configuration loading...")
    
    # Test loading with default values
    config = load_app_config()
    print(f"Loaded configuration: {type(config)}")
    
    # Test accessing values through the Pydantic model
    print(f"Platform URL: {config.Environment.egeria_platform_url}")
    print(f"Debug mode: {config.Debug.debug_mode}")
    print(f"Logging enabled: {config.Logging.enable_logging}")
    print(f"User name: {config.User_Profile.user_name}")
    
    # Test get_app_config
    config2 = get_app_config()
    print(f"Same config object: {config is config2}")
    
    print("Configuration loading test completed successfully!")

def test_env_override():
    """Test that environment variables override configuration values."""
    print("\nTesting environment variable override...")
    
    # Set an environment variable
    os.environ["EGERIA_PLATFORM_URL"] = "https://test-override:9443"
    
    # Clear the loaded configuration to force reloading
    import pyegeria.load_config
    pyegeria.load_config._app_config = None
    
    # Reload the configuration
    config = load_app_config()
    
    # Check that the environment variable override worked
    print(f"Platform URL (should be overridden): {config.Environment.egeria_platform_url}")
    
    # Clean up
    del os.environ["EGERIA_PLATFORM_URL"]
    
    print("Environment variable override test completed!")

def test_validation():
    """Test that validation works correctly."""
    print("\nTesting validation...")
    
    # Set an environment variable to an invalid value
    os.environ["EGERIA_USER_PASSWORD"] = ""
    
    # Clear the loaded configuration to force reloading
    import pyegeria.load_config
    pyegeria.load_config._app_config = None
    
    # Reload the configuration - this should raise an exception
    try:
        config = load_app_config()
        print("ERROR: Validation failed to catch empty password!")
    except Exception as e:
        print(f"Validation correctly caught the error: {type(e).__name__}")
        print(f"Error message: {str(e)}")
    
    # Clean up
    del os.environ["EGERIA_USER_PASSWORD"]
    
    print("Validation test completed!")

if __name__ == "__main__":
    test_config_loading()
    test_env_override()
    test_validation()