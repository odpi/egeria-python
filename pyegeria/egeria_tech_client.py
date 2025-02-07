"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Runtime manager is a view service that supports user interaction with the running platforms.

"""
from pyegeria.x_action_author_omvs import ActionAuthor
from pyegeria.asset_catalog_omvs import AssetCatalog
from pyegeria.collection_manager_omvs import CollectionManager
from pyegeria.glossary_manager_omvs import GlossaryManager
from pyegeria.project_manager_omvs import ProjectManager
from pyegeria.automated_curation_omvs import AutomatedCuration
from pyegeria.classification_manager_omvs import ClassificationManager
from pyegeria.template_manager_omvs import TemplateManager
from pyegeria.runtime_manager_omvs import RuntimeManager
from pyegeria.full_omag_server_config import FullServerConfig
from pyegeria.metadata_explorer_omvs import MetadataExplorer
from pyegeria.egeria_my_client import EgeriaMy
from pyegeria.solution_architect_omvs import SolutionArchitect
from pyegeria.server_operations import ServerOps
from pyegeria.registered_info import RegisteredInfo
from pyegeria.valid_metadata_omvs import ValidMetadataManager
from pyegeria.egeria_cat_client import EgeriaCat
from pyegeria.metadata_explorer_omvs import MetadataExplorer
from pyegeria.feedback_manager_omvs import FeedbackManager
from pyegeria.my_profile_omvs import MyProfile
from pyegeria.solution_architect_omvs import SolutionArchitect
from pyegeria.my_profile_omvs import MyProfile
from pyegeria.utils import body_slimmer
from pyegeria import (
    INTEGRATION_GUIDS,
    TEMPLATE_GUIDS,  # ActionAuthor,
    max_paging_size,
)
from pyegeria._exceptions import InvalidParameterException


class EgeriaTech(
    # ActionAuthor,
    AutomatedCuration,
    EgeriaCat,
    ClassificationManager,
    RegisteredInfo,
    RuntimeManager,
    ValidMetadataManager,
    MetadataExplorer,
    SolutionArchitect,
):
    """
    Client for technical Egeria users.

    Attributes:

        view_server: str
                Name of the server to use.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None
        token: str, optional
            Bearer token

    Methods:
        Inherits methods from EgeriaCat, ActionAuthor, AutomatedCuration,
        ClassificationManager, RegisteredInfo, ValidMetadataManager
    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: str = None,
        token: str = None,
    ):
        # ActionAuthor.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        AutomatedCuration.__init__(
            self, view_server, platform_url, user_id, user_pwd, token
        )
        EgeriaCat.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        ClassificationManager.__init__(
            self, view_server, platform_url, user_id, user_pwd, token
        )
        RegisteredInfo.__init__(
            self, view_server, platform_url, user_id, user_pwd, token
        )
        RuntimeManager.__init__(
            self, view_server, platform_url, user_id, user_pwd, token
        )
        ValidMetadataManager.__init__(
            self, view_server, platform_url, user_id, user_pwd, token
        )
        MetadataExplorer.__init__(
            self, view_server, platform_url, user_id, user_pwd, token
        )
        SolutionArchitect.__init__(
            self, view_server, platform_url, user_id, user_pwd, token
        )


if __name__ == "__main__":
    print("Main-Tech Client")
