"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This class is the overall Egeria Client covering all of the functional pyegeria classes. May not be appropriate
for all use cases..using the more role based clients is often appropriate:
    * EgeriaCat - for catalog users
    * EgeriaConfig - for configuring the Egeria platform and servers
    * EgeriaMy - for personal actions
    * EgeriaOps - for operations and administration
    * EgeriaTech - for technical users such as data scientists and engineers

"""
from typing import Optional, Dict, Any

from pyegeria.egeria_config_client import EgeriaConfig
from pyegeria.omvs.action_author import ActionAuthor
from pyegeria.omvs.actor_manager import ActorManager
from pyegeria.omvs.asset_catalog import AssetCatalog
from pyegeria.omvs.asset_maker import AssetMaker
from pyegeria.omvs.automated_curation import AutomatedCuration
from pyegeria.omvs.classification_manager import ClassificationManager
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


class Egeria:
    """
    Overall Egeria client that composes all functional pyegeria clients using lazy loading.
    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: str = None,
        token: str = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.token = token

        self._subclient_map = {
            "action_author": ActionAuthor,
            "actor_manager": ActorManager,
            "asset_catalog": AssetCatalog,
            "asset_maker": AssetMaker,
            "auto_curate": AutomatedCuration,
            "class_mgr": ClassificationManager,
            "collections": CollectionManager,
            "community": CommunityMatters,
            "config": EgeriaConfig,
            "data_discovery": DataDiscovery,
            "data_engineer": DataEngineer,
            "designer": DataDesigner,
            "digital_business": DigitalBusiness,
            "expert": MetadataExpert,
            "explorer": MetadataExplorer,
            "external_refs": ExternalReferences,
            "feedback": FeedbackManager,
            "full_server_config": FullServerConfig,
            "glossary": GlossaryManager,
            "gov_officer": GovernanceOfficer,
            "lineage_linker": LineageLinker,
            "location": Location,
            "my_profile": MyProfile,
            "notifications": NotificationManager,
            "people_organizer": PeopleOrganizer,
            "product_manager": ProductManager,
            "projects": ProjectManager,
            "reference_data": ReferenceDataManager,
            "reg_info": RegisteredInfo,
            "runtime": RuntimeManager,
            "schema_maker": SchemaMaker,
            "server_ops": ServerOps,
            "sol_arch": SolutionArchitect,
            "specification_properties": SpecificationProperties,
            "subject_area": SubjectArea,
            "templates": TemplateManager,
            "time_keeper": TimeKeeper,
            "valid": ValidMetadataManager,
            "valid_metadata_lists": ValidMetadataLists,
            "valid_type_lists": ValidTypeLists,
        }
        self._instantiated_clients = {}

    def _get_subclient(self, attr_name: str):
        if attr_name not in self._instantiated_clients:
            client_cls = self._subclient_map[attr_name]
            self._instantiated_clients[attr_name] = client_cls(
                self.view_server, self.platform_url, self.user_id, self.user_pwd, self.token
            )
        return self._instantiated_clients[attr_name]

    def __getattr__(self, name):
        """Resolves attributes via instantiated or mapped subclients"""
        # Allow direct access to sub-clients if the name matches a key in the map
        if name in self._subclient_map:
            return self._get_subclient(name)

        for inst in self._instantiated_clients.values():
            if hasattr(inst, name):
                return getattr(inst, name)
        for attr_name, client_cls in self._subclient_map.items():
            if hasattr(client_cls, name):
                return getattr(self._get_subclient(attr_name), name)
        raise AttributeError(f"{self.__class__.__name__} object has no attribute {name}")

    def create_egeria_bearer_token(self, user_id: str = None, user_pwd: str = None):
        # Use server_ops as a reliable helper for token generation
        helper = self._get_subclient("server_ops")
        token_val = helper.create_egeria_bearer_token(user_id, user_pwd)
        self.set_bearer_token(token_val)
        return token_val

    def set_bearer_token(self, token: str) -> None:
        self.token = token
        for sub in self._instantiated_clients.values():
            sub.set_bearer_token(token)

    def get_token(self) -> str:
        if self.token: return self.token
        for sub in self._instantiated_clients.values():
            if hasattr(sub, "get_token"):
                return sub.get_token()
        return None

    def close_session(self) -> None:
        for sub in self._instantiated_clients.values():
            if hasattr(sub, "close_session"):
                try: sub.close_session()
                except Exception: pass
        self._instantiated_clients.clear()