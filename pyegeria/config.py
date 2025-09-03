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
from pydantic import BaseModel, Field, validator, ConfigDict
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
    pyegeria_root: str = Field(default="", alias="Pyegeria Root")
    pyegeria_config_directory: str = Field(default="", alias="Pyegeria Config Directory")
    pyegeria_config_file: str = Field(default="config.json", alias="Egeria Config File")
    pyegeria_publishing_root: str = Field(default="/dr-egeria-outbox", alias="Pyegeria Publishing Root")
    pyegeria_user_format_sets_dir: str = Field(default="~/.pyegeria/format_sets", alias="Pyegeria User Format Sets Dir")
    
    model_config = ConfigDict(populate_by_name=True, extra='allow')


class DebugConfig(BaseModel):
    """Debug configuration settings"""
    debug_mode: bool = False
    enable_logger_catch: bool = False
    timeout_seconds: int = 30
    
    model_config = ConfigDict(populate_by_name=True, extra='allow')


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
    
    model_config = ConfigDict(populate_by_name=True, extra='allow')


class UserProfileConfig(BaseModel):
    """User profile configuration settings"""
    egeria_home_collection: str = Field(default="MyHome", alias="Egeria Home Collection")
    egeria_home_glossary_name: str = Field(default="Egeria-Markdown", alias="Egeria Home Glossary Name")
    egeria_local_qualifier: str = Field(default="PDR", alias="Egeria Local Qualifier")
    user_name: Optional[str] = "erinoverview"
    user_pwd: Optional[str] = "secret"
    
    model_config = ConfigDict(populate_by_name=True, extra='allow')


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
    
    model_config = ConfigDict(populate_by_name=True, extra='allow')


# --- Configuration Loading Logic ---

# Private variable to hold the loaded configuration
_app_config = None

def _resolve_env_settings(env_file: str | None) -> PyegeriaSettings:
    if env_file:
        return PyegeriaSettings.with_env_file(env_file)
    return PyegeriaSettings()


def _find_config_file_path(settings: PyegeriaSettings) -> str | None:
    config_dir = (settings.pyegeria_config_directory or "").strip()
    root_path = (settings.pyegeria_root_path or "").strip()
    config_file = (settings.pyegeria_config_file or "config.json").strip()

    candidates = []
    if config_dir:
        candidates.append(os.path.join(config_dir, config_file))
    if root_path:
        candidates.append(os.path.join(root_path, config_file))
    candidates.append(os.path.abspath(os.path.join(os.getcwd(), "config.json")))

    for path in candidates:
        if path and os.path.exists(path):
            return path
    return None


