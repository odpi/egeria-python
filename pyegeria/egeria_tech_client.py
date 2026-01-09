"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

The Tech Client is a facade that provides a unified interface to the most 
commonly used technical OMVS modules.
"""
from pyegeria.omvs.automated_curation import AutomatedCuration
from pyegeria.omvs.classification_manager import ClassificationManager
from pyegeria.omvs.data_designer import DataDesigner
from pyegeria.omvs.metadata_explorer_omvs import MetadataExplorer
from pyegeria.omvs.metadata_expert import MetadataExpert
from pyegeria.omvs.registered_info import RegisteredInfo
from pyegeria.omvs.runtime_manager import RuntimeManager
from pyegeria.omvs.solution_architect import SolutionArchitect
from pyegeria.omvs.template_manager_omvs import TemplateManager
from pyegeria.omvs.valid_metadata import ValidMetadataManager
from pyegeria.omvs.governance_officer import GovernanceOfficer
from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.omvs.external_links import ExternalReferences
from pyegeria.omvs.actor_manager import ActorManager
from pyegeria.omvs.time_keeper import TimeKeeper
from pyegeria.omvs.product_manager import ProductManager
from pyegeria.omvs.location_arena import Location
from pyegeria.omvs.data_discovery import DataDiscovery
from pyegeria.omvs.data_engineer import DataEngineer
from pyegeria.omvs.digital_business import DigitalBusiness
from pyegeria.omvs.lineage_linker import LineageLinker
from pyegeria.omvs.schema_maker import SchemaMaker
from pyegeria.omvs.valid_type_lists import ValidTypeLists
from pyegeria.omvs.valid_metadata_lists import ValidMetadataLists
from pyegeria.omvs.action_author import ActionAuthor
from pyegeria.core._globals import NO_ELEMENTS_FOUND

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

        # Mapping of attribute names to their classes for lazy loading
        self._subclient_map = {
            "auto_curate": AutomatedCuration,
            "class_mgr": ClassificationManager,
            "reg_info": RegisteredInfo,
            "runtime": RuntimeManager,
            "valid": ValidMetadataManager,
            "explorer": MetadataExplorer,
            "expert": MetadataExpert,
            "sol_arch": SolutionArchitect,
            "designer": DataDesigner,
            "templates": TemplateManager,
            "gov_officer": GovernanceOfficer,
            "collections": CollectionManager,
            "external_references": ExternalReferences,
            "actor_manager": ActorManager,
            "time_keeper": TimeKeeper,
            "product_manager": ProductManager,
            "location_arena": Location,
            "data_discovery": DataDiscovery,
            "data_engineer": DataEngineer,
            "digital_business": DigitalBusiness,
            "lineage_linker": LineageLinker,
            "schema_maker": SchemaMaker,
            "valid_types": ValidTypeLists,
            "valid_metadata_lists": ValidMetadataLists,
            "action_author": ActionAuthor,
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

    def create_egeria_bearer_token(self, user_id: str = None, user_pwd: str = None):
        """Create token and synchronize it across all instantiated sub-clients."""
        # Use a reliable sub-client to generate the token (e.g., collections)
        helper = self._get_subclient("collections")
        token_val = helper.create_egeria_bearer_token(user_id, user_pwd)
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
        return None

    def close_session(self) -> None:
        """Close sessions for all sub-clients that were instantiated."""
        for sub in self._instantiated_clients.values():
            if hasattr(sub, "close_session"):
                try:
                    sub.close_session()
                except Exception:
                    pass
        self._instantiated_clients.clear()


if __name__ == "__main__":
    print("Main-Tech Client")
