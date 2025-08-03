"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module manages configuration information for pyegeria and pyegeria clients.

The load_app_config() function loads configuration information:
1) Default configuration variables are specified in the Pydantic models below.
2) Environment variables are loaded from the .env file using pydantic-settings.
   - PYEGERIA_ROOT_PATH and PYEGERIA_CONFIG_FILE are loaded first to locate the config file
   - Additional environment variables are loaded from the operating system
3) We construct a path to an external configuration JSON file from the Environment Variables
   - PYEGERIA_ROOT_PATH
   - PYEGERIA_CONFIG_FILE
4) If a valid configuration file is found, the configuration will be loaded on top of the default configuration.
5) We then update the in-memory configuration from Environment Variables, if set.

The result is that Environment Variable values take priority over configuration file values which override the defaults.

The get_app_config() function is used by other modules to get configuration information from the configuration structure
and makes it available as a Pydantic model.

"""
import inspect
import os
import json
from typing import List, Optional, Union, Dict, Any

from loguru import logger
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from pyegeria._exceptions_new import PyegeriaInvalidParameterException, PyegeriaException

logger.disable("pyegeria")
# --- Pydantic Settings for Environment Variables ---

class PyegeriaSettings(BaseSettings):
    """
    Settings loaded from environment variables using pydantic-settings.
    This class is used to load environment variables from the .env file.
    
    The .env file path can be specified when creating an instance of this class
    by passing the `_env_file` parameter. If not specified, it defaults to ".env"
    in the current directory.
    """
    # Core settings needed to locate the config file
    pyegeria_root_path: str = ""
    pyegeria_config_directory: str = ""
    pyegeria_config_file: str = "config.json"
    
    # Additional settings that can be loaded from .env
    pyegeria_console_width: int = 200
    pyegeria_user_format_sets_dir: str = "~/.pyegeria/format_sets"
    egeria_user_name: str = ""
    egeria_user_password: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )
    
    @classmethod
    def with_env_file(cls, env_file: str):
        """
        Create a PyegeriaSettings instance with a specific .env file.
        
        Args:
            env_file: Path to the .env file to load
            
        Returns:
            PyegeriaSettings: A new PyegeriaSettings instance
        """
        # Create a new class with a custom model_config that specifies the env_file
        class CustomSettings(cls):
            model_config = SettingsConfigDict(
                env_file=env_file,
                env_file_encoding="utf-8",
                extra="ignore",
                case_sensitive=False
            )
        
        # Create and return an instance of the custom class
        return CustomSettings()


# --- Pydantic Models for Configuration ---

class EnvironmentConfig(BaseModel):
    """Environment configuration settings"""
    console_width: int = Field(default=200, alias="Console Width")
    dr_egeria_inbox: str = Field(default="md_processing/dr-egeria-inbox", alias="Dr.Egeria Inbox")
    dr_egeria_outbox: str = Field(default="md_processing/dr-egeria-outbox", alias="Dr.Egeria Outbox")
    egeria_engine_host_url: str = Field(default="", alias="Egeria Engine Host URL")
    egeria_engine_host: str = Field(default="qs-engine-host", alias="Egeria Engine Host")
    egeria_glossary_path: str = Field(default="glossary", alias="Egeria Glossary Path")
    egeria_integration_daemon_url: str = Field(default="https://localhost:9443", alias="Egeria Integration Daemon URL")
    egeria_integration_daemon: str = Field(default="qs-integration-daemon", alias="Egeria Integration Daemon")
    egeria_jupyter: bool = Field(default=True, alias="Egeria Jupyter")
    egeria_kafka_endpoint: str = Field(default="localhost:9192", alias="Egeria Kafka Endpoint")
    egeria_mermaid_folder: str = Field(default="mermaid_graphs", alias="Egeria Mermaid Folder")
    egeria_metadata_store: str = Field(default="qs-metadata-store", alias="Egeria Metadata Store")
    egeria_platform_url: str = Field(default="https://localhost:9443", alias="Egeria Platform URL")
    egeria_view_server_url: str = Field(default="https://localhost:9443", alias="Egeria View Server URL")
    egeria_view_server: str = Field(default="qs-view-server", alias="Egeria View Server")
    pyegeria_root: str = Field(default="/Users/dwolfson/localGit/egeria-v5-3/egeria-python", alias="Pyegeria Root")
    pyegeria_config_directory: str = Field(default="", alias="Pyegeria Config Directory")
    pyegeria_config_file: str = Field(default="config.json", alias="Egeria Config File")
    pyegeria_publishing_root: str = Field(default="/dr-egeria-outbox", alias="Pyegeria Publishing Root")
    pyegeria_user_format_sets_dir: str = Field(default="~/.pyegeria/format_sets", alias="Pyegeria User Format Sets Dir")
    
    class Config:
        populate_by_name = True
        extra = "allow"


class DebugConfig(BaseModel):
    """Debug configuration settings"""
    debug_mode: bool = False
    enable_logger_catch: bool = False
    timeout_seconds: int = 30
    
    class Config:
        populate_by_name = True
        extra = "allow"


class LoggingConfig(BaseModel):
    """Logging configuration settings"""
    console_filter_levels: List[str] = ["ERROR"]
    console_logging_enabled: List[str] = ["_client_new", "_exceptions_new", "collections_manager_omvs", "tests"]
    console_logging_level: str = "INFO"
    enable_logging: bool = False
    file_logging_level: str = "INFO"
    log_directory: str = "logs"
    logging_console_format: str = " <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> -{extra}"
    logging_file_format: str = " {time:YYYY-MM-DD HH:mm:ss} | {level} | {function}:{line} - {message }-{extra}"
    
    class Config:
        populate_by_name = True
        extra = "allow"


class UserProfileConfig(BaseModel):
    """User profile configuration settings"""
    egeria_home_collection: str = Field(default="MyHome", alias="Egeria Home Collection")
    egeria_home_glossary_name: str = Field(default="Egeria-Markdown", alias="Egeria Home Glossary Name")
    egeria_local_qualifier: str = Field(default="PDR", alias="Egeria Local Qualifier")
    user_name: str = ""
    user_pwd: str = ""
    
    @validator('user_name')
    def validate_user_name(cls, v):
        if not v:
            raise ValueError("Egeria user name is not found in the configuration")
        return v
    
    @validator('user_pwd')
    def validate_user_pwd(cls, v):
        if not v:
            raise ValueError("Egeria user password is not found in the configuration")
        return v
    
    class Config:
        populate_by_name = True
        extra = "allow"


class AppConfig(BaseModel):
    """Main application configuration"""
    Environment: EnvironmentConfig
    Debug: DebugConfig
    Logging: LoggingConfig
    User_Profile: UserProfileConfig = Field(alias="User Profile")
    feature_x_enabled: bool = False
    
    def get(self, key, default=None):
        """
        Dictionary-like get method for backward compatibility.
        
        Args:
            key: The key to look up
            default: The default value to return if the key is not found
            
        Returns:
            The value for the key if found, otherwise the default value
        """
        # First check if the key is a direct attribute of this model
        if hasattr(self, key):
            return getattr(self, key)
        
        # Then check if it's in any of the nested models
        for section in [self.Environment, self.Debug, self.Logging, self.User_Profile]:
            if hasattr(section, key):
                return getattr(section, key)
            # Also check using the original field names (with aliases)
            for field_name, field in section.model_fields.items():
                # In Pydantic v2, the alias is stored in json_schema_extra
                alias = None
                if hasattr(field, 'alias'):
                    alias = field.alias
                elif hasattr(field, 'json_schema_extra') and field.json_schema_extra:
                    alias = field.json_schema_extra.get('alias')
                
                if alias == key:
                    return getattr(section, field_name)
        
        # If not found, return the default
        return default
    
    class Config:
        populate_by_name = True
        extra = "allow"


# --- Configuration Loading Logic ---

# Private variable to hold the loaded configuration
_app_config = None

def load_app_config(env_file: str = None):
    """
    Loads application configuration from files and environment variables.
    This function should ideally be called only once at application startup.
    
    The function follows this precedence order for configuration settings:
    1. If env_file is passed in, it uses that file to load environment variables
    2. Otherwise, it first checks if OS environment variables are set for PYEGERIA_ROOT_PATH and PYEGERIA_CONFIG_FILE
    3. If they are not set, it checks for a .env file in the current directory
    4. It then loads the configuration from the config file if available
    5. Finally, it updates the configuration with environment variables from the operating system,
       which take precedence over the config file values
    
    Args:
        env_file: Optional path to a specific .env file to load. If not specified,
                 the function follows the precedence order described above.
    
    Returns:
        AppConfig: The loaded configuration as a Pydantic model
    """
    global _app_config  # Declare intent to modify the global _app_config

    if _app_config is not None:
        # Configuration already loaded, return existing instance
        return _app_config

    # Start with default configuration from Pydantic models
    config_dict = {
        "Environment": {},
        "Debug": {},
        "Logging": {},
        "User Profile": {},
        "feature_x_enabled": False
    }
    
    # Initialize env_settings with default values
    env_settings = PyegeriaSettings()
    
    # First check if OS environment variables are set for PYEGERIA_CONFIG_DIRECTORY, PYEGERIA_ROOT_PATH and PYEGERIA_CONFIG_FILE
    config_directory = os.getenv("PYEGERIA_CONFIG_DIRECTORY")
    root_path = os.getenv("PYEGERIA_ROOT_PATH")
    config_file = os.getenv("PYEGERIA_CONFIG_FILE")
    
    logger.info(f"DEBUG: Initial config_directory from OS env: {config_directory}")
    logger.info(f"DEBUG: Initial root_path from OS env: {root_path}")
    logger.info(f"DEBUG: Initial config_file from OS env: {config_file}")
    logger.info(f"DEBUG: env_file parameter: {env_file}")
    
    # If env_file is specified, use it to load environment variables
    if env_file is not None:
        logger.trace(f"DEBUG: Loading environment variables from {env_file}")
        env_settings = PyegeriaSettings.with_env_file(env_file)

        # If env_file is specified, always use its values, regardless of OS environment variables
        config_directory = env_settings.pyegeria_config_directory
        root_path = env_settings.pyegeria_root_path
        config_file = env_settings.pyegeria_config_file
    # If config_file is set but config_directory and root_path are not, we'll try to load the config file first
    # and only check the .env file if we still don't have a config_directory or root_path after loading the config file
    elif config_file is not None and config_directory is None and root_path is None:
        # We'll check for a .env file later if needed
        pass
    # If any of config_directory, root_path, or config_file is not set, check for a .env file in the current directory
    elif (config_directory is None or root_path is None or config_file is None):
        if os.path.exists(".env"):
            logger.info("Found .env file")
            logger.debug(f"DEBUG: Loading environment variables from .env in current directory")
            env_settings = PyegeriaSettings()
            logger.debug(f"DEBUG: env_settings.pyegeria_config_directory: {env_settings.pyegeria_config_directory}")
            logger.debug(f"DEBUG: env_settings.pyegeria_root_path: {env_settings.pyegeria_root_path}")
            logger.debug(f"DEBUG: env_settings.pyegeria_config_file: {env_settings.pyegeria_config_file}")
            if config_directory is None:
                config_directory = env_settings.pyegeria_config_directory
            if root_path is None:
                root_path = env_settings.pyegeria_root_path
            if config_file is None:
                config_file = env_settings.pyegeria_config_file
        else:
            logger.error(f"The .env file at {env_file} wasn't found")
    else:
        logger.error(f"The .env file at {env_file} wasn't found-outer")
    # Use default values if still not set
    if config_directory is None:
        config_directory = ""
    if root_path is None:
        root_path = ""
    if config_file is None:
        config_file = "config.json"
    
    # Construct the config file path - prefer config_directory over root_path
    if config_directory:
        config_file_path = os.path.join(config_directory, config_file)
    else:
        config_file_path = os.path.join(root_path, config_file)
    
    if os.path.exists(config_file_path):
        logger.info("Found config file at {}".format(config_file_path))
        try:
            with open(config_file_path, 'r') as f:
                file_config = json.load(f)
                config_dict.update(file_config)  # Merge/override defaults
                
                # If config_directory is not set from environment variables or .env file,
                # set it from the config file if available
                if not config_directory and "Environment" in file_config and "Pyegeria Config Directory" in file_config["Environment"]:
                    config_directory = file_config["Environment"]["Pyegeria Config Directory"]
                    logger.debug(f"DEBUG: Setting config_directory from config file: {config_directory}")
                # If config_directory is still not set and root_path is not set from environment variables or .env file,
                # set root_path from the config file if available
                if not config_directory and not root_path and "Environment" in file_config and "Pyegeria Root" in file_config["Environment"]:
                    root_path = file_config["Environment"]["Pyegeria Root"]
                    logger.debug(f"DEBUG: Setting root_path from config file: {root_path}")
        except json.JSONDecodeError:
            logger.warning(f"Warning: Could not parse {config_file_path}. Using defaults/env vars.")
        except Exception as e:
            logger.warning(f"Warning: Error reading {config_file_path}: {e}. Using defaults/env vars.")
    else:
        logger.warning(f"Warning: Could not find {config_file_path}. Using defaults/env vars.")

    # The root_path has already been set with the correct precedence order:
    # 1. If env_file is passed in, use that file to load environment variables
    # 2. Otherwise, first check OS environment variables
    # 3. If not set, check for a .env file in the current directory
    # 4. If still not set, use the default value
    # We don't need to set it again here, as that would override the precedence order
    env = config_dict.get("Environment", {})

    # Update configuration from environment variables
    # Debug section
    debug = config_dict["Debug"]
    debug['debug_mode'] = _parse_bool_env("PYEGERIA_DEBUG_MODE", debug.get("debug_mode", False))
    debug["enable_logger_catch"] = _parse_bool_env("PYEGERIA_ENABLE_LOGGER_CATCH", debug.get("enable_logger_catch", False))
    debug["timeout_seconds"] = int(os.getenv("PYEGERIA_TIMEOUT_SECONDS", debug.get("timeout_seconds", 30)))

    # Environment section
    env = config_dict["Environment"]
    # Use the settings from .env file, but allow OS environment variables to override them
    env["Console Width"] = int(os.getenv("PYEGERIA_CONSOLE_WIDTH", env.get("Console Width", env_settings.pyegeria_console_width)))
    env["Dr.Egeria Inbox"] = os.getenv("DR_EGERIA_INBOX_PATH", env.get("Dr.Egeria Inbox", "md_processing/dr-egeria-inbox"))
    env["Dr.Egeria Outbox"] = os.getenv("DR_EGERIA_OUTBOX_PATH", env.get("Dr.Egeria Outbox", "md_processing/dr-egeria-outbox"))
    env["Egeria Engine Host"] = os.getenv("EGERIA_ENGINE_HOST", env.get("Egeria Engine Host", "qs-engine-host"))
    env["Egeria Engine Host URL"] = os.getenv("EGERIA_ENGINE_HOST_URL", env.get("Egeria Engine Host URL", "https://localhost:9443"))
    env["Egeria Glossary Path"] = os.getenv("EGERIA_GLOSSARY_PATH", env.get("Egeria Glossary Path", "glossary"))
    env["Egeria Integration Daemon"] = os.getenv("EGERIA_INTEGRATION_DAEMON", env.get("Egeria Integration Daemon", "qs-integration-daemon"))
    env["Egeria Integration Daemon URL"] = os.getenv("EGERIA_INTEGRATION_DAEMON_URL", env.get("Egeria Integration Daemon URL", "https://localhost:9443"))
    env["Egeria Jupyter"] = _parse_bool_env("EGERIA_JUPYTER", env.get("Egeria Jupyter", True))
    env["Egeria Kafka Endpoint"] = os.getenv("EGERIA_KAFKA", env.get("Egeria Kafka Endpoint", "localhost:9192"))
    env["Egeria Mermaid Folder"] = os.getenv("EGERIA_MERMAID_FOLDER", env.get("Egeria Mermaid Folder", "mermaid_graphs"))
    env["Egeria Metadata Store"] = os.getenv("EGERIA_METADATA_STORE", env.get("Egeria Metadata Store", "qs-metadata-store"))
    env["Egeria Platform URL"] = os.getenv("EGERIA_PLATFORM_URL", env.get("Egeria Platform URL", "https://localhost:9443"))
    env["Egeria View Server"] = os.getenv("EGERIA_VIEW_SERVER", env.get("Egeria View Server", "qs-view-server"))
    env["Egeria View Server URL"] = os.getenv("EGERIA_VIEW_SERVER_URL", env.get("Egeria View Server URL", "https://localhost:9443"))
    env['Pyegeria Publishing Root'] = os.getenv("PYEGERIA_PUBLISHING_ROOT", env.get("Pyegeria Publishing Root", "/dr-egeria-outbox"))
    env['Pyegeria User Format Sets Dir'] = os.getenv("PYEGERIA_USER_FORMAT_SETS_DIR", env.get("Pyegeria User Format Sets Dir", "~/.pyegeria/format_sets"))
    # Set Pyegeria Config Directory to the config_directory value we've already determined with the correct precedence order
    env["Pyegeria Config Directory"] = config_directory
    # Set Pyegeria Root to the root_path value we've already determined with the correct precedence order
    env["Pyegeria Root"] = root_path

    # Logging section
    log = config_dict["Logging"]
    log["console_filter_levels"] = _parse_list_env("PYEGERIA_CONSOLE_FILTER_LEVELS", log.get("console_filter_levels", ["ERROR"]))
    log["console_logging_enabled"] = _parse_list_env("PYEGERIA_CONSOLE_LOGGING_ENABLED", log.get("console_logging_enabled", ["pyegeria"]))
    log["console_logging_level"] = os.getenv("PYEGERIA_CONSOLE_LOG_LVL", log.get("console_logging_level", "INFO"))
    log["enable_logging"] = _parse_bool_env("PYEGERIA_ENABLE_LOGGING", log.get("enable_logging", False))
    log["file_logging_level"] = os.getenv("PYEGERIA_FILE_LOG_LVL", log.get("file_logging_level", "INFO"))
    log["log_directory"] = os.getenv("PYEGERIA_LOG_DIRECTORY", log.get("log_directory", 'logs'))
    log["logging_console_format"] = os.getenv("PYEGERIA_LOGGING_CONSOLE_FORMAT", log.get("logging_console_format",
                                             "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | "
                                             "<cyan>{name}</cyan>:<cyan>{line}</cyan> - "
                                             "<level>{message}</level> -{extra}"))
    log["logging_file_format"] = os.getenv("PYEGERIA_LOGGING_FILE_FORMAT", log.get("logging_file_format",
                                           "{time:YYYY-MM-DD HH:mm:ss} | {level} | {function}:{line} "
                                           "- {message}-{extra}"))

    # User Profile section
    user = config_dict["User Profile"]
    user["Egeria Home Collection"] = os.getenv("EGERIA_HOME_COLLECTION", user.get("Egeria Home Collection", "myHome"))
    user["Egeria Home Glossary Name"] = os.getenv("EGERIA_HOME_GLOSSARY_NAME", user.get("Egeria Home Glossary Name", "Egeria-Markdown"))
    user["Egeria Local Qualifier"] = os.getenv("EGERIA_LOCAL_QUALIFIER", user.get("Egeria Local Qualifier", "myLocal"))
    
    # Load user credentials with proper precedence
    # 1. Check OS environment variables
    user_name = os.getenv("EGERIA_USER")
    user_pwd = os.getenv("EGERIA_USER_PASSWORD")
    
    # 2. If not set, check config file
    if user_name is None:
        user_name = user.get("user_name")
    if user_pwd is None:
        user_pwd = user.get("user_pwd")
    
    # 3. If still not set and we have env_settings, check .env file
    if (user_name is None or user_pwd is None) and 'env_settings' in locals():
        if user_name is None:
            user_name = env_settings.egeria_user_name
        if user_pwd is None:
            user_pwd = env_settings.egeria_user_password
    
    # Set the values in the config dictionary
    user["user_name"] = user_name
    user["user_pwd"] = user_pwd

    # Feature flags
    # Ensure feature_x_enabled is a boolean, regardless of what's in the config file
    feature_x = config_dict.get("feature_x_enabled", False)
    feature_x = _parse_bool_value(feature_x)
    # Check if the environment variable is set, which would override the config value
    if "FEATURE_X_ENABLED" in os.environ:
        feature_x = _parse_bool_value(os.getenv("FEATURE_X_ENABLED"))
    config_dict["feature_x_enabled"] = feature_x

    try:
        # Create Pydantic model from the configuration dictionary
        _app_config = AppConfig(**config_dict)
    except ValueError as e:
        # Handle validation errors from Pydantic
        context = {"caller method": inspect.currentframe().f_back.f_code.co_name}
        additional_info = {"reason": str(e)}
        raise PyegeriaInvalidParameterException(None, context, additional_info)

    return _app_config


def get_app_config(env_file: str = None):
    """
    Provides access to the loaded application configuration.
    Ensures config is loaded if not already (useful for testing or simple scripts).
    For structured apps, load_app_config() should be called explicitly once at startup.
    
    Args:
        env_file: Optional path to a specific .env file to load. If not specified,
                 the default .env file in the current directory is used.
    
    Returns:
        AppConfig: The loaded configuration as a Pydantic model
    """
    if _app_config is None:
        # If get_app_config is called before load_app_config, load it now.
        # This can be convenient but explicit loading is generally better.
        logger.info(f"The env_file {env_file} is being passed in")
        return load_app_config(env_file)
    return _app_config


def _parse_bool_env(env_var: str, default: bool) -> bool:
    """
    Parse a boolean environment variable.
    
    Args:
        env_var: The name of the environment variable
        default: The default value if the environment variable is not set
        
    Returns:
        bool: The parsed boolean value
    """
    if env_var in os.environ:
        value = os.getenv(env_var).lower()
        return value in ('true', '1', 't', 'y', 'yes', 'on')
    return default

def _parse_bool_value(value: Any) -> bool:
    """
    Parse a boolean value from any type.
    
    Args:
        value: The value to parse
        
    Returns:
        bool: The parsed boolean value
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 't', 'y', 'yes', 'on')
    if isinstance(value, (int, float)):
        return bool(value)
    return False


def _parse_list_env(env_var: str, default: List[str]) -> List[str]:
    """
    Parse a list environment variable (comma-separated).
    
    Args:
        env_var: The name of the environment variable
        default: The default value if the environment variable is not set
        
    Returns:
        List[str]: The parsed list value
    """
    if env_var in os.environ:
        value = os.getenv(env_var)
        if value:
            return [item.strip() for item in value.split(',')]
    return default