def load_app_config(env_file: str | None = None):
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

    # 1) Defaults from models
    config_dict: dict[str, Any] = {
        "Environment": {},
        "Debug": {},
        "Logging": {},
        "User Profile": {},
        "feature_x_enabled": False,
    }

    # 2) Load env settings from OS/.env according to env_file
    env_settings = _resolve_env_settings(env_file)

    # 3) Load config file if found
    file_path = _find_config_file_path(env_settings)
    if file_path:
        logger.info(f"Using config file: {file_path}")
        try:
            with open(file_path, "r") as f:
                file_cfg = json.load(f)
                if isinstance(file_cfg, dict):
                    config_dict.update(file_cfg)
                else:
                    logger.warning("Config file root is not an object; ignoring.")
        except Exception as e:
            logger.warning(f"Could not read/parse config file '{file_path}': {e}. Continuing with defaults+env.")
    else:
        logger.debug("No config.json found; continuing with defaults + env.")

    # 4) Overlay environment variables
    # Debug
    dbg = config_dict.setdefault("Debug", {})
    dbg["debug_mode"] = _parse_bool_env("PYEGERIA_DEBUG_MODE", bool(dbg.get("debug_mode", False)))
    dbg["enable_logger_catch"] = _parse_bool_env("PYEGERIA_ENABLE_LOGGER_CATCH", bool(dbg.get("enable_logger_catch", False)))
    dbg["timeout_seconds"] = int(os.getenv("PYEGERIA_TIMEOUT_SECONDS", dbg.get("timeout_seconds", 30)))

    # Environment
    env = config_dict.setdefault("Environment", {})
    default_root = env.get("Pyegeria Root") or os.getcwd()
    env_config_dir = os.getenv("PYEGERIA_CONFIG_DIRECTORY", env_settings.pyegeria_config_directory or "")
    env_root = os.getenv("PYEGERIA_ROOT_PATH", env_settings.pyegeria_root_path or default_root)
    env_config_file = os.getenv("PYEGERIA_CONFIG_FILE", env_settings.pyegeria_config_file or "config.json")

    env["Pyegeria Config Directory"] = env_config_dir
    env["pyegeria_config_directory"] = env_config_dir
    env["Pyegeria Root"] = env_root
    env["pyegeria_root"] = env_root
    env["Egeria Config File"] = env_config_file
    env["pyegeria_config_file"] = env_config_file

    env["Console Width"] = int(os.getenv("PYEGERIA_CONSOLE_WIDTH", env.get("Console Width", env_settings.pyegeria_console_width)))
    env["console_width"] = env["Console Width"]
    env["Dr.Egeria Inbox"] = os.getenv("DR_EGERIA_INBOX_PATH", env.get("Dr.Egeria Inbox", "md_processing/dr-egeria-inbox"))
    env["Dr.Egeria Outbox"] = os.getenv("DR_EGERIA_OUTBOX_PATH", env.get("Dr.Egeria Outbox", "md_processing/dr-egeria-outbox"))
    env["Egeria Engine Host"] = os.getenv("EGERIA_ENGINE_HOST", env.get("Egeria Engine Host", "qs-engine-host"))
    env["Egeria Engine Host URL"] = os.getenv("EGERIA_ENGINE_HOST_URL", env.get("Egeria Engine Host URL", "https://localhost:9443"))
    env["Egeria Glossary Path"] = os.getenv("EGERIA_GLOSSARY_PATH", env.get("Egeria Glossary Path", "glossary"))
    env["Egeria Integration Daemon"] = os.getenv("EGERIA_INTEGRATION_DAEMON", env.get("Egeria Integration Daemon", "qs-integration-daemon"))
    env["Egeria Integration Daemon URL"] = os.getenv("EGERIA_INTEGRATION_DAEMON_URL", env.get("Egeria Integration Daemon URL", "https://localhost:9443"))
    env["Egeria Jupyter"] = _parse_bool_env("EGERIA_JUPYTER", bool(env.get("Egeria Jupyter", True)))
    env["Egeria Kafka Endpoint"] = os.getenv("EGERIA_KAFKA", env.get("Egeria Kafka Endpoint", "localhost:9192"))
    env["Egeria Mermaid Folder"] = os.getenv("EGERIA_MERMAID_FOLDER", env.get("Egeria Mermaid Folder", "mermaid_graphs"))
    env["Egeria Metadata Store"] = os.getenv("EGERIA_METADATA_STORE", env.get("Egeria Metadata Store", "qs-metadata-store"))
    env["Egeria Platform URL"] = os.getenv("EGERIA_PLATFORM_URL", env.get("Egeria Platform URL", "https://localhost:9443"))
    env["Egeria View Server"] = os.getenv("EGERIA_VIEW_SERVER", env.get("Egeria View Server", "qs-view-server"))
    env["Egeria View Server URL"] = os.getenv("EGERIA_VIEW_SERVER_URL", env.get("Egeria View Server URL", "https://localhost:9443"))
    env["Pyegeria Publishing Root"] = os.getenv("PYEGERIA_PUBLISHING_ROOT", env.get("Pyegeria Publishing Root", "/dr-egeria-outbox"))
    env["Pyegeria User Format Sets Dir"] = os.getenv("PYEGERIA_USER_FORMAT_SETS_DIR", env.get("Pyegeria User Format Sets Dir", "~/.pyegeria/format_sets"))

    # Logging
    log = config_dict.setdefault("Logging", {})
    log["console_filter_levels"] = _parse_list_env("PYEGERIA_CONSOLE_FILTER_LEVELS", log.get("console_filter_levels", ["ERROR", "WARNING", "INFO", "SUCCESS"]))
    log["console_logging_enabled"] = _parse_list_env("PYEGERIA_CONSOLE_LOGGING_ENABLED", log.get("console_logging_enabled", ["pyegeria"]))
    log["console_logging_level"] = os.getenv("PYEGERIA_CONSOLE_LOG_LVL", log.get("console_logging_level", "INFO"))
    log["enable_logging"] = _parse_bool_env("PYEGERIA_ENABLE_LOGGING", bool(log.get("enable_logging", False)))
    log["file_logging_level"] = os.getenv("PYEGERIA_FILE_LOG_LVL", log.get("file_logging_level", "INFO"))
    log["log_directory"] = os.getenv("PYEGERIA_LOG_DIRECTORY", log.get("log_directory", "logs"))
    log["logging_console_format"] = os.getenv(
        "PYEGERIA_LOGGING_CONSOLE_FORMAT",
        log.get(
            "logging_console_format",
            " <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> -{extra}",
        ),
    )
    log["logging_file_format"] = os.getenv(
        "PYEGERIA_LOGGING_FILE_FORMAT",
        log.get("logging_file_format", " {time:YYYY-MM-DD HH:mm:ss} | {level} | {function}:{line} - {message }-{extra}"),
    )

    # User Profile
    user = config_dict.setdefault("User Profile", {})
    user["Egeria Home Collection"] = os.getenv("EGERIA_HOME_COLLECTION", user.get("Egeria Home Collection", "MyHome"))
    user["Egeria Home Glossary Name"] = os.getenv("EGERIA_HOME_GLOSSARY_NAME", user.get("Egeria Home Glossary Name", "Egeria-Markdown"))
    user["Egeria Local Qualifier"] = os.getenv("EGERIA_LOCAL_QUALIFIER", user.get("Egeria Local Qualifier", "PDR"))

    user_name = os.getenv("EGERIA_USER", user.get("user_name") or env_settings.egeria_user_name or None)
    user_pwd = os.getenv("EGERIA_USER_PASSWORD", user.get("user_pwd") or env_settings.egeria_user_password or None)
    user["user_name"] = user_name
    user["user_pwd"] = user_pwd

    # Feature flags
    feature_x = _parse_bool_value(os.getenv("FEATURE_X_ENABLED", config_dict.get("feature_x_enabled", False)))
    config_dict["feature_x_enabled"] = feature_x

    # Debug print of env before model creation
    try:
        logger.info(f"DEBUG ENV SECTION: {config_dict.get('Environment')}")
        _app_config = AppConfig(**config_dict)
    except Exception as e:
        context = {"caller method": inspect.currentframe().f_back.f_code.co_name}
        additional_info = {"reason": str(e)}
        raise PyegeriaInvalidParameterException(None, context, additional_info)

    return _app_config


