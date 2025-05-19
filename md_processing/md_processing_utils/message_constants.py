"""
This file contains message-related constants for Egeria Markdown processing.
These constants are separated from other modules to avoid circular imports.
"""

# Define message_types
message_types = {
    "INFO": "INFO-", "WARNING": "WARNING->", "ERROR": "ERROR->", "DEBUG-INFO": "DEBUG-INFO->",
    "DEBUG-WARNING": "DEBUG-WARNING->", "DEBUG-ERROR": "DEBUG-ERROR->", "ALWAYS": "\n\n==> "
}

# Constants for message levels
ALWAYS = "ALWAYS"
ERROR = "ERROR"
INFO = "INFO"
WARNING = "WARNING"

# Other constants
EXISTS_REQUIRED = "Exists Required"
