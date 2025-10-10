"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This is the pyegeria client package. The purpose of the package is to provide
easy access to Egeria (https://egeria-project.org). The package is currently in
development.

The first capabilities are around Egeria's platform services used to start and stop
the server platform and servers.

"""

from pyegeria._globals import (default_time_out, disable_ssl_warnings, enable_ssl_check,
                       is_debug, max_paging_size, NO_ELEMENTS_FOUND, NO_ASSETS_FOUND, NO_SERVERS_FOUND,
                       NO_CATALOGS_FOUND, NO_GLOSSARIES_FOUND, NO_TERMS_FOUND, NO_CATEGORIES_FOUND, NO_ELEMENT_FOUND,
                       NO_PROJECTS_FOUND, DEBUG_LEVEL,)

if disable_ssl_warnings:
    from urllib3 import disable_warnings
    from urllib3.exceptions import InsecureRequestWarning

    disable_warnings(InsecureRequestWarning)

# Note: Avoid importing md_processing at package import time to keep pyegeria lightweight
# and to prevent test-time ImportErrors if md_processing optional symbols change.
# If you need md_processing commands, import md_processing directly in your application code.
# import md_processing  # intentionally not imported to avoid coupling
# from md_processing import (...)
# from md_processing.md_commands.data_designer_commands import (...)

from pyegeria._client import Client
from pyegeria._deprecated_gov_engine import GovEng
from pyegeria._exceptions import (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,
                          print_exception_response, )
from pyegeria._validators import (is_json, validate_guid, validate_name, validate_public, validate_search_string,
                          validate_server_name, validate_url, validate_user_id, )
from pyegeria.asset_catalog_omvs import AssetCatalog
from pyegeria.automated_curation import AutomatedCuration
from pyegeria.classification_manager_omvs import ClassificationManager
from pyegeria.collection_manager import CollectionManager
from pyegeria.core_omag_server_config import CoreServerConfig
from pyegeria.create_tech_guid_lists import build_global_guid_lists
from pyegeria.egeria_cat_client import EgeriaCat
# from .pyegeria.egeria_client import Egeria
from pyegeria.egeria_config_client import EgeriaConfig
from pyegeria.egeria_my_client import EgeriaMy
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.feedback_manager_omvs import FeedbackManager
from pyegeria.full_omag_server_config import FullServerConfig

from pyegeria.glossary_manager import GlossaryManager
from pyegeria.mermaid_utilities import (construct_mermaid_web, construct_mermaid_jup, load_mermaid,
                                parse_mermaid_code, render_mermaid, save_mermaid_graph, save_mermaid_html, )
from pyegeria.metadata_explorer_omvs import MetadataExplorer
from pyegeria.my_profile_omvs import MyProfile
from pyegeria.platform_services import Platform
from pyegeria.project_manager import ProjectManager
from pyegeria.registered_info import RegisteredInfo
from pyegeria.runtime_manager_omvs import RuntimeManager
from pyegeria.server_operations import ServerOps
from pyegeria.solution_architect import SolutionArchitect
from pyegeria.utils import body_slimmer
from pyegeria.valid_metadata_omvs import ValidMetadataManager
from pyegeria.x_action_author_omvs import ActionAuthor
from pyegeria.template_manager_omvs import TemplateManager



if __name__ == "__main__":
    print("Main-Init")