def get_app_config(env_file: str = None)-> AppConfig:
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


# Export a lazily-evaluated settings accessor to avoid import-time side effects
class _LazySettings:
    def __getattr__(self, name):
        cfg = get_app_config()
        return getattr(cfg, name)

settings = _LazySettings()


def pretty_print_config(env_file: str | None = None, safe: bool = True, to_console: bool = True) -> Dict[str, Dict[str, Any]]:
    """
    Pretty print the current configuration and indicate the source of each value
    (Environment, .env file, config file, or default). Uses Rich if available.

    Args:
        env_file: Optional .env path to force loading before printing (if config not yet loaded).
        safe: Mask sensitive values such as passwords/tokens.
        to_console: If True, prints to console; function always returns a structured dict.

    Returns:
        dict mapping section -> { key -> {"value": ..., "source": ...} }
    """
    # Ensure config is loaded
    cfg = get_app_config(env_file)

    # Try import rich lazily
    try:
        from rich.console import Console
        from rich.table import Table
        from rich import box
        console = Console(width=getattr(cfg.Environment, 'console_width', 200))
        use_rich = True
    except Exception:
        console = None
        use_rich = False

    # Helper to mask sensitive keys
    def _mask(key: str, val: Any) -> Any:
        if not safe:
            return val
        key_l = (key or "").lower()
        if any(s in key_l for s in ["password", "pwd", "secret", "token", "apikey", "api_key"]):
            if val is None:
                return None
            s = str(val)
            if len(s) <= 4:
                return "****"
            return s[:2] + "****" + s[-2:]
        return val

    # Determine sources. Because we merge defaults, config.json, and env, we infer source:
    # - If an OS env var exists for a specific setting name we used, it's "env".
    # - Else if a config file was found (by our path resolver) and provided an override, mark "config".
    # - Else if value equals model default and neither env nor config provided, "default".

    # We need to reconstruct which keys are influenced by ENV VAR names.
    env_var_map = {
        # Debug
        ("Debug", "debug_mode"): "PYEGERIA_DEBUG_MODE",
        ("Debug", "enable_logger_catch"): "PYEGERIA_ENABLE_LOGGER_CATCH",
        ("Debug", "timeout_seconds"): "PYEGERIA_TIMEOUT_SECONDS",
        # Environment
        ("Environment", "Console Width"): "PYEGERIA_CONSOLE_WIDTH",
        ("Environment", "Dr.Egeria Inbox"): "DR_EGERIA_INBOX_PATH",
        ("Environment", "Dr.Egeria Outbox"): "DR_EGERIA_OUTBOX_PATH",
        ("Environment", "Egeria Engine Host"): "EGERIA_ENGINE_HOST",
        ("Environment", "Egeria Engine Host URL"): "EGERIA_ENGINE_HOST_URL",
        ("Environment", "Egeria Glossary Path"): "EGERIA_GLOSSARY_PATH",
        ("Environment", "Egeria Integration Daemon"): "EGERIA_INTEGRATION_DAEMON",
        ("Environment", "Egeria Integration Daemon URL"): "EGERIA_INTEGRATION_DAEMON_URL",
        ("Environment", "Egeria Jupyter"): "EGERIA_JUPYTER",
        ("Environment", "Egeria Kafka Endpoint"): "EGERIA_KAFKA",
        ("Environment", "Egeria Mermaid Folder"): "EGERIA_MERMAID_FOLDER",
        ("Environment", "Egeria Metadata Store"): "EGERIA_METADATA_STORE",
        ("Environment", "Egeria Platform URL"): "EGERIA_PLATFORM_URL",
        ("Environment", "Egeria View Server"): "EGERIA_VIEW_SERVER",
        ("Environment", "Egeria View Server URL"): "EGERIA_VIEW_SERVER_URL",
        ("Environment", "Pyegeria Publishing Root"): "PYEGERIA_PUBLISHING_ROOT",
        ("Environment", "Pyegeria User Format Sets Dir"): "PYEGERIA_USER_FORMAT_SETS_DIR",
        ("Environment", "Pyegeria Root"): "PYEGERIA_ROOT_PATH",
        ("Environment", "Pyegeria Config Directory"): "PYEGERIA_CONFIG_DIRECTORY",
        ("Environment", "Egeria Config File"): "PYEGERIA_CONFIG_FILE",
        # Logging
        ("Logging", "console_filter_levels"): "PYEGERIA_CONSOLE_FILTER_LEVELS",
        ("Logging", "console_logging_enabled"): "PYEGERIA_CONSOLE_LOGGING_ENABLED",
        ("Logging", "console_logging_level"): "PYEGERIA_CONSOLE_LOG_LVL",
        ("Logging", "enable_logging"): "PYEGERIA_ENABLE_LOGGING",
        ("Logging", "file_logging_level"): "PYEGERIA_FILE_LOG_LVL",
        ("Logging", "log_directory"): "PYEGERIA_LOG_DIRECTORY",
        ("Logging", "logging_console_format"): "PYEGERIA_LOGGING_CONSOLE_FORMAT",
        ("Logging", "logging_file_format"): "PYEGERIA_LOGGING_FILE_FORMAT",
        # User profile
        ("User Profile", "Egeria Home Collection"): "EGERIA_HOME_COLLECTION",
        ("User Profile", "Egeria Home Glossary Name"): "EGERIA_HOME_GLOSSARY_NAME",
        ("User Profile", "Egeria Local Qualifier"): "EGERIA_LOCAL_QUALIFIER",
        ("User Profile", "user_name"): "EGERIA_USER",
        ("User Profile", "user_pwd"): "EGERIA_USER_PASSWORD",
        # Feature flag example
        (None, "feature_x_enabled"): "FEATURE_X_ENABLED",
    }

    # Attempt to detect if a config.json was used
    env_settings = _resolve_env_settings(env_file)
    config_file_path = _find_config_file_path(env_settings)

    # Build a snapshot of defaults by instantiating empty models
    defaults = {
        "Environment": EnvironmentConfig().model_dump(by_alias=True),
        "Debug": DebugConfig().model_dump(by_alias=True),
        "Logging": LoggingConfig().model_dump(by_alias=False),
        "User Profile": UserProfileConfig().model_dump(by_alias=True),
        "feature_x_enabled": False,
    }

    # Current values from cfg
    sections = [
        ("Environment", cfg.Environment.model_dump(by_alias=True)),
        ("Debug", cfg.Debug.model_dump(by_alias=False)),
        ("Logging", cfg.Logging.model_dump(by_alias=False)),
        ("User Profile", cfg.User_Profile.model_dump(by_alias=True)),
    ]

    result: Dict[str, Dict[str, Any]] = {}

    for section_name, values in sections:
        section_out: Dict[str, Any] = {}
        for key, val in values.items():
            # Prefer alias keys in display; ensure key exists in defaults appropriately
            default_section = defaults.get(section_name, {})
            default_val = default_section.get(key, None)

            # Identify env var used for this key if any
            env_var = env_var_map.get((section_name, key))
            source = "default"
            if env_var and env_var in os.environ:
                source = "env"
            elif config_file_path and (key in (defaults.get(section_name, {}) or {}) or True):
                # If a config file exists and value differs from default and no env var set
                if val != default_val:
                    source = "config"
                else:
                    source = "default"
            else:
                source = "default"

            section_out[key] = {
                "value": _mask(key, val),
                "source": source,
            }
        result[section_name] = section_out

    # Add top-level feature flags
    feat_val = getattr(cfg, "feature_x_enabled", False)
    source = "env" if ("FEATURE_X_ENABLED" in os.environ) else ("config" if config_file_path and feat_val != defaults["feature_x_enabled"] else "default")
    result["feature_x_enabled"] = {"value": _mask("feature_x_enabled", feat_val), "source": source}

    if to_console:
        if use_rich and console:
            for section_name in ["Environment", "Debug", "Logging", "User Profile"]:
                table = Table(title=f"{section_name} Settings", box=box.SIMPLE_HEAVY)
                table.add_column("Key")
                table.add_column("Value")
                table.add_column("Source")
                for k, info in result[section_name].items():
                    table.add_row(str(k), str(info["value"]), info["source"])
                console.print(table)
            # Feature flags
            table = Table(title="Feature Flags", box=box.SIMPLE_HEAVY)
            table.add_column("Key")
            table.add_column("Value")
            table.add_column("Source")
            ff = result["feature_x_enabled"]
            table.add_row("feature_x_enabled", str(ff["value"]), ff["source"])
            console.print(table)
        else:
            # Plain text fallback
            print("Configuration:")
            for section_name in ["Environment", "Debug", "Logging", "User Profile"]:
                print(f"[{section_name}]")
                for k, info in result[section_name].items():
                    print(f"- {k}: {info['value']} (source: {info['source']})")
            ff = result["feature_x_enabled"]
            print(f"feature_x_enabled: {ff['value']} (source: {ff['source']})")

    return result