"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This is the pyegeria client package. The purpose of the package is to provide
easy access to Egeria (https://egeria-project.org). The package is currently in
development.

The first capabilities are around Egeria's platform services used to start and stop
the server platform and servers.

"""
from .config import load_app_config, get_app_config,pretty_print_config
from .logging_configuration import config_logging, init_logging
from ._globals import (default_time_out, disable_ssl_warnings, enable_ssl_check,
                       is_debug, max_paging_size, NO_ELEMENTS_FOUND, NO_ASSETS_FOUND, NO_SERVERS_FOUND,
                       NO_CATALOGS_FOUND, NO_GLOSSARIES_FOUND, NO_TERMS_FOUND, NO_CATEGORIES_FOUND, NO_ELEMENT_FOUND,
                       NO_PROJECTS_FOUND, DEBUG_LEVEL, NO_COLLECTION_FOUND, NO_GUID_RETURNED, COMMENT_TYPES,
                       TERM_STATUS
                       )



if disable_ssl_warnings:
    from urllib3 import disable_warnings
    from urllib3.exceptions import InsecureRequestWarning

    disable_warnings(InsecureRequestWarning)

# from ._client import Client
from ._server_client import ServerClient
from ._exceptions import (PyegeriaInvalidParameterException, PyegeriaAPIException, PyegeriaException,
                          PyegeriaUnauthorizedException, PyegeriaClientException, PyegeriaUnknownException,
                          PyegeriaConnectionException, PyegeriaNotFoundException,
                          print_exception_table, print_basic_exception, print_validation_error)
from .config import load_app_config, get_app_config, settings
from .logging_configuration import config_logging, console_log_filter, init_logging
# from ._exceptions import (PyegeriaInvalidParameterException, PyegeriaAPIException, PyegeriaUnauthorizedException,
#                           print_exception_response, )
from ._validators import (is_json, validate_guid, validate_name, validate_public, validate_search_string,
                          validate_server_name, validate_url, validate_user_id, )
from .asset_catalog import AssetCatalog
from .automated_curation import AutomatedCuration
from .classification_manager import ClassificationManager
from .collection_manager import CollectionManager
from .core_omag_server_config import CoreServerConfig
from .create_tech_guid_lists import build_global_guid_lists
from .egeria_cat_client import EgeriaCat
from .egeria_client import Egeria
from .egeria_config_client import EgeriaConfig

from .egeria_tech_client import EgeriaTech
# from .feedback_manager_omvs import FeedbackManager
from .full_omag_server_config import FullServerConfig
from .glossary_manager import GlossaryManager
from .governance_officer import GovernanceOfficer
from .mermaid_utilities import (construct_mermaid_web, construct_mermaid_jup,  load_mermaid,
                                parse_mermaid_code, render_mermaid, save_mermaid_graph, save_mermaid_html, )
from .metadata_explorer_omvs import MetadataExplorer
from .my_profile_omvs import MyProfile
from .platform_services import Platform
from .project_manager import ProjectManager
from .registered_info import RegisteredInfo
from .runtime_manager import RuntimeManager
from .server_operations import ServerOps
from .solution_architect import SolutionArchitect
from .utils import body_slimmer,to_pascal_case, to_camel_case, camel_to_title_case
from .valid_metadata import ValidMetadataManager
from .x_action_author_omvs import ActionAuthor
from .template_manager_omvs import TemplateManager
from .data_designer import DataDesigner
from .base_report_formats import select_report_spec
from .mcp_adapter import list_reports, describe_report, run_report, _async_run_report, _execute_egeria_call_blocking
from .base_report_formats import report_spec_list, select_report_spec, get_report_format_description
from .actor_manager import ActorManager
from .community_matters_omvs import CommunityMatters
#
# 2/12/25

def __getattr__(name):
    """
    Lazy attribute loader to avoid import-time circular dependencies while preserving API.
    Exposes:
    - process_markdown_file via commands.cat.dr_egeria_md
    - md_processing package
    - commands package
    """
    if name == "process_markdown_file":
        from commands.cat.dr_egeria_md import process_markdown_file as _pmf
        return _pmf
    if name == "md_processing":
        import md_processing as _mdp
        return _mdp
    if name == "commands":
        import commands as _cmd
        return _cmd
    raise AttributeError(f"module 'pyegeria' has no attribute {name!r}")

if __name__ == "__main__":
    print("Main-Init")
