"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This class is meant to be a client for catalog users and currently inherits from
AssetCatalog, CollectionManager, GlossaryManager, and ProjectManager.

"""

from pyegeria import (
    AssetCatalog,
    CollectionManager,
    EgeriaMy,
    GlossaryManager,
    ProjectManager,
)


class EgeriaCat(
    AssetCatalog,
    CollectionManager,
    EgeriaMy,
    GlossaryManager,
    # GovernanceAuthor,
    # PeopleOrganizer,
    ProjectManager,
):
    """
    Client to issue Runtime status requests.

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
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd

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


if __name__ == "__main__":
    print("Egeria Cat Client")
