"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This is the pyegeria client package. The purpose of the package is to provide
easy access to Egeria (https://egeria-project.org). The package is currently in
development. 

The first capabilities are around Egeria's platform services used to start and stop
the server platform and servers. 

"""


try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from ._globals import is_debug, disable_ssl_warnings, max_paging_size

if disable_ssl_warnings:
    from urllib3.exceptions import InsecureRequestWarning
    from urllib3 import disable_warnings
    disable_warnings(InsecureRequestWarning)

from ._exceptions import (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,
                          print_exception_response)
from .utils import print_response, body_slimmer, wrap_text
from ._client import Client
from .automated_curation_omvs import AutomatedCuration
from .core_omag_server_config import CoreServerConfig
from .platform_services import Platform
from .registered_info import RegisteredInfo
from .glossary_omvs import GlossaryBrowser
from ._validators import (validate_user_id, validate_name, validate_guid, validate_server_name, validate_search_string,
                          validate_url, is_json, validate_public)
# from .asset_catalog_omvs import AssetCatalog
from .gov_engine import GovEng
from .my_profile_omvs import MyProfile
from .full_omag_server_config import FullServerConfig
from .server_operations import ServerOps

__version__ = "0.3"
