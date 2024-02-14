"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This is the pyegeria client package. The purpose of the package is to provide
easy access to Egeria (https://egeria-project.org). The package is currently in
development. 

The first capabilities are around Egeria's platform services used to start and stop
the server platform and servers along with some basic configuration of Egeria servers.

"""

from importlib import resources
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from ._globals import is_debug, disable_ssl_warnings

if disable_ssl_warnings:
    from urllib3.exceptions import InsecureRequestWarning
    from urllib3 import disable_warnings
    disable_warnings(InsecureRequestWarning)

from ._exceptions import (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,
                          print_exception_response, )
from .utils import print_response
from ._client import Client
from .platform_services import Platform
from .core_omag_server_config import CoreServerConfig

__version__ = "0.1"