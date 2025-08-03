#!/usr/bin/env python3
"""
Test script to verify the changes to load_config.py.
"""
import os
import json
import tempfile
import shutil
from pathlib import Path
from pyegeria.load_config import load_app_config, get_app_config, PyegeriaSettings
from pyegeria._exceptions_new import PyegeriaInvalidParameterException

def reset_config():
    """Reset the loaded configuration to force reloading."""
    import pyegeria.load_config
    pyegeria.load_config._app_config = None

def test_parameter_passing():
    """Test that the env_file parameter is correctly passed from get_app_config to load_app_config."""
    print("\nTesting parameter passing between functions...")
    
    # Save the original environment variables
    original_env = {}
    for var in ["PYEGERIA_ROOT_PATH", "PYEGERIA_CONFIG_FILE", "EGERIA_USER_NAME", "EGERIA_USER_PASSWORD"]:
        if var in os.environ:
            original_env[var] = os.environ[var]
    
    try:
        # Set environment variables to ensure the test works
        os.environ["EGERIA_USER_NAME"] = "test_user"
        os.environ["EGERIA_USER_PASSWORD"] = "test_password"
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temporary .env file
            env_file = Path(temp_dir) / ".env"
            with open(env_file, 'w') as f:
                f.write("PYEGERIA_ROOT_PATH=/test/env/path\n")
                f.write("PYEGERIA_CONFIG_FILE=test_config.json\n")
                f.write("EGERIA_USER_NAME=env_user\n")
                f.write("EGERIA_USER_PASSWORD=env_password\n")
            
            # Reset the loaded configuration
            reset_config()
            
            # Load the configuration using get_app_config with the env_file parameter
            config = get_app_config(str(env_file))
            
            # Check that the configuration was loaded correctly
            print(f"Root path: {config.Environment.pyegeria_root}")
            assert config.Environment.pyegeria_root == "/test/env/path", f"Expected '/test/env/path', got '{config.Environment.pyegeria_root}'"
            
            print("Parameter passing test passed!")
    finally:
        # Restore the original environment variables
        for var in ["PYEGERIA_ROOT_PATH", "PYEGERIA_CONFIG_FILE", "EGERIA_USER_NAME", "EGERIA_USER_PASSWORD"]:
            if var in original_env:
                os.environ[var] = original_env[var]
            elif var in os.environ:
                del os.environ[var]

def test_precedence_order():
    """Test that the precedence order for configuration settings is correct."""
    print("\nTesting precedence order for configuration settings...")
    
    # Save the original environment variables
    original_env = {}
    for var in ["PYEGERIA_ROOT_PATH", "PYEGERIA_CONFIG_FILE", "EGERIA_USER_NAME", "EGERIA_USER_PASSWORD"]:
        if var in os.environ:
            original_env[var] = os.environ[var]
    
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temporary .env file
            env_file = Path(temp_dir) / ".env"
            with open(env_file, 'w') as f:
                f.write("PYEGERIA_ROOT_PATH=/env/file/path\n")
                f.write("PYEGERIA_CONFIG_FILE=env_config.json\n")
                f.write("EGERIA_USER_NAME=env_user\n")
                f.write("EGERIA_USER_PASSWORD=env_password\n")
            
            # Create a temporary config file
            config_file = Path(temp_dir) / "config.json"
            with open(config_file, 'w') as f:
                json.dump({
                    "Environment": {
                        "Pyegeria Root": "/config/file/path"
                    },
                    "User Profile": {
                        "user_name": "config_user",
                        "user_pwd": "config_password"
                    }
                }, f)
            
            # Test 1: OS environment variables take precedence over .env file and config file
            os.environ["PYEGERIA_ROOT_PATH"] = "/os/env/path"
            os.environ["PYEGERIA_CONFIG_FILE"] = "os_config.json"
            os.environ["EGERIA_USER_NAME"] = "os_user"
            os.environ["EGERIA_USER_PASSWORD"] = "os_password"
            
            # Reset the loaded configuration
            reset_config()
            
            # Save the original working directory
            original_dir = os.getcwd()
            
            try:
                # Change to the temporary directory
                os.chdir(temp_dir)
                
                # Create a dummy config file to avoid errors
                with open("os_config.json", 'w') as f:
                    json.dump({
                        "Environment": {},
                        "Debug": {},
                        "Logging": {},
                        "User Profile": {}
                    }, f)
                
                # Load the configuration
                config = load_app_config()
                
                # Check that the OS environment variables were used
                print(f"Root path (should be from OS env): {config.Environment.pyegeria_root}")
                assert config.Environment.pyegeria_root == "/os/env/path", f"Expected '/os/env/path', got '{config.Environment.pyegeria_root}'"
                print(f"User name (should be from OS env): {config.User_Profile.user_name}")
                assert config.User_Profile.user_name == "os_user", f"Expected 'os_user', got '{config.User_Profile.user_name}'"
                
                # Test 2: If OS environment variables are not set, .env file is used
                del os.environ["PYEGERIA_ROOT_PATH"]
                del os.environ["PYEGERIA_CONFIG_FILE"]
                del os.environ["EGERIA_USER_NAME"]
                del os.environ["EGERIA_USER_PASSWORD"]
                
                # Reset the loaded configuration
                reset_config()
                
                # Load the configuration
                config = load_app_config()
                
                # Check that the .env file values were used
                print(f"Root path (should be from .env file): {config.Environment.pyegeria_root}")
                assert config.Environment.pyegeria_root == "/env/file/path", f"Expected '/env/file/path', got '{config.Environment.pyegeria_root}'"
                print(f"User name (should be from .env file): {config.User_Profile.user_name}")
                assert config.User_Profile.user_name == "env_user", f"Expected 'env_user', got '{config.User_Profile.user_name}'"
                
                # Test 3: If neither OS environment variables nor .env file are set, config file is used
                # Move the .env file to simulate it not existing
                shutil.move(env_file, env_file.with_suffix(".bak"))
                
                # Reset the loaded configuration
                reset_config()
                
                # Rename the config file to the expected name instead of copying it
                os.rename(config_file, "../config/config.json")
                
                # Load the configuration
                config = load_app_config()
                
                # Check that the config file values were used
                print(f"Root path (should be from config file): {config.Environment.pyegeria_root}")
                assert config.Environment.pyegeria_root == "/config/file/path", f"Expected '/config/file/path', got '{config.Environment.pyegeria_root}'"
                print(f"User name (should be from config file): {config.User_Profile.user_name}")
                assert config.User_Profile.user_name == "config_user", f"Expected 'config_user', got '{config.User_Profile.user_name}'"
                
            finally:
                # Change back to the original directory
                os.chdir(original_dir)
            
            print("Precedence order test passed!")
    finally:
        # Restore the original environment variables
        for var in ["PYEGERIA_ROOT_PATH", "PYEGERIA_CONFIG_FILE", "EGERIA_USER_NAME", "EGERIA_USER_PASSWORD"]:
            if var in original_env:
                os.environ[var] = original_env[var]
            elif var in os.environ:
                del os.environ[var]

