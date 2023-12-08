"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.
"""
"""
This is the pyegeria client package. The purpose of the package is to provide
easy access to Egeria (https://egeria-project.org). The package is currently in
development. 

The first capabilities are around Egeria's platform services used to start and stop
the server platform and servers. 

"""

from .config import is_debug, disable_ssl_warnings

if disable_ssl_warnings:
    from urllib3.exceptions import InsecureRequestWarning
    from urllib3 import disable_warnings
    disable_warnings(InsecureRequestWarning)


from .util_exp import (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,
                       print_exception_response, print_rest_response)
from .client import Client
from .platform_services import Platform

from pyegeria.util_exp import (
    InvalidParameterException,
    PropertyServerException,
    print_exception_response,
    print_rest_response,
)

from pyegeria.platform_services import Platform