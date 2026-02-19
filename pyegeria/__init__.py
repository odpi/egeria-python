"""
pyegeria: A Python SDK for ODPi Egeria.
"""
from pyegeria.core.config import load_app_config, get_app_config, pretty_print_config
from pyegeria.core.logging_configuration import config_logging, init_logging
from pyegeria.core._globals import (
    COMMENT_TYPES,
    DEBUG_LEVEL,
    default_time_out,
    disable_ssl_warnings,
    enable_ssl_check,
    is_debug,
    max_paging_size,
    MERMAID_GRAPH_TITLES,
    MERMAID_GRAPHS,
    NO_ASSETS_FOUND,
    NO_CATALOGS_FOUND,
    NO_CATEGORIES_FOUND,
    NO_COLLECTION_FOUND,
    NO_ELEMENT_FOUND,
    NO_ELEMENTS_FOUND,
    NO_GLOSSARIES_FOUND,
    NO_GUID_RETURNED,
    NO_MEMBERS_FOUND,
    NO_PROJECTS_FOUND,
    NO_SERVERS_FOUND,
    NO_TERMS_FOUND,
    TERM_STATUS,
    ACTIVITY_STATUS,
)

if disable_ssl_warnings:
    from urllib3 import disable_warnings
    from urllib3.exceptions import InsecureRequestWarning

    disable_warnings(InsecureRequestWarning)

from pyegeria.core._server_client import ServerClient
from pyegeria.core._exceptions import (
    PyegeriaException,
    PyegeriaAPIException,
    PyegeriaConnectionException,
    PyegeriaTimeoutException,
    PyegeriaNotFoundException,
    PyegeriaUnauthorizedException,
    PyegeriaInvalidParameterException,
    PyegeriaClientException,
    PyegeriaUnknownException,
    print_exception_table,
    print_basic_exception,
    print_validation_error,
)
from pyegeria.core.config import settings

from pyegeria.core.utils import body_slimmer
# OMVS Clients - Promoted to package level for ease of use
from pyegeria.omvs.action_author import ActionAuthor
from pyegeria.omvs.actor_manager import ActorManager
from pyegeria.omvs.asset_catalog import AssetCatalog
from pyegeria.omvs.asset_maker import AssetMaker
from pyegeria.omvs.automated_curation import AutomatedCuration
from pyegeria.omvs.classification_explorer import ClassificationExplorer
from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.omvs.community_matters_omvs import CommunityMatters
from pyegeria.omvs.data_designer import DataDesigner
from pyegeria.omvs.data_discovery import DataDiscovery
from pyegeria.omvs.data_engineer import DataEngineer
from pyegeria.omvs.digital_business import DigitalBusiness
from pyegeria.omvs.external_links import ExternalReferences
from pyegeria.omvs.feedback_manager import FeedbackManager
from pyegeria.omvs.full_omag_server_config import FullServerConfig
from pyegeria.omvs.glossary_manager import GlossaryManager
from pyegeria.omvs.governance_officer import GovernanceOfficer
from pyegeria.omvs.lineage_linker import LineageLinker
from pyegeria.omvs.location_arena import Location
from pyegeria.omvs.metadata_expert import MetadataExpert
from pyegeria.omvs.metadata_explorer_omvs import MetadataExplorer
from pyegeria.omvs.my_profile import MyProfile
from pyegeria.omvs.notification_manager import NotificationManager
from pyegeria.omvs.people_organizer import PeopleOrganizer
from pyegeria.omvs.product_manager import ProductManager
from pyegeria.omvs.project_manager import ProjectManager
from pyegeria.omvs.reference_data import ReferenceDataManager
from pyegeria.omvs.registered_info import RegisteredInfo
from pyegeria.omvs.runtime_manager import RuntimeManager
from pyegeria.omvs.schema_maker import SchemaMaker
from pyegeria.omvs.server_operations import ServerOps
from pyegeria.omvs.solution_architect import SolutionArchitect
from pyegeria.omvs.specification_properties import SpecificationProperties
from pyegeria.omvs.subject_area import SubjectArea
from pyegeria.omvs.template_manager_omvs import TemplateManager
from pyegeria.omvs.time_keeper import TimeKeeper
from pyegeria.omvs.valid_metadata import ValidMetadataManager
from pyegeria.omvs.valid_metadata_lists import ValidMetadataLists
from pyegeria.omvs.valid_type_lists import ValidTypeLists

