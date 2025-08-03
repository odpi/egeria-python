
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module configures logging using loguru. The pyegeria library modules do not configure
loguru automatically so that the calling application has control over the logging. However, if the
calling application doesn't have its own logging setup, it can use this module to configure loguru logging.

If the application uses another logging library, such as the built-in python logging, it can
do so by redirecting loguru output. Here is an example:

    # application.py - App uses standard logging, redirects Loguru)

    import logging
    import logging.config
    import sys # For sys.stderr
    from loguru import logger # Import Loguru's logger
    from my_library.my_module import MyLibraryClass, library_function

    # --- Standard Logging Configuration (for the application) ---
    # This is your application's primary logging setup.
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "standard",
                "filename": "app_standard.log",
                "maxBytes": 10485760,
                "backupCount": 5
            }
        },
        "loggers": {
            # Root logger for the application
            "": { # Empty string means the root logger
                "handlers": ["console", "file"],
                "level": "DEBUG", # Set the overall minimum level here
                "propagate": False
            }
        }
    }

    try:
        logging.config.dictConfig(LOGGING_CONFIG)
        app_logger = logging.getLogger(__name__)
        app_logger.info("Application standard logging configured successfully.")
    except Exception as e:
        print(f"Error configuring standard logging: {e}. Falling back to basicConfig.")
        logging.basicConfig(level=logging.INFO)
        app_logger = logging.getLogger(__name__)
        app_logger.warning("Using basic logging due to configuration error.")

    # --- Integrate Loguru with Standard Logging ---
    # This is the key to "disabling" Loguru's separate output.

    # 1. Remove Loguru's default handler (which outputs to stderr)
    logger.remove(0)

    # 2. Add a handler to Loguru that redirects messages to the standard logging module.
    #    The level here determines what Loguru sends to standard logging.
    logger.add(
        logging.StreamHandler(sys.stderr), # You can use any standard logging handler here
        level="DEBUG", # Loguru will send messages at this level or higher to standard logging
        format="{message}" # Keep Loguru's format simple, let standard logging handle formatting
    )

    # Optional: If you want to completely suppress Loguru's output and rely solely on standard logging
    # for your library's messages, you can set Loguru's level to a very high value:
    # logger.level("CRITICAL") # This would make it only log critical errors
    # Or, if you want to completely disable it (not recommended for general use):
    # logger.disable("my_library") # This disables logging for the 'my_library' hierarchy

    app_logger.info("Loguru integrated with standard logging.")

    # --- Main Application Logic ---
    if __name__ == "__main__":
        app_logger.info("Application started.")

        # Your library's logs will now go through the standard logging system
        my_instance = MyLibraryClass("test_value")
        processed = my_instance.process_data("hello world")
        app_logger.info("Processed data: %s", processed)

        library_function()

        try:
            my_instance.perform_risky_operation()
        except Exception:
            app_logger.error("Caught exception from risky operation in library.")

        app_logger.info("Application finished.")

To suppress logging, an application can do the following:
    # application.py (Scenario C: App wants library to be silent)

    from loguru import logger
    from my_library.my_module import MyLibraryClass, library_function

    # Remove Loguru's default handler
    logger.remove(0)

    # Completely disable logging for the 'my_library' hierarchy
    logger.disable("my_library")

    logger.info("Application started. Loguru for 'my_library' is disabled.")

    my_instance = MyLibraryClass("test_value")
    processed = my_instance.process_data("hello world") # These will not be logged by library
    logger.info("Processed data: %s", processed) # This will be logged by app's logger

    library_function() # This will not be logged by library

    logger.info("Application finished.")

"""

# application.py (Scenario A: App uses Loguru)
import os, sys
from loguru import logger
from pyegeria.load_config import get_app_config

# Load configuration parameters
app_settings = get_app_config()

def console_log_filter(record):
    if len(record["module"]) > 0:
        module_ok = True
    else:
        module_ok = record["module"] in app_settings.logging.console_logging_enabled


    return (module_ok
            and
            record["level"].name in app_settings.Logging.console_filter_levels
            )

def init_logging(log_init:bool= False):
    if not log_init:
       logger.disable("pyegeria")

def config_logging(verbose: bool=False):
    """
    Configures logging for the application using Loguru.

    This function sets up logging functionalities for the application. It reads
    the necessary logging configurations, ensures the desired log directory exists,
    and defines logging handlers for both file-based and console-based logging.
    Log messages can be retained with a rotation and compression policy for file logs.

    Raises:
        OSError: If the log directory cannot be created.

    """


    # Get the directory for log files from the environment variable
    log_app_settings = app_settings.Logging
    log_directory = log_app_settings.log_directory
    console_logging_level = log_app_settings.console_logging_level
    logging_console_format = log_app_settings.logging_console_format
    file_logging_level = log_app_settings.file_logging_level
    logging_file_format = log_app_settings.logging_file_format
    console_logging_enabled = log_app_settings.console_logging_enabled
    enable_logging = log_app_settings.enable_logging

    # Ensure the directory exists
    os.makedirs(log_directory, exist_ok=True)

    # Define the log file path
    log_file_path = os.path.join(log_directory, "pyegeria.log")
    # Remove Loguru's default stderr handler (id=0) if you want full control
    logger.remove()

    # Add your desired handlers for the application (and thus the library)
    logger.add(log_file_path,
               level=file_logging_level,
               format=logging_file_format,
               # filter = "",
               retention="7 days",  # Keep logs for 7 days
               rotation="10 MB", # rotate logs once they are 10mb
               compression="zip")
    logger.add(
        sys.stderr,
        level=console_logging_level,
        format=logging_console_format,
        filter=console_log_filter,
        colorize=True
    )

    if enable_logging:
        logger.enable("pyegeria")
    logger.trace("Application started with Loguru configured.")