def test_missing_credentials():
    """Test that an exception is thrown when credentials are missing."""
    print("\nTesting exception for missing credentials...")
    
    # Save the original environment variables
    original_env = {}
    for var in ["PYEGERIA_ROOT_PATH", "PYEGERIA_CONFIG_FILE", "EGERIA_USER_NAME", "EGERIA_USER_PASSWORD"]:
        if var in os.environ:
            original_env[var] = os.environ[var]
    
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temporary config file with missing credentials
            config_file = Path(temp_dir) / "config.json"
            with open(config_file, 'w') as f:
                json.dump({
                    "Environment": {},
                    "Debug": {},
                    "Logging": {},
                    "User Profile": {}
                }, f)
            
            # Reset the loaded configuration
            reset_config()
            
            # Save the original working directory
            original_dir = os.getcwd()
            
            try:
                # Change to the temporary directory
                os.chdir(temp_dir)
                
                # Test 1: Missing username
                os.environ["EGERIA_USER_PASSWORD"] = "test_password"
                if "EGERIA_USER_NAME" in os.environ:
                    del os.environ["EGERIA_USER_NAME"]
                
                # Reset the loaded configuration
                reset_config()
                
                # Load the configuration - this should raise an exception
                try:
                    config = load_app_config()
                    print("ERROR: Exception not raised for missing username!")
                    assert False, "Exception not raised for missing username"
                except PyegeriaInvalidParameterException as e:
                    print(f"Exception correctly raised for missing username: {type(e).__name__}")
                    print(f"Error message: {str(e)}")
                    assert "Egeria user name is not found" in str(e), f"Expected error message about missing username, got: {str(e)}"
                
                # Test 2: Missing password
                os.environ["EGERIA_USER_NAME"] = "test_user"
                if "EGERIA_USER_PASSWORD" in os.environ:
                    del os.environ["EGERIA_USER_PASSWORD"]
                
                # Reset the loaded configuration
                reset_config()
                
                # Load the configuration - this should raise an exception
                try:
                    config = load_app_config()
                    print("ERROR: Exception not raised for missing password!")
                    assert False, "Exception not raised for missing password"
                except PyegeriaInvalidParameterException as e:
                    print(f"Exception correctly raised for missing password: {type(e).__name__}")
                    print(f"Error message: {str(e)}")
                    assert "Egeria user password is not found" in str(e), f"Expected error message about missing password, got: {str(e)}"
                
            finally:
                # Change back to the original directory
                os.chdir(original_dir)
            
            print("Missing credentials test passed!")
    finally:
        # Restore the original environment variables
        for var in ["PYEGERIA_ROOT_PATH", "PYEGERIA_CONFIG_FILE", "EGERIA_USER_NAME", "EGERIA_USER_PASSWORD"]:
            if var in original_env:
                os.environ[var] = original_env[var]
            elif var in os.environ:
                del os.environ[var]

if __name__ == "__main__":
    test_parameter_passing()
    test_precedence_order()
    test_missing_credentials()
    print("\nAll tests passed!")