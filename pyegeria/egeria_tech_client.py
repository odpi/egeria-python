"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Runtime manager is a view service that supports user interaction with the running platforms.

"""

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
    # ActionAuthor,
    ClassificationManager,
    RegisteredInfo,
    RuntimeManager,
    TEMPLATE_GUIDS,
    INTEGRATION_GUIDS,
)


class EgeriaTech(
    # ActionAuthor,
    AutomatedCuration,
    EgeriaCat,
    ClassificationManager,
    RegisteredInfo,
    RuntimeManager,
    ValidMetadataManager,
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


if __name__ == "__main__":
    print("Main-Tech Client")
