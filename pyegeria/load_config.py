
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module configures logging for pyegeria.
"""
import os

PYEGERIA_LOG_DIRECTORY = os.getenv("PYEGERIA_LOG_DIRECTORY", "/tmp")
PYEGERIA_CONSOLE_LOG_LVL = os.getenv("PYEGERIA_CONSOLE_LOG_LVL", "INFO")
PYEGERIA_FILE_LOG_LVL = os.getenv("PYEGERIA_FILE_LOG_LVL", "TRACE")

# config.py

import os
import json
# from dotenv import load_dotenv # pip install python-dotenv if you use .env files

# --- Configuration Loading Logic ---

# Private variable to hold the loaded configuration
_app_config = None

def load_app_config():
    """
    Loads application configuration from files and environment variables.
    This function should ideally be called only once at application startup.
    """
    global _app_config # Declare intent to modify the global _app_config

    if _app_config is not None:
        # Configuration already loaded, return existing instance
        return _app_config

    # 1. Load .env variables first if present (for local development)
    #    This ensures os.getenv can pick them up.
    # load_dotenv()

    # Define default configuration values
    config = {
        "log_directory": "/tmp",
        "console_logging_level": "INFO",
        "console_format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{module}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        "file_logging_level": "TRACE",
        "file_format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{line} - {message}",
        "timeout_seconds": 30,
        "debug_mode": False,
        "feature_x_enabled": False
    }

    # 2. Load from a configuration file (e.g., config.json)
    #    This allows overriding defaults with file-based settings.
    config_file_path = 'config.json' # Or config.yaml, config.ini etc.
    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config) # Merge/override defaults
        except json.JSONDecodeError:
            print(f"Warning: Could not parse {config_file_path}. Using defaults/env vars.")
        except Exception as e:
            print(f"Warning: Error reading {config_file_path}: {e}. Using defaults/env vars.")

    # 3. Override with environment variables
    #    Environment variables take highest precedence.
    config["log_directory"] = os.getenv("PYEGERIA_LOG_DIRECTORY", config.get("log_directory",None))
    config["console_logging_level"] = os.getenv("PYEGERIA_CONSOLE_LOG_LVL", config.get("console_logging_level",None))
    config["file_logging_level"] = os.getenv("PYEGERIA_FILE_LOG_LVL", config.get("file_logging_level",None))


    # Handle type conversion for env vars (they are always strings)
    # if "TIMEOUT_SECONDS" in os.environ:
    #     try:
    #         config["timeout_seconds"] = int(os.getenv("TIMEOUT_SECONDS"))
    #     except ValueError:
    #         print("Warning: TIMEOUT_SECONDS environment variable is not an integer. Using default.")
    #
    # if "DEBUG_MODE" in os.environ:
    #     # Convert string "true", "false", "1", "0" to boolean
    #     debug_str = os.getenv("DEBUG_MODE").lower()
    #     config["debug_mode"] = debug_str in ('true', '1', 't', 'y', 'yes', 'on')
    #
    # if "FEATURE_X_ENABLED" in os.environ:
    #     feature_x_str = os.getenv("FEATURE_X_ENABLED").lower()
    #     config["feature_x_enabled"] = feature_x_str in ('true', '1', 't', 'y', 'yes', 'on')

    # 4. Handle sensitive API key (only from environment variable)
    # config["api_key"] = os.getenv("MY_SERVICE_API_KEY")
    # if config["api_key"] is None:
    #     print("Error: MY_SERVICE_API_KEY environment variable is critical and not set.")
    #     # In a production application, you might raise a critical exception here:
    #     # raise ValueError("MY_SERVICE_API_KEY is not set!")

    _app_config = config # Store the final loaded configuration
    return _app_config

def get_app_config():
    """
    Provides access to the loaded application configuration.
    Ensures config is loaded if not already (useful for testing or simple scripts).
    For structured apps, load_app_config() should be called explicitly once at startup.
    """
    if _app_config is None:
        # If get_app_config is called before load_app_config, load it now.
        # This can be convenient but explicit loading is generally better.
        return load_app_config()
    return _app_config

# You can also define constants based on the config for common access,
# but be aware these won't update if the config changes after initial load.
# E.g., API_ENDPOINT = get_app_config().get("api_endpoint")