# View Utilities
from pyegeria.view.mermaid_utilities import (
    construct_mermaid_web,
    construct_mermaid_jup,
    load_mermaid,
    render_mermaid,
    save_mermaid_html,
    save_mermaid_graph,
)
from pyegeria.view.output_formatter import (
    generate_output,
    resolve_output_formats,
    populate_common_columns,
)

# Combined Clients
from pyegeria.egeria_client import Egeria
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.egeria_config_client import EgeriaConfig
from pyegeria.egeria_cat_client import EgeriaCat

__all__ = [
    # Main Clients
    "Egeria",
    "EgeriaTech",
    "EgeriaConfig",
    "EgeriaCat",
    "ServerClient",
    # Exceptions
    "PyegeriaException",
    "PyegeriaAPIException",
    "PyegeriaConnectionException",
    "PyegeriaTimeoutException",
    "PyegeriaNotFoundException",
    "PyegeriaUnauthorizedException",
    "PyegeriaInvalidParameterException",
    "PyegeriaClientException",
    "PyegeriaUnknownException",
    "print_exception_table",
    # Globals & Constants
    "COMMENT_TYPES",
    "DEBUG_LEVEL",
    "default_time_out",
    "disable_ssl_warnings",
    "enable_ssl_check",
    "is_debug",
    "max_paging_size",
    "MERMAID_GRAPH_TITLES",
    "MERMAID_GRAPHS",
    "NO_ASSETS_FOUND",
    "NO_CATALOGS_FOUND",
    "NO_CATEGORIES_FOUND",
    "NO_COLLECTION_FOUND",
    "NO_ELEMENT_FOUND",
    "NO_ELEMENTS_FOUND",
    "NO_GLOSSARIES_FOUND",
    "NO_GUID_RETURNED",
    "NO_MEMBERS_FOUND",
    "NO_PROJECTS_FOUND",
    "NO_SERVERS_FOUND",
    "NO_TERMS_FOUND",
    "TERM_STATUS",
    "ACTIVITY_STATUS",
    # OMVS Module Clients
    "ActionAuthor",
    "ActorManager",
    "AssetCatalog",
    "AssetMaker",
    "AutomatedCuration",
    "ClassificationExplorer",
    "CollectionManager",
    "CommunityMatters",
    "DataDesigner",
    "DataDiscovery",
    "DataEngineer",
    "DigitalBusiness",
    "ExternalReferences",
    "FeedbackManager",
    "FullServerConfig",
    "GlossaryManager",
    "GovernanceOfficer",
    "LineageLinker",
    "Location",
    "MetadataExpert",
    "MetadataExplorer",
    "MyProfile",
    "NotificationManager",
    "PeopleOrganizer",
    "ProductManager",
    "ProjectManager",
    "ReferenceDataManager",
    "RegisteredInfo",
    "RuntimeManager",
    "SchemaMaker",
    "ServerOps",
    "SolutionArchitect",
    "SpecificationProperties",
    "SubjectArea",
    "TemplateManager",
    "TimeKeeper",
    "ValidMetadataManager",
    "ValidMetadataLists",
    "ValidTypeLists",
    # View Utilities
    "construct_mermaid_web",
    "construct_mermaid_jup",
    "load_mermaid",
    "render_mermaid",
    "save_mermaid_html",
    "save_mermaid_graph",
    "generate_output",
    "resolve_output_formats",
    "populate_common_columns",
    # Config Utilities
    "load_app_config",
    "get_app_config",
    "pretty_print_config",
    # Logging Utilities
    "config_logging",
    "init_logging",
]
