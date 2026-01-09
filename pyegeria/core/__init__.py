"""
Core module for pyegeria.
"""
from pyegeria.core._server_client import ServerClient
from pyegeria.core._exceptions import (
    PyegeriaException,
    PyegeriaAPIException,
    PyegeriaConnectionException,
    PyegeriaNotFoundException,
    PyegeriaUnauthorizedException,
    PyegeriaInvalidParameterException,
    PyegeriaClientException,
    PyegeriaUnknownException,
)
from pyegeria.core._globals import (
    default_time_out,
    disable_ssl_warnings,
    enable_ssl_check,
    is_debug,
    max_paging_size,
    NO_ELEMENTS_FOUND,
)

__all__ = [
    "ServerClient",
    "PyegeriaException",
    "PyegeriaAPIException",
    "PyegeriaConnectionException",
    "PyegeriaNotFoundException",
    "PyegeriaUnauthorizedException",
    "PyegeriaInvalidParameterException",
    "PyegeriaClientException",
    "PyegeriaUnknownException",
    "default_time_out",
    "disable_ssl_warnings",
    "enable_ssl_check",
    "is_debug",
    "max_paging_size",
    "NO_ELEMENTS_FOUND",
]
