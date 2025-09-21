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
# from pyegeria.x_action_author_omvs import ActionAuthor
from pyegeria.asset_catalog_omvs import AssetCatalog
# from pyegeria.collection_manager import CollectionManager
from pyegeria.glossary_manager import GlossaryManager
from pyegeria.project_manager import ProjectManager
from pyegeria.automated_curation import AutomatedCuration
from pyegeria.classification_manager_omvs import ClassificationManager
from pyegeria.template_manager_omvs import TemplateManager
from pyegeria.runtime_manager_omvs import RuntimeManager
from pyegeria.full_omag_server_config import FullServerConfig
from pyegeria.metadata_explorer_omvs import MetadataExplorer
from pyegeria.my_profile_omvs import MyProfile
from pyegeria.feedback_manager_omvs import FeedbackManager
from pyegeria.solution_architect import SolutionArchitect
from pyegeria.server_operations import ServerOps
from pyegeria.registered_info import RegisteredInfo
from pyegeria.valid_metadata_omvs import ValidMetadataManager
from pyegeria.egeria_config_client import EgeriaConfig
from pyegeria.data_designer import DataDesigner
from pyegeria.governance_officer import GovernanceOfficer
# from pyegeria.md_processing_utils import render_markdown


class Egeria:
    """
    Overall Egeria client that composes all functional pyegeria clients and delegates calls to them.

    Attributes:
        view_server: str
            Name of the view server to use.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None
        token: str
            An optional bearer token

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
        # Compose major umbrella and service clients
        self._asset_catalog = AssetCatalog(view_server, platform_url, user_id, user_pwd, token)
        self._my_profile = MyProfile(view_server, platform_url, user_id, user_pwd, token)
        self._feedback = FeedbackManager(view_server, platform_url, user_id, user_pwd, token)
        self._glossary = GlossaryManager(view_server, platform_url, user_id, user_pwd, token)
        self._projects = ProjectManager(view_server, platform_url, user_id, user_pwd, token)
        self._runtime = RuntimeManager(view_server, platform_url, user_id, user_pwd, token)
        self._server_ops = ServerOps(view_server, platform_url, user_id, user_pwd)
        self._full_server_config = FullServerConfig(view_server, platform_url, user_id, user_pwd)
        self._auto_curate = AutomatedCuration(view_server, platform_url, user_id, user_pwd, token)
        self._class_mgr = ClassificationManager(view_server, platform_url, user_id, user_pwd, token)
        self._reg_info = RegisteredInfo(view_server, platform_url, user_id, user_pwd, token)
        self._templates = TemplateManager(view_server, platform_url, user_id, user_pwd, token)
        self._valid = ValidMetadataManager(view_server, platform_url, user_id, user_pwd, token)
        self._explorer = MetadataExplorer(view_server, platform_url, user_id, user_pwd, token)
        self._sol_arch = SolutionArchitect(view_server, platform_url, user_id, user_pwd, token)
        self._config = EgeriaConfig(view_server, platform_url, user_id, user_pwd)
        self._designer = DataDesigner(view_server, platform_url, user_id, user_pwd, token)
        self._gov_officer = GovernanceOfficer(view_server, platform_url, user_id, user_pwd, token)

        self._subclients = [
            self._asset_catalog,
            self._my_profile,
            self._feedback,
            self._glossary,
            self._projects,
            self._runtime,
            self._server_ops,
            self._full_server_config,
            self._auto_curate,
            self._class_mgr,
            self._reg_info,
            self._templates,
            self._valid,
            self._explorer,
            self._sol_arch,
            self._config,
            self._designer,
            self._gov_officer,
        ]

    def __getattr__(self, name):
        for sub in self._subclients:
            if hasattr(sub, name):
                return getattr(sub, name)
        raise AttributeError(f"{self.__class__.__name__!s} object has no attribute {name!r}")

    def create_egeria_bearer_token(self, user_id: str = None, user_pwd: str = None):
        token_val = None
        for sub in self._subclients:
            if hasattr(sub, "create_egeria_bearer_token"):
                token_val = sub.create_egeria_bearer_token(user_id, user_pwd)
        return token_val

    def set_bearer_token(self, token: str) -> None:
        for sub in self._subclients:
            if hasattr(sub, "set_bearer_token"):
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
