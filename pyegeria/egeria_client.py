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



class Egeria(
    AssetCatalog,
    CollectionManager,
    EgeriaMy,
    GlossaryManager,
    # GovernanceAuthor,
    # PeopleOrganizer,
    ProjectManager,
    RuntimeManager,
    ServerOps,
    FullServerConfig,
    ActionAuthor,
    AutomatedCuration,
    ClassificationManager,
    RegisteredInfo,
    # TemplateManager,
    ValidMetadataManager,
    MetadataExplorer,
    SolutionArchitect,
):
    """
    Client to issue Runtime status requests.

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

    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: str = None,
        token: str = None,
    ):
        AssetCatalog.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        CollectionManager.__init__(
            self, view_server, platform_url, user_id, user_pwd, token
        )

        EgeriaMy.__init__(self, view_server, platform_url, user_id, user_pwd, token)

        GlossaryManager.__init__(
            self, view_server, platform_url, user_id, user_pwd, token
        )

        ProjectManager.__init__(
            self, view_server, platform_url, user_id, user_pwd, token
        )

        RuntimeManager.__init__(
            self, view_server, platform_url, user_id, user_pwd, token=token
        )
        ServerOps.__init__(self, view_server, platform_url, user_id, user_pwd)

        EgeriaConfig.__init__(self, view_server, platform_url, user_id, user_pwd)

        ActionAuthor.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        AutomatedCuration.__init__(
            self, view_server, platform_url, user_id, user_pwd, token
        )
        ClassificationManager.__init__(
            self, view_server, platform_url, user_id, user_pwd, token
        )
        RegisteredInfo.__init__(
            self, view_server, platform_url, user_id, user_pwd, token
        )
        ValidMetadataManager.__init__(
            self, view_server, platform_url, user_id, user_pwd, token
        )
        SolutionArchitect.__init__(
            self, view_server, platform_url, user_id, user_pwd, token
        )
