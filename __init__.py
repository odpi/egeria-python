"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This is the pyegeria client package. The purpose of the package is to provide
easy access to Egeria (https://egeria-project.org). The package is currently in
development.

The first capabilities are around Egeria's platform services used to start and stop
the server platform and servers.

"""

from pyegeria.core._globals import (disable_ssl_warnings, )

if disable_ssl_warnings:
    from urllib3 import disable_warnings
    from urllib3.exceptions import InsecureRequestWarning
    disable_warnings(InsecureRequestWarning)

# from .pyegeria.egeria_client import Egeria
# from pyegeria.egeria_my_client import EgeriaMy


if __name__ == "__main__":
    print("Main-Init")
