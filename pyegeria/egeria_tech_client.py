"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

The Tech Client is a facade that provides a unified interface to the most 
commonly used technical OMVS modules.
"""
from pyegeria.omvs.action_author import ActionAuthor
from pyegeria.omvs.actor_manager import ActorManager
from pyegeria.omvs.asset_catalog import AssetCatalog
from pyegeria.omvs.asset_maker import AssetMaker
from pyegeria.omvs.automated_curation import AutomatedCuration
from pyegeria.omvs.classification_explorer import ClassificationExplorer
from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.omvs.community_matters_omvs import CommunityMatters
from pyegeria.omvs.connection_maker import ConnectionMaker
from pyegeria.omvs.data_designer import DataDesigner
from pyegeria.omvs.data_discovery import DataDiscovery
from pyegeria.omvs.data_engineer import DataEngineer
from pyegeria.omvs.digital_business import DigitalBusiness
from pyegeria.omvs.external_links import ExternalReferences
from pyegeria.core._server_client import ServerClient
from pyegeria.omvs.glossary_manager import GlossaryManager
from pyegeria.omvs.governance_officer import GovernanceOfficer
from pyegeria.omvs.lineage_linker import LineageLinker
from pyegeria.omvs.location_arena import LocationArena
from pyegeria.omvs.metadata_expert import MetadataExpert
from pyegeria.omvs.my_profile import MyProfile
from pyegeria.omvs.notification_manager import NotificationManager
from pyegeria.omvs.people_organizer import PeopleOrganizer
from pyegeria.omvs.product_manager import ProductManager
from pyegeria.omvs.project_manager import ProjectManager
from pyegeria.omvs.reference_data import ReferenceDataManager
from pyegeria.omvs.registered_info import RegisteredInfo
from pyegeria.omvs.runtime_manager import RuntimeManager
from pyegeria.omvs.schema_maker import SchemaMaker
from pyegeria.omvs.security_officer import SecurityOfficer
from pyegeria.omvs.solution_architect import SolutionArchitect
from pyegeria.omvs.specification_properties import SpecificationProperties
from pyegeria.omvs.subject_area import SubjectArea
from pyegeria.omvs.template_manager_omvs import TemplateManager
from pyegeria.omvs.time_keeper import TimeKeeper
from pyegeria.omvs.valid_metadata import ValidMetadataManager
from pyegeria.omvs.valid_metadata_lists import ValidMetadataLists
from pyegeria.omvs.valid_type_lists import ValidTypeLists
from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.core.config import settings

class EgeriaTech:
    """
    Client for technical Egeria users using lazy-loading composition.

    Attributes:
        view_server: str
            Name of the view server to use.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method.
        user_pwd: str
            The password associated with the user_id. Defaults to None
        token: str, optional
            Bearer token

    Methods:
        Methods are provided by composed sub-clients via delegation.
    """

    def __init__(
        self,
        view_server: str = None,
        platform_url: str = None,
        user_id: str = None,
        user_pwd: str = None,
        token: str = None,
    ):
        self.view_server = view_server or settings.Environment.egeria_view_server
        self.platform_url = platform_url or settings.Environment.egeria_platform_url
        self.user_id = user_id or settings.User_Profile.user_name
        self.user_pwd = user_pwd or settings.User_Profile.user_pwd
        self.token = token

        # Mapping of attribute names to their classes for lazy loading
        self._subclient_map = {
            "auto_curate": AutomatedCuration,
            "automated_curation": AutomatedCuration,
            "class_mgr": ClassificationExplorer,
            "classification_manager": ClassificationExplorer,
            "reg_info": RegisteredInfo,
            "registered_info": RegisteredInfo,
            "runtime": RuntimeManager,
            "runtime_manager": RuntimeManager,
            "valid": ValidMetadataManager,
            "valid_metadata": ValidMetadataManager,
            "expert": MetadataExpert,
            "metadata_expert": MetadataExpert,
            "sol_arch": SolutionArchitect,
            "solution_architect": SolutionArchitect,
            "designer": DataDesigner,
            "data_designer": DataDesigner,
            "glossary": GlossaryManager,
            "glossary_manager": GlossaryManager,
            "templates": TemplateManager,
            "template_manager": TemplateManager,
            "gov_officer": GovernanceOfficer,
            "governance_officer": GovernanceOfficer,
            "collections": CollectionManager,
            "collection_manager": CollectionManager,
            "external_references": ExternalReferences,
            "external_refs": ExternalReferences,
            "actor_manager": ActorManager,
            "connection_maker": ConnectionMaker,
            "time_keeper": TimeKeeper,
            "product_manager": ProductManager,
            "location_arena": LocationArena,
            "data_discovery": DataDiscovery,
            "data_engineer": DataEngineer,
            "security_officer": SecurityOfficer,
            "digital_business": DigitalBusiness,
            "lineage_linker": LineageLinker,
            "schema_maker": SchemaMaker,
            "valid_types": ValidTypeLists,
            "valid_type_lists": ValidTypeLists,
            "valid_metadata_lists": ValidMetadataLists,
            "action_author": ActionAuthor,
            "asset_catalog": AssetCatalog,
            "asset_maker": AssetMaker,
            "community": CommunityMatters,
            "community_matters": CommunityMatters,
            "feedback": ServerClient,
            "feedback_manager": ServerClient,
            "my_profile": MyProfile,
            "notifications": NotificationManager,
            "notification_manager": NotificationManager,
            "people_organizer": PeopleOrganizer,
            "projects": ProjectManager,
            "project_manager": ProjectManager,
            "reference_data": ReferenceDataManager,
            "specification_properties": SpecificationProperties,
            "subject_area": SubjectArea,
            "subject_area_manager": SubjectArea,
        }
        self._instantiated_clients = {}
        self.NO_ELEMENTS_FOUND = NO_ELEMENTS_FOUND

    def _get_subclient(self, attr_name: str):
        """Lazy-load and cache sub-clients."""
        if attr_name not in self._instantiated_clients:
            client_cls = self._subclient_map[attr_name]
            self._instantiated_clients[attr_name] = client_cls(
                self.view_server,
                self.platform_url,
                self.user_id,
                self.user_pwd,
                self.token,
            )
        return self._instantiated_clients[attr_name]

    def __getattr__(self, name):
        """Delegate method calls to sub-clients, instantiating them on-demand."""
        # Allow direct access to sub-clients if the name matches a key in the map
        if name in self._subclient_map:
            return self._get_subclient(name)

        # Check already instantiated clients first for speed
        for inst in self._instantiated_clients.values():
            if hasattr(inst, name):
                return getattr(inst, name)

        # Look through the map for a class that provides this method
        for attr_name, client_cls in self._subclient_map.items():
            if hasattr(client_cls, name):
                client = self._get_subclient(attr_name)
                return getattr(client, name)

        raise AttributeError(
            f"{self.__class__.__name__!s} object has no attribute {name!r}"
        )

    async def _async_create_egeria_bearer_token(
            self, user_id: str = None, password: str = None, new_password: str = None
    ) -> str:
        """Create token and synchronize it across all instantiated sub-clients (Async)."""
        # Use a reliable sub-client to generate the token (e.g., collections)
        helper = self._get_subclient("collections")
        token_val = await helper._async_create_egeria_bearer_token(user_id, password, new_password)
        self.set_bearer_token(token_val)
        return token_val

    def create_egeria_bearer_token(self, user_id: str = None, password: str = None, new_password: str = None) -> str:
        """Create token and synchronize it across all instantiated sub-clients."""
        # Use a reliable sub-client to generate the token (e.g., collections)
        helper = self._get_subclient("collections")
        token_val = helper.create_egeria_bearer_token(user_id, password, new_password)
        self.set_bearer_token(token_val)
        return token_val

    def set_bearer_token(self, token: str) -> None:
        """Update token for the tech client and all active sub-clients."""
        self.token = token
        for sub in self._instantiated_clients.values():
            sub.set_bearer_token(token)

    def get_token(self) -> str:
        """Retrieve the current token from state or an active sub-client."""
        if self.token:
            return self.token
        for sub in self._instantiated_clients.values():
            if hasattr(sub, "get_token"):
                return sub.get_token()
        return self.token

    def close_session(self) -> None:
        """Close sessions for all sub-clients that were instantiated."""
        for sub in self._instantiated_clients.values():
            if hasattr(sub, "close_session"):
                try:
                    sub.close_session()
                except Exception:
                    pass
        self._instantiated_clients.clear()

    def get_report_spec_schema(self, report_spec_name: str, **kwargs) -> list:
        """
        Executes a report spec's action to dynamically discover all available attributes
        and their data types, returning a list of dictionaries suitable for reporting.
        """
        from pyegeria.view.base_report_formats import report_specs
        from pyegeria.view.output_formatter import materialize_egeria_summary
        from pyegeria.core.utils import discover_element_schema
        import logging

        logger = logging.getLogger(__name__)

        spec = report_specs.get(report_spec_name)
        if not spec or not getattr(spec, "action", None):
            return [{"attribute_path": "Error", "data_type": f"Report spec '{report_spec_name}' not found or has no action."}]

        exclude_sys = kwargs.pop("exclude_system_properties", True)

        # Merge kwargs with spec_params if they exist
        action_params = spec.action.spec_params.copy() if spec.action.spec_params else {}
        action_params.update(kwargs)
        
        # Force output format to JSON to bypass filtering and get raw attributes
        action_params["output_format"] = "JSON"

        func_name = spec.action.function
        if "." in func_name:
            # E.g., 'GovernanceOfficer.find_governance_definitions' -> method_name
            _, method_name = func_name.split(".", 1)
        else:
            method_name = func_name

        try:
            # Retrieve the function dynamically from self (the TechClient facade)
            func = getattr(self, method_name)
            results = func(**action_params)
        except Exception as e:
            logger.error(f"Failed to execute action {method_name} for schema discovery: {e}")
            return [{"attribute_path": "Error", "data_type": f"Execution failed: {str(e)}"}]

        if not results or isinstance(results, str):
            return [{"attribute_path": "Info", "data_type": "No elements found by this action."}]
        
        # Take the first element
        first_el = results[0] if isinstance(results, list) else results

        # Flatten and extract using the standard engine
        materialized = materialize_egeria_summary(first_el)
        schema = discover_element_schema(materialized, exclude_system_properties=exclude_sys)

        # Format as table rows
        schema_list = [{"attribute_path": path, "data_type": dtype} for path, dtype in schema.items()]
        return schema_list


if __name__ == "__main__":
    print("Main-Tech Client")
