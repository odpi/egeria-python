"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Client to manage Egeria operations. Inherits methods from EgeriaConfig,
ServerOps, RuntimeManager and Platform.

"""
from examples.doc_samples.Create_Sustainability_Collection_Sample import token
from pyegeria._exceptions import (
    InvalidParameterException,
)
from pyegeria import (
    max_paging_size,
    body_slimmer,
    MyProfile,
    FeedbackManager,
    EgeriaCat,
    ValidMetadataManager,
    AutomatedCuration,
    ActionAuthor,
    ClassificationManager,
    RegisteredInfo,
    RuntimeManager,
    ServerOps,
    EgeriaConfig,
    Platform,
    EgeriaMy,
)


class EgeriaOps(RuntimeManager, EgeriaConfig, ServerOps, EgeriaMy):
    """
    Client for managing Egeria operations.

    Attributes:

        server_name: str
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
        server_name: str,
        platform_url: str,
        user_id: str,
        user_pwd: str = None,
        token: str = None,
    ):
        EgeriaConfig.__init__(self, server_name, platform_url, user_id, user_pwd)
        RuntimeManager.__init__(
            self, server_name, platform_url, user_id, user_pwd, token=token
        )
        ServerOps.__init__(self, server_name, platform_url, user_id, user_pwd)

        EgeriaMy.__init__(
            self, server_name, platform_url, user_id, user_pwd, token=token
        )
