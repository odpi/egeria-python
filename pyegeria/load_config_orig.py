
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module manages configuration information for pyegeria and pyegeria clients.

The load_app_config() function loads configuration information:
1) Default configuration variables are specified in the Dict structure below.
2) We construct a path to an external configuration JSON file from the Environment Variables
    - PYEGERIA_ROOT_PATH
    - PYEGERIA_CONFIG_FILE
3) If a valid configuration file is found, the configuration will be loaded on top of the default configuration.
4) We then update the in-memory configuration from Environment Variables, if set.

The result is that Environment Variable values take priority over configuration file values which override the defaults.

The get_app_config() function is used by other modules to get configuration information from the configuration structure
and makes it available as a dict.

"""
import inspect
import os
import json

from loguru import logger
from pyegeria._exceptions_new import PyegeriaInvalidParameterException


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


    # Define default configuration values
    config = {
        "Environment": {
                "Console Width": 200,
                "Dr.Egeria Inbox": "md_processing/dr-egeria-inbox",
                "Dr.Egeria Outbox": "md_processing/dr-egeria-outbox",
                "Egeria Engine Host URL": "",
                "Egeria Engine Host": "qs-engine-host",
                "Egeria Glossary Path": "glossary",
                "Egeria Integration Daemon URL": "https://localhost:9443",
                "Egeria Integration Daemon": "qs-integration-daemon",
                "Egeria Jupyter": True,
                "Egeria Kafka Endpoint": "localhost:9192",
                "Egeria Mermaid Folder": "mermaid_graphs",
                "Egeria Metadata Store": "qs-metadata-store",
                "Egeria Platform URL": "https://localhost:9443",
                "Egeria View Server URL": "https://localhost:9443",
                "Egeria View Server": "qs-view-server",
                "Pyegeria Root": "/Users/dwolfson/localGit/egeria-v5-3/egeria-python",
        },

        "Debug": {
                "debug_mode": False,
                "enable_logger_catch": False,
                "timeout_seconds": 30,
        },
        "feature_x_enabled": False,
        "Logging": {
                "console_filter_levels": [
                        "ERROR"
                ],
                "console_logging_enabled": [
                        "_client_new",
                        "_exceptions_new",
                        "collections_manager_omvs"
                        "tests",
                ],
                "console_logging_level": "INFO",
                "enable_logging": False,
                "file_logging_level": "INFO",
                "log_directory": "logs",
                "logging_console_format":
                    " <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> -{extra}",
                    " <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> |"
                "logging_file_format":
                    " {time:YYYY-MM-DD HH:mm:ss} | {level} | {function}:{line} - {message }-{extra}"
        },
        "User Profile": {
                "Egeria Home Collection": "MyHome",
                "Egeria Home Glossary Name": "Egeria-Markdown",
                "Egeria Local Qualifier": "PDR"
        }
}

    root_path = os.getenv("PYEGERIA_ROOT_PATH", config["Environment"].get("Pyegeria Root",""))
    config_file = os.getenv("PYEGERIA_CONFIG_FILE", "config.json")
    config_file_path = os.path.join(root_path,config_file)
    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config) # Merge/override defaults
                # logger.debug("Configuration file loaded from {}".format(config_file_path))
        except json.JSONDecodeError:
            print(f"Warning: Could not parse {config_file_path}. Using defaults/env vars.")
        except Exception as e:
            print(f"Warning: Error reading {config_file_path}: {e}. Using defaults/env vars.")
    else:
        logger.warning(f"Warning: Could not find {config_file_path}. Using defaults/env vars.")

    debug = config["Debug"]
    debug['debug_mode'] = os.getenv("PYEGERIA_DEBUG_MODE", debug.get("debug_mode", False))
    debug["enable_logger_catch"] = os.getenv("PYEGERIA_ENABLE_LOGGER_CATCH", debug.get("enable_logger_catch", False))
    debug["timeout_seconds"] = int(os.getenv("PYEGERIA_TIMEOUT_SECONDS", debug.get("timeout_seconds", 30)))

    env = config["Environment"]
    env["Console Width"] = int(os.getenv("PYEGERIA_CONSOLE_WIDTH", env.get("EGERIA_WIDTH", 200)))
    env["Dr.Egeria Inbox"] = os.getenv("DR_EGERIA_INBOX_PATH", env.get("Dr_EGERIA_INBOX",
                                                                       "md_processing/dr-egeria-inbox"))
    env["Dr.Egeria Outbox"] = os.getenv("DR_EGERIA_OUTBOX_PATH", env.get("DR_EGERIA_OUTBOX",
                                                                         "md_processing/dr-egeria-outbox"))
    env["Egeria Engine Host"] = os.getenv("EGERIA_ENGINE_HOST", env.get("Egeria Engine Host", "qs-engine-host"))
    env["Egeria Engine Host URL"] = os.getenv("EGERIA_ENGINE_HOST_URL",env.get("Egeria Engine Host URL", "https://localhost:9443"))

    env["Egeria Glossary Path"] = os.getenv("EGERIA_GLOSSARY_PATH", env.get("Egeria Glossary Path", "glossary"))
    env["Egeria Integration Daemon"] = os.getenv("EGERIA_INTEGRATION_DAEMON", env.get("Egeria Integration Daemon", "qs-integration-daemon"))
    env["Egeria Integration Daemon URL"] = os.getenv("EGERIA_INTEGRATION_DAEMON_URL",env.get("Egeria Integration Daemon URL", "https://localhost:9443"))
    env["Egeria Jupyter"] = os.getenv("EGERIA_JUPYTER", env.get("Egeria Jupyter", True))
    env["Egeria Kafka"] = os.getenv("EGERIA_KAFKA", env.get("Egeria Kafka", "https://localhost:9192"))
    env["Egeria Mermaid Folder"] = os.getenv("EGERIA_MERMAID_FOLDER", env.get("Egeria Mermaid Folder","mermaid_graphs"))
    env["Egeria Metadata Store"] = os.getenv("EGERIA_METADATA_STORE", env.get("Egeria Metadata Store","qs-metadata-store"))
    env["Egeria Platform URL"] = os.getenv("EGERIA_PLATFORM_URL", env.get("Egeria Platform URL","https://localhost:9443"))
    env["Egeria View Server"] = os.getenv("EGERIA_VIEW_SERVER", env.get("Egeria View Server","qs-view-server"))
    env["Egeria VIew Server URL"] = os.getenv("EGERIA_VIEW_SERVER_URL", env.get("Egeria View Server URL","https://localhost:9443"))
    env["Pyegeria Root"] = root_path

    log = config["Logging"]
    log["console_filter_levels"] = os.getenv("PYEGERIA_CONSOLE_FILTER_LEVELS",
                                                log.get("console_filter_levels", ["ERROR"]))
    log["console_logging_enabled"] = os.getenv("PYEGERIA_CONSOLE_LOGGING_ENABLED",
                                                  log.get("console_logging_enabled", ["tests"]))
    log["console_logging_level"] = os.getenv("PYEGERIA_CONSOLE_LOG_LVL", log.get("console_logging_level", None))
    log["enable_logging"] = os.getenv("PYEGERIA_ENABLE_LOGGING", log.get("enable_logging", False))
    log["file_logging_level"] = os.getenv("PYEGERIA_FILE_LOG_LVL", log.get("file_logging_level","INFO"))
    log["log_directory"] = os.getenv("PYEGERIA_LOG_DIRECTORY", log.get("log_directory",'logs'))
    log["logging_console_format"] = os.getenv("PYEGERIA_LOGGING_CONSOLE_FORMAT", log.get("logging_console_format",
                                             " <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | "
                                             "<cyan>{name}</cyan>:<cyan>{line}</cyan> - "
                                             "<level>{message}</level> -{extra}"  ))
    log["logging_file_format"] = os.getenv("PYEGERIA_LOGGING_FILE_FORMAT",log.get("logging_file_format",
                                           " {time:YYYY-MM-DD HH:mm:ss} | {level} | {function}:{line} "
                                           "- {message }-{extra}"  ))

    user = config["User Profile"]
    user["Egeria Home Collection"] = os.getenv("EGERIA_HOME_COLLECTION", user.get("Egeria Home Collection", "myHome"))
    user["Egeria Home Glossary Name"] = os.getenv("EGERIA_HOME_GLOSSARY_NAME", user.get("Egeria Home Glossary Name", "Egeria-Markdown"))
    user["Egeria Local Qualifier"] = os.getenv("EGERIA_LOCAL_QUALIFIER", user.get("Egeria Local Qualifier", "myLocal"))
    user["user_name"] = os.getenv("EGERIA_USER_NAME", "peterprofile")
    user["user_pwd"] = os.getenv("EGERIA_USER_PASSWORD", "secret")

    if not user.get("user_pwd"):
        context: dict = {}
        context['caller method'] = inspect.currentframe().f_back.f_code.co_name
        additional_info: dict = {"reason": "Egeria user password is not found in the environment"}
        raise PyegeriaInvalidParameterException(None, context, additional_info)




    # Handle type conversion for env vars (they are always strings)
    # if "TIMEOUT_SECONDS" in os.environ:
    #     try:
    #         config["timeout_seconds"] = int(os.getenv("TIMEOUT_SECONDS"))
    #     except ValueError:
    #         print("Warning: TIMEOUT_SECONDS environment variable is not an integer. Using default.")
    #
    # if "DEBUG_MODE" in os.environ:
    #     # Convert string "True", "False", "1", "0" to boolean
    #     debug_str = os.getenv("DEBUG_MODE").lower()
    #     config["debug_mode"] = debug_str in ('True', '1', 't', 'y', 'yes', 'on')
    #
    # if "FEATURE_X_ENABLED" in os.environ:
    #     feature_x_str = os.getenv("FEATURE_X_ENABLED").lower()
    #     config["feature_x_enabled"] = feature_x_str in ('True', '1', 't', 'y', 'yes', 'on')

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