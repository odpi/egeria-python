"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Runtime manager is a view service that supports user interaction with the running platforms.

"""
from pyegeria.automated_curation import AutomatedCuration
from pyegeria.classification_manager_omvs import ClassificationManager
from pyegeria.data_designer import DataDesigner
from pyegeria.egeria_cat_client import EgeriaCat
from pyegeria.metadata_explorer_omvs import MetadataExplorer
from pyegeria.registered_info import RegisteredInfo
from pyegeria.runtime_manager_omvs import RuntimeManager
from pyegeria.solution_architect import SolutionArchitect
from pyegeria.template_manager_omvs import TemplateManager
from pyegeria.valid_metadata_omvs import ValidMetadataManager
from pyegeria.governance_officer import GovernanceOfficer
from pyegeria.collection_manager import CollectionManager
from pyegeria.external_references import ExternalReferences
from pyegeria._globals import NO_ELEMENTS_FOUND

class EgeriaTech:
    """
    Client for technical Egeria users using composition.

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

        # Compose sub-clients
        self._auto_curate = AutomatedCuration(view_server, platform_url, user_id, user_pwd, token)
        self._cat = EgeriaCat(view_server, platform_url, user_id, user_pwd, token)
        self._class_mgr = ClassificationManager(view_server, platform_url, user_id, user_pwd, token)
        self._reg_info = RegisteredInfo(view_server, platform_url, user_id, user_pwd, token)
        self._runtime = RuntimeManager(view_server, platform_url, user_id, user_pwd, token)
        self._valid = ValidMetadataManager(view_server, platform_url, user_id, user_pwd, token)
        self._explorer = MetadataExplorer(view_server, platform_url, user_id, user_pwd, token)
        self._sol_arch = SolutionArchitect(view_server, platform_url, user_id, user_pwd, token)
        self._designer = DataDesigner(view_server, platform_url, user_id, user_pwd, token)
        self._templates = TemplateManager(view_server, platform_url, user_id, user_pwd, token)
        self._gov_officer = GovernanceOfficer(view_server, platform_url, user_id, user_pwd, token)
        self._collections = CollectionManager(view_server, platform_url, user_id, user_pwd, token)
        self._external_references = ExternalReferences(view_server, platform_url, user_id, user_pwd, token)

        self._subclients = [
            self._auto_curate,
            self._cat,
            self._class_mgr,
            self._reg_info,
            self._runtime,
            self._valid,
            self._explorer,
            self._sol_arch,
            self._designer,
            self._templates,
            self._gov_officer,
            self._collections,
            self._external_references,
        ]
        self.NO_ELEMENTS_FOUND = NO_ELEMENTS_FOUND

    def __getattr__(self, name):
        for sub in self._subclients:
            if hasattr(sub, name):
                return getattr(sub, name)
        raise AttributeError(f"{self.__class__.__name__!s} object has no attribute {name!r}")

    def create_egeria_bearer_token(self, user_id: str = None, user_pwd: str = None):
        token_val = None
        for sub in self._subclients:
            token_val = sub.create_egeria_bearer_token(user_id, user_pwd)
        return token_val

    def set_bearer_token(self, token: str) -> None:
        for sub in self._subclients:
            sub.set_bearer_token(token)

    def get_token(self) -> str:
        for sub in self._subclients:
            if hasattr(sub, "get_token"):
                return sub.get_token()
        return None

    def close_session(self) -> None:
        for sub in self._subclients:
            if hasattr(sub, "close_session"):
                try:
                    sub.close_session()
                except Exception:
                    pass

if __name__ == "__main__":
    print("Main-Tech Client")
